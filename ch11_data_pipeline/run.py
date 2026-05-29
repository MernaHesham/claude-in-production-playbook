from dotenv import load_dotenv
from pipeline.orchestrator import analyse

load_dotenv()

if __name__ == "__main__":
    result = analyse(
        "What are the top 5 products by total revenue? "
        "Create a bar chart and write a one-paragraph summary."
    )
    print(result["report"])
    for a in result["artefacts"]:
        if a.kind == "chart":
            print(f"\nChart saved: {a.content}")
