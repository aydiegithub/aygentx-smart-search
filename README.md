# AygentX Smart Search

**AygentX Smart Search** is an AI-powered Master Control Program (MCP) backend built with **FastAPI**. It dynamically and intelligently routes user queries between structured SQL Retrieval (Cloudflare D1) and a custom Vectorless Hierarchical Agentic RAG to deliver precise, context-aware results. It also features a **Real-Time Voice Agent** powered by the Gemini Multimodal Live API.

---

## Table of Contents
1. [Project Documentation](#project-documentation)
2. [For Backend Developers (Cloning & Setup)](#for-backend-developers-cloning--setup)
3. [API Usage Tutorial & Route Reference](#api-usage-tutorial--route-reference)
4. [Code Integration Examples](#code-integration-examples)
5. [Security Best Practices](#security-best-practices)
6. [Contact & Author](#contact--author)

---

## Project Documentation

### Architecture Overview
The backend acts as an intelligent router and synthesizer. Instead of blindly passing user text to an LLM, the system operates in three distinct phases:
1. **Intent Analysis:** A lightweight LLM acts as a router to determine if the query requires querying a structured database, searching personal unstructured knowledge (RAG), or engaging in general conversation.
2. **Tool Execution:** The system autonomously calls the respective tools (e.g., `query_cloudflare_d1` or `search_vectorless_rag`).
3. **Synthesis:** It combines the raw JSON/SQL data into a polished, Markdown-formatted conversational response.

### Core Features
*   **Intelligent Query Routing:** Automatically decides which database or knowledge tree to search without user intervention.
*   **Vectorless Hierarchical RAG:** Bypasses traditional vector embeddings. It uses Gemini to ingest raw text, structure it into a hierarchical JSON Tree (Table of Contents), and query it natively using SQLite/D1.
*   **Real-Time Voice Agent:** A WebSocket endpoint that streams raw PCM 16kHz audio directly to Google's Gemini Live API, supporting real-time function calling (RAG + SQL) mid-conversation.
*   **Cloudflare D1 Integration:** Fast, serverless SQLite edge database integration for structured portfolio and project data.

---

## For Backend Developers (Cloning & Setup)

If you are cloning this repository to run it locally, extend its features, or deploy it to AWS, follow these steps.

### Prerequisites
*   Python 3.10+
*   [`uv` package manager](https://github.com/astral-sh/uv) (recommended) or standard `pip`
*   Google Gemini API Key
*   Cloudflare D1 Database credentials

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/aydiegithub/aygentx-smart-search.git
   cd aygentx-smart-search
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   # OR: pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   API_SECRET_KEY=your_super_secret_api_key_here
   GEMINI_API_KEY=your_google_gemini_key
   CLOUDFLARE_ACCOUNT_ID=your_cf_account_id
   CLOUDFLARE_DATABASE_ID=your_cf_d1_db_id
   CLOUDFLARE_API_TOKEN=your_cf_api_token
   ```

4. **Run the Server:**
   ```bash
   uv run main.py
   ```
   The API will be available at `http://localhost:8000`. You can view the interactive Swagger documentation at `http://localhost:8000/docs`.

---

## API Usage Tutorial & Route Reference

All REST endpoints require the `x-api-key` header. The WebSocket endpoint requires the `?api_key=` query parameter.

### 1. Main Text Query (The Chat Endpoint)
This is the primary endpoint for text-based chat. Send a user query, and the backend will route it, run tools, and return the synthesized response.

**Request:** `POST /api/v1/query`
```json
{
  "user_message": "Tell me about Aydie's latest music release.",
  "model": "gemini-3.1-flash-lite-preview",
  "session_id": "001"
}
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "ai_response": "Aydie's latest release is 'Your Quest', a highly motivational rap track released in early 2024. The song compares life to a thrilling sea and urges listeners to persevere.",
  "metadata": {
    "tools_used": ["query_cloudflare_d1"],
    "routing_decision": "database_lookup"
  }
}
```

### 2. Update RAG Knowledge Base
Ingest raw, unstructured text into the Vectorless RAG brain. The AI will parse the text, identify topics, and build/update a hierarchical folder structure in the database.

**Request:** `POST /api/v1/rag/update`
```json
{
  "content": "Aditya Dinesh K is a software engineer and musician known as Aydie. He started coding in 2018.",
  "update_mode": "merge", 
  "model": "gemini-2.5-pro"
}
```
*Note on `update_mode`: `merge` appends data and reorganizes the tree. `replace` deletes the existing tree and builds a new one from scratch. `clear` formats the database.*

**Success Response (200 OK):**
```json
{
  "status": "success",
  "message": "Knowledge base successfully merged and updated.",
  "metadata": {
    "model_used": "gemini-2.5-pro",
    "total_branches_created": 2,
    "total_leaf_nodes_created": 5
  }
}
```

### 3. Get RAG Tree Indices
Fetch the generated JSON Table of Contents representing the AI's internal knowledge structure.

**Request:** `GET /api/v1/rag/indices`

**Success Response (200 OK):**
```json
[
  {
    "id": "branch_tech_career",
    "title": "Technology & Software Engineering",
    "content": null,
    "children": [
      {
        "id": "leaf_early_coding",
        "title": "Started coding in 2018",
        "content": "Aditya Dinesh K started his coding journey in 2018, initially exploring Python and web development.",
        "children": []
      }
    ]
  }
]
```

### 4. Download Database Backup
Download the raw documents and current tree structure as a JSON file for backup purposes.

**Request:** `GET /api/v1/rag/download?file=true`

**Success Response (200 OK):**
Returns a downloadable JSON file attachment (e.g., `2026-04-14-knowledge_backup.json`).

### 5. Live Voice Stream (WebSocket)
Establish a persistent, two-way connection for real-time voice conversations.

**Request:** `WS /api/v1/voice/stream?api_key=YOUR_API_KEY`

**Usage Flow:**
1. Client connects to the WebSocket URL.
2. Client captures microphone audio at a 16kHz sample rate.
3. Client sends raw binary `Int16Array` (PCM16) chunks over the WebSocket.
4. Server intercepts tool calls (RAG/SQL) silently in the background.
5. Server streams raw binary `Int16Array` (PCM16) chunks back to the client.
6. Client decodes to `Float32` and plays through the Web Audio API.

---

## Code Integration Examples

### Python (Backend-to-Backend Integration)

**Querying the Text API**
```python
import requests
import json

API_KEY = "your_super_secret_api_key_here"
HEADERS = {
    "x-api-key": API_KEY, 
    "Content-Type": "application/json"
}

payload = {
    "user_message": "What projects has Aydie built?",
    "model": "gemini-3.1-flash-lite-preview",
    "session_id": "001"
}

response = requests.post(
    "http://localhost:8000/api/v1/query",
    headers=HEADERS,
    json=payload
)

if response.status_code == 200:
    data = response.json()
    print("AI Response:", data["ai_response"])
else:
    print("Error:", response.text)
```

### Next.js (TypeScript Frontend Integration)

**1. Querying the Text API (Server Action)**
*Always execute REST API calls securely from the server side to protect your API key.*

```typescript
// app/actions.ts
'use server'

export async function askAygentX(userQuery: string) {
  try {
    const res = await fetch('http://localhost:8000/api/v1/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.AYGENTX_SECRET_KEY as string,
      },
      body: JSON.stringify({ 
        user_message: userQuery,
        model: "gemini-3.1-flash-lite-preview",
        session_id: "001"
      }),
    });

    if (!res.ok) {
      throw new Error(`API Error: ${res.status}`);
    }

    const data = await res.json();
    return data.ai_response;
  } catch (error) {
    console.error("Failed to fetch from AygentX", error);
    return "Sorry, I am currently unavailable.";
  }
}
```

**2. Connecting to the Voice WebSocket (Client Component)**
```typescript
// components/VoiceAgentButton.tsx
'use client'
import { useState, useRef } from 'react';

export default function VoiceAgentButton() {
  const [isListening, setIsListening] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  const startVoiceSession = async () => {
    try {
      // 1. Request Microphone
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { sampleRate: 16000 } });
      
      // 2. Connect WebSocket
      // Note: See "Security Best Practices" regarding exposing API keys in URLs
      const wsUrl = `wss://api.yourdomain.com/api/v1/voice/stream?api_key=${process.env.NEXT_PUBLIC_VOICE_API_KEY}`;
      const ws = new WebSocket(wsUrl);
      ws.binaryType = "arraybuffer";

      ws.onopen = () => {
        setIsListening(true);
        
        // 3. Setup Audio Context & Processor
        const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
        audioContextRef.current = audioCtx;
        
        const source = audioCtx.createMediaStreamSource(stream);
        const processor = audioCtx.createScriptProcessor(4096, 1, 1);
        
        processor.onaudioprocess = (e) => {
          if (ws.readyState !== WebSocket.OPEN) return;
          
          // Convert Float32 to Int16 PCM
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm16Buffer = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            let s = Math.max(-1, Math.min(1, inputData[i]));
            pcm16Buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
          }
          ws.send(pcm16Buffer.buffer);
        };

        source.connect(processor);
        processor.connect(audioCtx.destination);
      };

      // 4. Handle Incoming Audio from AI
      ws.onmessage = async (event) => {
        if (event.data instanceof ArrayBuffer && audioContextRef.current) {
          const int16Array = new Int16Array(event.data);
          const float32Array = new Float32Array(int16Array.length);
          
          for (let i = 0; i < int16Array.length; i++) {
            float32Array[i] = int16Array[i] / (int16Array[i] < 0 ? 0x8000 : 0x7FFF);
          }

          const audioBuffer = audioContextRef.current.createBuffer(1, float32Array.length, 24000);
          audioBuffer.getChannelData(0).set(float32Array);
          
          const sourceNode = audioContextRef.current.createBufferSource();
          sourceNode.buffer = audioBuffer;
          sourceNode.connect(audioContextRef.current.destination);
          sourceNode.start();
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error("Microphone access denied or connection failed", err);
    }
  };

  const stopVoiceSession = () => {
    if (wsRef.current) wsRef.current.close();
    if (audioContextRef.current) audioContextRef.current.close();
    setIsListening(false);
  };

  return (
    <button onClick={isListening ? stopVoiceSession : startVoiceSession}>
      {isListening ? 'End Call' : 'Start Voice Chat'}
    </button>
  );
}
```

---

## Security Best Practices

When deploying this API to production (e.g., AWS, Render, Railway):

1. **Protect your Admin Routes:** The `/rag/update` and `/rag/download` routes can overwrite or expose your entire database. Ensure your master `API_SECRET_KEY` is strictly kept on the server side and never exposed in client-side code (like React/Next.js).
2. **WebSocket Authentication:** Browser WebSockets do not support custom headers, meaning the API key must be passed in the query URL (`?api_key=...`). 
   * Do not put your master admin key in the public frontend code. 
   * For production, it is recommended to implement a secondary, read-only API key (e.g., `NEXT_PUBLIC_VOICE_KEY`) that is only accepted by the `/voice/stream` endpoint, or utilize a Backend-For-Frontend (BFF) proxy to handle the connection securely.

---

## Contact & Author

*   **Repository:** [aydiegithub/aygentx-smart-search](https://github.com/aydiegithub/aygentx-smart-search)
*   **Developer Name:** Aditya (Aydie) Dinesh K
*   **Developer Website:** [www.aydie.in](https://www.aydie.in)
*   **Email:** [aditya@aydie.in](mailto:aditya@aydie.in)