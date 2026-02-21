# 🧠 RequirementIQ — AI Requirements Generator

> Transform raw stakeholder discussions into professional BRDs, FRDs, and Agile artifacts in seconds.

**Stack:** Streamlit · Python 3.12 · MySQL · OpenAI GPT-4o

---

## 📁 Project Structure

```
AI BA-PM/
├── app.py                      # Main entry + Login/Register/Dashboard
├── config.py                   # Settings (pydantic-settings from .env)
├── requirements.txt
│
├── pages/                      # Streamlit multi-page app
│   ├── 01_Generate.py          # Upload/paste → Generate workflow
│   ├── 02_Document.py          # Document viewer + Export
│   ├── 03_History.py           # All past documents
│   └── 04_Settings.py          # Account, plan, AI usage stats
│
├── ai/                         # AI Orchestration Layer
│   ├── orchestrator.py         # Pipeline controller (parallel + sequential)
│   ├── domain_context.py       # Domain-aware context injection
│   └── chains/
│       ├── brd_chain.py        # BRD generation
│       ├── frd_chain.py        # FRD generation
│       ├── agile_chain.py      # Epics + Stories + Gherkin AC
│       ├── gap_chain.py        # Gap detection (7 categories)
│       └── risk_chain.py       # Risk engine (6 categories)
│
├── services/                   # Business Logic
│   ├── auth_service.py         # Register/login/quota
│   ├── document_service.py     # Save/fetch documents from MySQL
│   ├── file_parser.py          # .txt / .docx / paste → clean text
│   └── export_service.py       # ReportLab PDF + python-docx DOCX
│
├── database/
│   ├── connection.py           # SQLAlchemy engine + session
│   └── schema.sql              # MySQL DDL (all 8 tables)
│
├── utils/
│   ├── text_chunker.py         # Token-aware text splitting
│   └── domain_classifier.py   # Keyword-based domain detection
│
└── .streamlit/
    └── config.toml             # Theme + server config
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- OpenAI API key

### 1. Clone and setup environment

```bash
cd "d:\My projects\AI BA-PM"
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Configure environment

```bash
copy .env.example .env
# Edit .env and fill in:
# OPENAI_API_KEY=sk-...
# DB_HOST=localhost
# DB_USER=your_mysql_user
# DB_PASSWORD=your_mysql_password
```

### 3. Create MySQL database and schema

```bash
# In MySQL shell:
mysql -u root -p < database/schema.sql

# OR let the app auto-init on first run (init_db() in app.py)
```

### 4. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |
| `DB_HOST` | ✅ | MySQL host (default: localhost) |
| `DB_USER` | ✅ | MySQL username |
| `DB_PASSWORD` | ✅ | MySQL password |
| `DB_NAME` | ✅ | Database name (default: requirementiq) |
| `OPENAI_MODEL` | ❌ | Model to use (default: gpt-4o) |
| `AI_MAX_RETRIES` | ❌ | Retry count on AI errors (default: 2) |
| `FREE_TIER_MONTHLY_DOCS` | ❌ | Free tier limit (default: 3) |

---

## 🧠 AI Pipeline Flow

```
User Input (.txt / .docx / paste)
    ↓
File Parser → Clean Text
    ↓
Domain Classifier (keyword-based, no LLM)
    ↓
Stage 3: Parallel Generation ─────────────────────────────────
  ├── BRD Chain (GPT-4o, JSON mode)
  ├── FRD Chain (GPT-4o, JSON mode)
  └── Agile Chain (GPT-4o, JSON mode + Gherkin)
    ↓
Stage 4: Sequential Intelligence
  ├── Gap Detection Chain (7 gap categories)
  └── Risk Engine Chain (6 risk categories)
    ↓
Assemble → Score → Save to MySQL → PDF/DOCX Export
```

---

## 📊 Database Tables

| Table | Purpose |
|---|---|
| `users` | Auth, plan, quota tracking |
| `projects` | Document grouping |
| `documents` | Generation jobs + status |
| `generated_artifacts` | BRD/FRD/Agile JSON content |
| `gap_reports` | Gap analysis results |
| `risk_reports` | Risk register |
| `ai_usage_logs` | Token + cost tracking per chain |
| `industry_templates` | Domain-specific prompt contexts |

---

## 💰 Estimated AI Cost

| Generation | Tokens | Estimated Cost |
|---|---|---|
| BRD + FRD + Agile + Gap + Risk | ~14,000 | ~$0.15–0.25 |
| BRD only | ~6,000 | ~$0.06 |

---

## 🚀 Next Steps (Post-MVP)

- [ ] Stripe billing integration (upgrade flow)
- [ ] Document version history
- [ ] Jira/Confluence export integration
- [ ] Team workspace / multi-user access
- [ ] Fine-tuned model for domain-specific accuracy
- [ ] Docker containerization for deployment

---

*Built with Antigravity AI · RequirementIQ v0.1.0 MVP*
