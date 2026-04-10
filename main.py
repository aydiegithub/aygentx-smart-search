from app.llm.openrouter_client import chat
import time
from colorama import Fore, Style, init
init(autoreset=True)


def main():
    queries = [
        """
You are given a knowledge base. Answer the question using it.

### Knowledge Base:
AygentX is an AI-powered search system that combines SQL-based retrieval with vectorless RAG. 
It uses an agent to decide whether to query structured databases or perform keyword-based retrieval.
The system uses Cloudflare D1 for structured data and KV for fast indexing. 
It focuses on speed, cost-efficiency, and explainability over heavy vector search systems.

### Task:
Explain how AgentX works.

### Output Format:
- Use markdown
- Use bullet points for key ideas
- Use short paragraphs for explanations
- Keep it structured and readable
""",
        "Explain the difference between SQL retrieval and vectorless RAG.",
        "Why is Cloudflare KV used in AgentX?",
        "How does the agent decide between SQL and RAG?",
        "What are the advantages of vectorless RAG over vector search?"
    ]

    reasoning_models = [
        "liquid/lfm-2.5-1.2b-thinking:free",
        "openai/gpt-oss-120b:free",
        "openai/gpt-oss-20b:free",
    ]

    fast_models = [
        "liquid/lfm-2.5-1.2b-instruct:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "google/gemma-3n-e2b-it:free",
        "google/gemma-3n-e4b-it:free",
        "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "google/gemma-4-26b-a4b-it:free",
        "google/gemma-4-31b-it:free",
    ]

    def test_models(model_list, category_name):
        print(Fore.CYAN + Style.BRIGHT + f"\n===== {category_name} =====\n")

        results = []

        for model in model_list:
            total_time = 0

            try:
                for idx, query in enumerate(queries):
                    start_time = time.time()

                    response = chat(
                        model=model,
                        messages=[{"role": "user", "content": query}]
                    )

                    end_time = time.time()
                    latency = end_time - start_time
                    total_time += latency

                    print(Fore.BLUE + f"\nQ{idx+1} Response:")
                    print(Style.RESET_ALL + str(response)[:500])

                avg_latency = total_time / len(queries)
                results.append((model, avg_latency))

                print(Fore.GREEN + f"\n{model}" + Style.RESET_ALL +
                      f" -> Avg Latency: " + Fore.YELLOW + f"{avg_latency:.2f}s")
                print(Fore.WHITE + "=" * 60)

            except Exception as e:
                print(Fore.RED + f"{model} -> ERROR: {str(e)}")

        return results

    reasoning_results = test_models(reasoning_models, "REASONING MODELS")
    fast_results = test_models(fast_models, "FAST RESPONSE MODELS")

    print(Fore.MAGENTA + Style.BRIGHT + "\n===== SUMMARY =====\n")

    print(Fore.CYAN + Style.BRIGHT + "Reasoning Models:")
    for model, latency in reasoning_results:
        print(Fore.GREEN + f"{model}" + Style.RESET_ALL +
              " : " + Fore.YELLOW + f"{latency:.2f}s")

    print(Fore.CYAN + Style.BRIGHT + "\nFast Models:")
    for model, latency in fast_results:
        print(Fore.GREEN + f"{model}" + Style.RESET_ALL +
              " : " + Fore.YELLOW + f"{latency:.2f}s")


if __name__ == "__main__":
    main()
