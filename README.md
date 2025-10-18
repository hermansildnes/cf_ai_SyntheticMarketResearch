# Synthetic Market Research

A full-stack AI-powered market research platform built with Cloudflare Workers, featuring synthetic consumer evalutation and intelligent product insights.


**Proof of concept based on findings from [this paper](https://arxiv.org/abs/2510.08338).**

## Overview

This platform uses Cloudflare Workers AI (llama 3.2) to create synthetic consumer personas that evaluate products across different demographics. It implements the Semantic Similarity Rating (SSR) method presented by [Maier et al.](https://arxiv.org/abs/2510.08338) for converting qualitative AI feedback into quantitative Likert-scale distributions.

## Components

- **`api/`** - Python Worker for synthetic consumer evaluations using Workers AI and Semantic Similarity Ratings
- **`backend/`** - TypeScript Worker with Durable Objects for session management and LLM chat interface
- **`frontend/`** - Svelte frontend running on Cloudflare Pages for uploading products and chatting with Workers AI LLM for further insights
- **`shared/`** - Shared TypeScript types and interfaces

## Features

- **Syntetic Market Research**: Uses Llama 3.2 Vision model to qualitativly evaluate a product across multiple demographics
- **Semantic Similarity Ratings**: Converts qualitative responses to quantitative ratings using semantic similarity
- **Session Management**: Durable Objects for persistent user sessions and chat history
- **LLM Chat**: Ask questions about market research data to gain further insights

## Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Cloudflare account with API access

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/hermansildnes/cf_ai_SyntheticMarketResearch.git
cd cf_ai_SyntheticMarketResearch
```

2. **Install dependencies**
```bash
# Python dependencies for API
cd api
uv sync
cd ..

# Node dependencies for backend
cd backend
npm install
cd ..

# Node dependencies for frontend
cd frontend
npm install
cd ..
```

3. **Configure environment**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Cloudflare credentials:
# CLOUDFLARE_API_KEY
# CLOUDFLARE_ACCOUNT_ID
```

4. **Start the application**
```bash
./run.sh
```

The app will be available at `http://localhost:5173`

### Manual Start (Alternative)

If you prefer to start services individually:

```bash
# Terminal 1: TypeScript Backend
cd backend
npm run dev

# Terminal 2: Python API
cd api
npx wrangler dev

# Terminal 3: Svelte Frontend
cd frontend
npm run dev
```

### What You'll See

1. **Upload Page** - Drag and drop (or upload) a product image
2. **Processing** - Wait for the AI-powered market research to complete
3. **Results** - See ratings across demographics
4. **Chat** - Ask questions about the evaluation results

