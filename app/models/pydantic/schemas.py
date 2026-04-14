from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Dict, Any, List, Optional, Literal
from app.core.logging import Logger
from app.core.logging import Logger
from app.constants import RAG_REASONING_MODEL

logger = Logger(__name__)

logging = Logger()

ALLOWED_MODELS = ["gemini-3.1-flash-lite-preview", "gpt-4o-mini"]


class QueryRequest(BaseModel):
    model: str
    session_id: str = "default_session"
    user_message: str
    # Could be a base64 audio string or file path
    user_voice_memo: Optional[str] = None

    supporting_url_exist: bool = False
    supporting_url_title: List[str] = Field(default_factory=list)
    supporting_url: List[str] = Field(default_factory=list)

    @field_validator("model")
    @classmethod
    def check_model_supported(cls, v: str) -> str:
        if v not in ALLOWED_MODELS:
            raise ValueError(
                f"Supported models are {', '.join(ALLOWED_MODELS)}")
        return v

    @model_validator(mode="after")
    def check_input_provided(self):
        # Ensure that the user provided EITHER a text message OR a voice memo
        if not self.user_message and not self.user_voice_memo:
            raise ValueError(
                "You must provide either 'user_message' or 'user_voice_memo'")
        return self


class QueryResponse(BaseModel):
    # core response field
    ai_response: str

    # Voice memo
    assistant_voice_memo: bool = False
    assistant_voice_file: Optional[str] = None

    # Keeping the structured data from your SQL/RAG tools
    data: List[Dict[str, Any]] = Field(default_factory=list)


class LinkItem(BaseModel):
    title: str
    url: str


class OueryResponse(BaseModel):
    ai_response: str
    suggested_links: List[LinkItem] = Field(default_factory=list)

    assistant_voice_memo: bool = False
    assistant_voice_file: Optional[str] = None

    data: List[Dict[str, Any]] = Field(default_factory=list)


class RagUpdateRequest(BaseModel):
    content: str = ""
    update_mode: Literal["replace", "merge", "clear"] = "replace"
    model: str = RAG_REASONING_MODEL


class RagUpdateMetadata(BaseModel):
    model_used: str
    total_branches_created: int
    total_leaf_nodes_created: int


class RagUpdateResponse(BaseModel):
    status: str
    message: str
    metadata: RagUpdateMetadata

# RAG INDICES SCHEMAS


class RagTreeNode(BaseModel):
    id: str
    title: str
    content: Optional[str] = None
    children: List['RagTreeNode'] = []


class RagIndicesResponse(BaseModel):
    status: str
    total_nodes: int
    tree: List[RagTreeNode]


class RagRawDocument(BaseModel):
    id: str
    content: str
    created_at: str


class RagRawDocument(BaseModel):
    id: str
    content: str
    created_at: str


class RagDownloadResponse(BaseModel):
    status: str
    backup_date: str
    raw_documents: List[RagRawDocument]
    knowledge_tree: List[RagTreeNode]


RagTreeNode.model_rebuild()


# class UserQueryRequest(BaseModel):
#     query: str


# class ProcessedResponse(BaseModel):
#     status: str
#     tool_used: str
#     data: List[Dict[str, Any]]
#     message: Optional[str] = None
