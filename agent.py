import os
import time
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.8-flash"


def ask_ai(prompt):
    for attempt in range(6):
        try:
            return gemini.models.generate_content(model=MODEL, contents=prompt).text
        except Exception:
            print("Server busy, trying again in 15 seconds...")
            time.sleep(15)
    return "Sorry, the AI server is too busy. Try again later."


question = input("Ask your research question: ")

print("\nStep 1: Planning searches...")
plan = ask_ai(
    "Split this question into 3 short web search queries. "
    "Write one query per line. No numbers, no bullets, nothing else.\n"
    "Question: " + question
)
queries = [line.strip("-* ").strip() for line in plan.split("\n") if line.strip()][:3]
if plan.startswith("Sorry"):
    queries = [question]
for q in queries:
    print(" -", q)

print("\nStep 2: Searching the web...")
text = ""
for q in queries:
    results = tavily.search(q, max_results=3)
    for item in results["results"]:
        text += item["title"] + "\n" + item["url"] + "\n" + item["content"] + "\n\n"

print("\nStep 3: Writing the report...\n")
report = ask_ai(
    "Using only the information below, write a clear short report answering: "
    + question
    + "\nUse simple words. Add the source links at the end.\n\n"
    + text
)
print(report)