# CEO Arena

CEO Arena is a fullstack RAG application for conversations with four AI simulated tech leaders.
It combines a modern single page chat UI with a FastAPI backend, Pinecone retrieval, and Groq generation.

## Current Capabilities

1. One chat interface with four selectable speakers
2. Persistent local chat history in the browser
3. FastAPI endpoints for chat, debate, health, and speakers
4. RAG retrieval with speaker specific namespaces in Pinecone
5. Speaker specific prompting and response style control
6. End to end data pipeline for collection, normalization, and ingestion
7. Cloudflare Pages ready frontend deployment

## Architecture

1. Frontend  
React, TypeScript, and Vite

2. Backend  
FastAPI with a startup initialized query engine

3. Retrieval and Generation  
LlamaIndex, Pinecone, and Groq

4. Data Pipeline  
Collectors, normalization, and ingestion scripts

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
3. `VITE_API_BASE=http://127.0.0.1:8000/api npm run dev`

## Data Pipeline

1. `python run_collection.py`
2. `python normalize.py`
3. `python -m rag.ingest`

## API Endpoints

1. `GET /api/health`
2. `GET /api/speakers`
3. `POST /api/chat`
4. `POST /api/debate`

## Cloudflare Deployment

### Frontend on Cloudflare Pages

1. `cd frontend`
2. `npx wrangler login`
3. `npx wrangler whoami`
4. Set `VITE_API_BASE` in Cloudflare Pages project settings to your backend API URL
5. `npm run cf:deploy`

### Frontend local Cloudflare preview

1. `cd frontend`
2. `npm run cf:dev`

## Security

1. Secrets are loaded from environment variables
2. `.env` is excluded from git
3. `.env.example` keeps placeholders only
