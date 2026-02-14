from groq import Groq
from backend.config import GROQ_API_KEY, LLM_MODEL
from backend.memory import memory
from backend.hybrid_search import hybrid_search
from backend.mcp_tools.duckduckgo_mcp import duckduckgo_mcp
import json

client = Groq(api_key=GROQ_API_KEY)


# ---------------------------

def query_analysis_agent(state):

    query = state["query"]
    session_id = state.get("session_id", "default")

    # -----------------------------------
    # STEP 1: Check if memory can answer
    # -----------------------------------
    stored_facts = memory.get_all_facts(session_id)

    if stored_facts:
        memory_check_prompt = """
You are a decision agent.

Given the stored user facts and a question,
determine if the question can be answered using ONLY the stored facts.

Respond with one word:
YES
or
NO
"""

        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": memory_check_prompt},
                {"role": "user", "content": f"Facts: {stored_facts}\n\nQuestion: {query}"}
            ],
        )

        memory_decision = completion.choices[0].message.content.strip().upper()

        if "YES" in memory_decision:
            state["route"] = "MEMORY"
            state["facts"] = stored_facts
            print("Routing Decision: MEMORY")
            return state

    # -----------------------------------
    # STEP 2: Normal Routing
    # -----------------------------------
    system_prompt = """
You are a routing classifier.

Classify the user question into one of these categories:

1. DOCUMENT → Question related to uploaded document.
2. GENERAL → General knowledge question.
3. REALTIME → Question requiring current or live information.

Respond with only one word:
DOCUMENT
GENERAL
REALTIME
"""

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
    )

    decision = completion.choices[0].message.content.strip().upper()

    state["route"] = decision

    print("Routing Decision:", decision)

    return state





def retrieval_agent(state):

    query = state["query"]
    route = state.get("route")

    if route == "DOCUMENT":
        docs = hybrid_search.search(query)
        state["context"] = "\n\n".join(docs)
        state["source"] = "documents"

    elif route == "REALTIME":
        web_results = duckduckgo_mcp.search_web(query)

        formatted = "\n\n".join([
            f"Title: {r['title']}\nContent: {r['body']}"
            for r in web_results
        ])

        state["context"] = formatted
        state["source"] = "web"

    else:  # GENERAL
        state["context"] = None
        state["source"] = "llm"

    return state




# ---------------------------
# 3️⃣ GENERATION AGENT
# ---------------------------
def generation_agent(state):

    query = state["query"]
    route = state.get("route")
    context = state.get("context")

    if route == "DOCUMENT":
        system_prompt = """
Answer ONLY using the provided document context.
If not found, say information not in document.
"""
        user_prompt = f"Context:\n{context}\n\nQuestion:\n{query}"

    elif route == "REALTIME":
        system_prompt = """
Answer using the provided web search results.
"""
        user_prompt = f"Web Results:\n{context}\n\nQuestion:\n{query}"

    else:  # GENERAL
        system_prompt = """
Answer as a knowledgeable assistant.
"""
        user_prompt = query

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    state["answer"] = completion.choices[0].message.content
    return state



def rerank_agent(state):
    """
    Simple placeholder reranker.
    Later you can add cross-encoder scoring.
    """
    context = state.get("context", "")
    # For now, pass through
    state["reranked_context"] = context
    return state

def citation_agent(state):
    """
    Adds basic citation formatting.
    """

    source = state.get("source", "documents")

    state["final_answer"] = {
        "answer": state.get("answer"),
        "source": source
    }

    return state


def memory_extraction_agent(state):

    query = state["query"]
    session_id = state.get("session_id", "default")

    system_prompt = """
Extract personal facts about the user from the message.
If there are no personal facts, return empty JSON.

Return only valid JSON.

Example:
Input: My name is Yaswanth and I live in Hyderabad.
Output:
{
  "name": "Yaswanth",
  "location": "Hyderabad"
}
"""

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
    )

    response = completion.choices[0].message.content.strip()

    try:
        facts = json.loads(response)
        if isinstance(facts, dict):
            memory.store_facts(session_id, facts)
    except:
        pass

    return state