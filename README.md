# 🎓 XJTLU Academic Navigator

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

> An MCP (Model-Context-Protocol) based AI assistant for XJTLU Economics students. This project demonstrates how commercial AI systems can integrate fragmented academic data sources without requiring official API access.

![Academic Navigator Interface](docs/demo_screenshots/dashboard.png)

## 🔍 Project Vision

Current academic systems at XJTLU (Learning Mall, e-Bridge) operate in isolation, forcing students to manually synthesize information. Our solution provides:

- ✨ **Course explanations** contextualized to career goals (e.g., HKU MFWM preparation)  
- 📅 **Personalized semester planning** based on academic background and credit constraints  
- 🎯 **Career pathway analysis** mapping XJTLU Economics courses to target graduate programs  
- 🔍 **Prerequisite validation** and workload assessment for optimal course selection

## 🏗️ MCP Architecture

![MCP Architecture Diagram](docs/architecture/mcp_diagram.png)

Our system implements a strict **Model-Context-Protocol separation**:

| Component | Role | Implementation |
|-----------|------|----------------|
| **Model** | AI reasoning engine | DeepSeek API integration with professional fallbacks |
| **Context** | Academic knowledge base | Mock data derived from official XJTLU Economics programme specification |
| **Protocol** | Standardized communication | JSON message format with intent routing and validation rules |

### Key Architectural Components:

- **Dispatcher**: Intent recognition and request routing
- **Orchestrator**: Multi-agent coordination for complex queries
- **Course Service**: Semantic search over curriculum data
- **Planning Service**: Rule-based semester planning with AI enhancement
- **AI Service**: Unified interface for LLM interactions with graceful degradation

## 🛡️ Compliance & Ethics

This project strictly adheres to ethical and compliance standards:

- ✅ **No access to real student data** - all data is synthetic/mock
- ✅ **No scraping of XJTLU systems** - course data derived from publicly available programme specifications
- ✅ **Transparent AI sourcing** - all AI-generated content is clearly marked
- ✅ **Privacy by design** - no user data persistence in demo version
- ✅ **Academic integrity** - all course descriptions accurately reflect official XJTLU curriculum

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js (optional, for frontend enhancements)
- DeepSeek API Key (optional - mock mode available)

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/xjtlu-academic-navigator.git
cd xjtlu-academic-navigator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your DeepSeek API key (or keep USE_MOCK_AI=true)
