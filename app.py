import os
import time
import streamlit as st
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
            time.sleep(15)
    return "Sorry, the AI server is too busy. Try again later."


st.set_page_config(page_title="AI Research Agent", page_icon="🔎")
st.title("🔎 AI Research Agent")
st.write("Ask any question. The agent searches the web, writes a report with sources, and checks how much you can trust it.")

question = st.text_input("Your research question")

if st.button("Research") and question:
    with st.spinner("Step 1: Planning searches..."):
        plan = ask_ai(
            "Split this question into 3 short web search queries. "
            "Write one query per line. No numbers, no bullets, nothing else.\n"
            "Question: " + question
        )
        queries = [line.strip("-* ").strip() for line in plan.split("\n") if line.strip()][:3]
        if plan.startswith("Sorry"):
            queries = [question]

    st.subheader("Step 1: Search plan")
    for q in queries:
        st.write("•", q)

    with st.spinner("Step 2: Searching the web..."):
        text = ""
        sources = []
        for q in queries:
            results = tavily.search(q, max_results=3)
            for item in results["results"]:
                text += item["title"] + "\n" + item["url"] + "\n" + item["content"] + "\n\n"
                sources.append((item["title"], item["url"]))

    with st.spinner("Step 3: Writing the report..."):
        report = ask_ai(
            "Using only the information below, write a clear short report answering: "
            + question
            + "\nUse simple words. Add the source links at the end.\n\n"
            + text
        )

    st.subheader("Step 3: Report")
    st.markdown(report)

    with st.spinner("Step 4: Checking trust..."):
        check = ask_ai(
            "Look at the information below. Do the sources agree with each other? "
            "Answer in exactly 3 short lines, simple words:\n"
            "Confidence score (1 to 10): <number>\n"
            "Why: <one short reason>\n"
            "Conflicts: <facts where sources disagree, or None>\n\n"
            "Question: " + question + "\n\n" + text
        )

    st.subheader("Step 4: Trust check")
    st.info(check.replace("\n", "\n\n"))

    with st.expander("All sources"):
        for title, url in sources:
            st.markdown("- [" + title + "](" + url + ")")