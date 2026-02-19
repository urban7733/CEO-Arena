# CEO Arena

CEO Arena is a professional AI application that delivers simulation based conversations with four iconic tech CEOs. The project combines a modern single page interface with a RAG powered backend built on curated public sources, producing responses with distinct voice and personality.

## Vision

The goal of CEO Arena is to create a conversation experience that feels clear, fast, and credible. Users choose a speaker, start chatting instantly, and keep a persistent local conversation history. The product is designed with strong user experience standards and a reliable retrieval pipeline at its core.

## Current Capabilities

1. Speaker selection across Elon Musk, Sam Altman, Dario Amodei, and Mark Zuckerberg.
2. Persistent browser based chat history through local storage.
3. FastAPI backend with chat, debate, health, and speaker endpoints.
4. RAG retrieval with dedicated Pinecone namespaces per speaker.
5. Response generation through Groq with speaker specific prompts.
6. Full data pipeline for collection, normalization, and ingestion.
7. Render ready fullstack deployment through a unified Blueprint setup.

## Technical Architecture

The architecture is intentionally clean and separated.

1. Frontend
React, TypeScript, and Vite power a high performance single page application with a polished glassmorphic design system.

2. Backend
FastAPI exposes the API and initializes the query engine at startup.

3. Retrieval and Generation
LlamaIndex connects embeddings, vector search, and prompting. Pinecone stores vectors in dedicated speaker namespaces. Groq handles response generation.

4. Data Pipeline
Collectors fetch public content, normalization enforces a consistent schema, and ingestion writes processed data into the vector store.

## Local Setup

### Requirements

1. Python 3.11 or newer
2. Node.js 20 or newer
3. API keys for Pinecone and Groq

### Start Backend

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`
5. Fill `.env` with real values
6. `python api.py`

### Start Frontend

1. `cd frontend`
2. `npm ci`
3. `npm run dev`

## Run Data Pipeline

1. `python run_collection.py`
2. `python normalize.py`
3. `python -m rag.ingest`

Collection can also be run per speaker when only partial updates are needed.

## API Overview

1. `GET /api/health`
2. `GET /api/speakers`
3. `POST /api/chat`
4. `POST /api/debate`

## Deployment on Render

This repository includes a production focused `render.yaml` that provisions both services through Render Blueprint.

1. Create a new Blueprint deployment in Render.
2. Select this repository and the `main` branch.
3. Configure secrets for `PINECONE_API_KEY` and `GROQ_API_KEY`.
4. Start deployment and verify both service URLs.
5. If service names differ, update `ALLOWED_ORIGINS` and `VITE_API_BASE` accordingly.

## Deployment on Cloudflare Pages

The frontend is also deployable on Cloudflare Pages.

1. Change into frontend directory with `cd frontend`.
2. Authenticate once with `npx wrangler login` and verify via `npx wrangler whoami`.
3. Set `VITE_API_BASE` in Cloudflare Pages project settings to your backend URL, for example `https://your-render-backend.onrender.com/api`.
4. Deploy with `npm run cf:deploy`.
5. Use `npm run cf:dev` for local Pages runtime preview.

## Security and Secrets

The project cleanly separates code and configuration.

1. Secrets live in `.env` and are not versioned.
2. `.env` is excluded via `.gitignore`.
3. `.env.example` contains placeholders only.
4. Runtime configuration for deployment is managed via environment variables.

## Quality Status

The current state is strong and release ready.

1. Frontend build is passing.
2. Linting is passing.
3. Python syntax checks are passing.

CEO Arena is in an excellent position for a professional production rollout on Render.
