# Enterprise AI Chat Interface (Chainlit Frontend)

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Async](https://img.shields.io/badge/Async-HTTPX-orange)

## 📋 Executive Summary

This repository contains a robust, asynchronous chat interface built with **Chainlit**. It is designed to serve as a secure frontend orchestrator between end-users and a proprietary **AI Middleware**.

The solution is engineered to handle **Customer Service** workflows (e.g., Order Tracking, Returns, General Inquiries) with a focus on **high concurrency**, **state management**, and **user experience (UX)**.

## Key Features

- ⚡ **Asynchronous Architecture:** Utilizes `httpx` and `asyncio` for non-blocking I/O, ensuring high throughput and low latency compared to traditional synchronous requests.
- 🧠 **Session State Management:** Implements persistent conversation history within the user session, allowing the AI to maintain context (memory) across multiple interactions.
- 🔒 **Security by Design:** Strict separation of configuration and code via Environment Variables. No sensitive URLs or API keys are hardcoded.
- ✨ **Optimistic UI & UX:** Features transitional states ("Thinking...", "Connecting to Specialist...") to manage user expectations and reduce perceived latency.
- ⚙️ **Configurable Persona:** The bot's name, role, and welcome message are fully customizable via environment variables without touching the codebase.

## 🏗 Architecture

The application acts as a stateless frontend layer that forwards user intent and history to a backend logic tier.


```mermaid
graph TB
    subgraph "📧 Email Input"
        Gmail["Gmail API<br/>(Email Worker)"]
    end

    subgraph "🖥️ Frontend (Opcional)"
        User("👤 End User") <-->|HTTP/JSON| Chat["Chat Endpoint<br/>(/chat)"]
    end

    subgraph "⚙️ Backend Infrastructure"
        Gmail -->|Polling cada 60s| Security["🛡️ Gatekeeper<br/>(Spam Filter)"]
        Security -->|PROCESS| Router["🧠 Main Router<br/>(Classifier)"]
        Security -->|IGNORE| Trash["🗑️ Mark as Read"]
        Chat --> Router
        
        Router --> Agents["👥 Specialized Agents<br/>(9 Categories)"]
        Agents <-->|Function Calling| Tools["🔧 Tools Engine"]
    end

    subgraph "🤖 AI Layer"
        Router <-->|Classification| OpenAI["OpenAI API<br/>(GPT-4o / GPT-4o-mini)"]
        Agents <-->|Generation| OpenAI
    end

    subgraph "🛍️ Data Sources"
        Tools <-->|REST + GraphQL| Shopify["Shopify Admin API"]
        Shopify --- Orders["📦 Orders"]
        Shopify --- Products["🏷️ Products"]
        Shopify --- Inventory["📊 Inventory"]
        Shopify --- Customers["👤 Customers"]
    end

    subgraph "📤 Output"
        Agents -->|Create Draft| Drafts["📝 Gmail Drafts"]
        Drafts -->|Human Review| Send["✉️ Send Email"]
    end

    style Security fill:#ff6b6b,stroke:#333,stroke-width:2px
    style Router fill:#4ecdc4,stroke:#333,stroke-width:2px
    style OpenAI fill:#9b59b6,stroke:#333,stroke-width:2px
    style Shopify fill:#96ceb4,stroke:#333,stroke-width:2px
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- `pip` (Python Package Manager)
- A running instance of the AI Middleware (Backend)

### 1. Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/hitthecodelabs/EnterpriseAICchat-Chainlit.git
cd EnterpriseAICchat-Chainlit
```

Create a virtual environment:

```bash
# MacOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory. You can use the provided example as a template:

```bash
cp .env.example .env
```

Required Variables:

| Variable           | Description                         | Example                          |
|-------------------|-------------------------------------|----------------------------------|
| `BACKEND_API_URL` | Endpoint of your AI Middleware      | `https://api.yourcompany.com/chat` |
| `BACKEND_API_SECRET` | Secure key to authenticate requests | `sk_prod_12345...`               |
| `BOT_NAME`        | Name displayed to the user          | `Maria S.`                       |
| `BOT_ROLE`        | Role description in welcome message | `Support Specialist`             |

### 3. Usage

Run the application locally with hot-reloading enabled:

```bash
chainlit run app.py -w
```

The interface will be available at: `http://localhost:8000`.

## 🛠 Project Structure

```text
├── .env.example       # Template for environment variables (Safe to commit)
├── .gitignore         # Ignores .env and venv (Security best practice)
├── app.py             # Main application logic (Async & Stateful)
├── chainlit.md        # Chainlit welcome markdown (Optional)
├── requirements.txt   # Project dependencies
└── README.md          # Project documentation
```

## 📦 Deployment (Production)

For production environments (e.g., Railway, AWS ECS, Docker), ensure the start command is configured to run headless:

```bash
chainlit run app.py --host 0.0.0.0 --port 8000 --headless
```

### Docker Support

This project is Docker-ready. Ensure you pass the environment variables defined in `.env` securely through your container orchestration platform secrets manager.

## 🛡 Disclaimer

This software is provided "as is", without warranty of any kind. It is intended as a frontend template and requires a functioning backend API to process natural language queries.

## 📝 Consultant Notes for Implementation

- **Customization:** Edit the `Config` class in `app.py` or update your `.env` file to change the bot's behavior.
- **Logging:** The application uses Python's standard `logging` library. In a production environment, ensure these logs are piped to a monitoring tool like Datadog or CloudWatch.
