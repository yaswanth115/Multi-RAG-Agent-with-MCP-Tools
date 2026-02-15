# Multi-RAG-Agent-with-MCP-Tools
Step 1: Clone the repository into Local

  git clone https://github.com/yaswanth115/Multi-RAG-Agent-with-MCP-Tools

Step2: Create the Virtual Environment and Activate it

● Python3 -m venv venv

● Source venv/bin/activate

Step 3: Go to Groq API keys(free source) https://console.groq.com/keys

● Sign up with Gmail and create a API and copy it

● Create a .env file in project folder store the API key which you have copied before

● In Groq there are lot of models which is free , you can use any models.
● Explore the all models and test it Accuracy https://console.groq.com/playground

Step 4: Run the Code

● cd frontend

● python -m http.server 5500

● Open the brower and visit http://localhost:5500

● Then you could ask Questions

Test the Backend: uvicorn backend.main:app --reload

Project Overview

This project implements a multi-agent Retrieval-Augmented Generation (RAG) system using
LangGraph for orchestration.

The system allows users to:

● Upload documents (PDF / TXT)

● Build a knowledge base

● Ask document-related questions

● Ask general knowledge questions

● Ask real-time questions (via web search)

● Maintain conversation memory across sessions

The system dynamically routes queries to:

● Document RAG

● LLM direct response

● Web Search (DuckDuckGo MCP)

● Memory store
