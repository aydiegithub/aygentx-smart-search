import json
import uuid
from typing import List, Dict, Any
from app.llm.factory import LLMFactory
from app.llm.base import ChatMessage
from app.core.logging import Logger
from app.constants import RAG_INNGESTION_PROMPT, GEMINI_PROVIDER, RAG_REASONING_MODEL
from app.db.connection import D1Connection

logging = Logger()


class RagService:
    def __init__(self):
        self.db = D1Connection()
        self.inngestion_prompt = RAG_INNGESTION_PROMPT

    async def process_update(self, content: str, update_mode: str, model_name: str) -> dict:
        """Handles replace, merge, and clear operations for the knowledge base."""

        # 1. CLEAR MODE
        if update_mode == "clear":
            logging.info("Clearing knowledge base...")
            self.db.query("DELETE FROM rag_nodes", [])
            self.db.query("DELETE FROM rag_raw_documents", [])
            return {"model_used": "none", "total_branches_created": 0, "total_leaf_nodes_created": 0}

        text_to_process = content

        # 2. MERGE MODE
        if update_mode == "merge":
            logging.info("Fetching existing raw documents for merge...")
            existing_docs = self.db.query(
                "SELECT content FROM rag_raw_documents", [])

            old_text = ""
            if isinstance(existing_docs, dict) and existing_docs.get("data"):
                old_text = "\n\n".join([doc["content"]
                                       for doc in existing_docs['data']])

            text_to_process = old_text + "\n\n" + content

            # Wipe only the old tree, we will rebuild it
            self.db.query("DELETE FROM rag_nodes", [])

            # Save the newly added text as a new raw document
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            self.db.query("INSERT INTO rag_raw_documents (id, content) VALUES (?, ?)", [
                          doc_id, content])

        # 3. REPLACE MODE
        if update_mode == "replace":
            logging.info("Replacing knowledge base...")
            # Wipe everything
            self.db.query("DELETE FROM rag_nodes", [])
            self.db.query("DELETE FROM rag_raw_documents", [])

            # Save the new text as the only raw document
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            self.db.query("INSERT INTO rag_raw_documents (id, content) VALUES (?, ?)", [
                          doc_id, content])

        # 4. REASONING & TREE GENERATION
        # Use the provided model, or fallback to the default RAG reasoning model
        actual_model = model_name if model_name else RAG_REASONING_MODEL
        logging.info(
            f"Passing {len(text_to_process)} chars to {actual_model} for tree generation...")

        llm = LLMFactory.create(provider=GEMINI_PROVIDER, model=actual_model)

        prompt = self.inngestion_prompt.format(raw_text=text_to_process)

        result = llm.generate_json([
            ChatMessage(role="user", content=prompt)
        ])

        # The result should be a list of root nodes. Handle it safely if the LLM wraps it in a dict.
        tree_data = result if isinstance(
            result, list) else result.get("tree", [])
        if not tree_data and isinstance(result, dict):
            # Fallback if the LLM wrapped the array in a different key name
            for v in result.values():
                if isinstance(v, list):
                    tree_data = v
                    break

        # 5. INSERT TREE INTO DATABASE
        branches_count = 0
        leaves_count = 0

        # Recursive function to insert nodes and their children
        def insert_node(node: dict, parent_id: str = None):
            nonlocal branches_count, leaves_count

            node_id = node.get("id", f"node_{uuid.uuid4().hex[:8]}")
            title = node.get("title", "Untitled")
            node_content = node.get("content")

            if node_content:
                leaves_count += 1
            else:
                branches_count += 1

            # Insert this specific node
            self.db.query(
                "INSERT INTO rag_nodes (id, parent_id, title, content) VALUES (?, ?, ?, ?)",
                [node_id, parent_id, title, node_content]
            )

            # Recursively process and insert all children
            for child in node.get("children", []):
                insert_node(child, node_id)

        # Kick off the recursive insertion
        for root_node in tree_data:
            insert_node(root_node, None)

        logging.info(
            f"Tree generation complete. Branches: {branches_count}, Leaves: {leaves_count}")

        return {
            "model_used": actual_model,
            "total_branches_created": branches_count,
            "total_leaf_nodes_created": leaves_count
        }

    def get_indices(self) -> dict:
        """Fetches all nodes and reconstructs the hierarchical tree."""
        response = self.db.query("SELECT * FROM rag_nodes", [])
        nodes = response.get("data", []) if isinstance(response, dict) else []

        # Build the tree in memory
        node_map = {node["id"]: {**node, "children": []} for node in nodes}
        tree = []

        for node in nodes:
            parent_id = node.get("parent_id")
            if parent_id and parent_id in node_map:
                node_map[parent_id]["children"].append(node_map[node["id"]])
            else:
                tree.append(node_map[node["id"]])

        return {"total_nodes": len(nodes), "tree": tree}

    def get_raw_documents(self) -> List[dict]:
        """Fetches all raw documents for backup/download."""
        response = self.db.query("SELECT * FROM rag_raw_documents", [])
        return response.get("data", []) if isinstance(response, dict) else []
