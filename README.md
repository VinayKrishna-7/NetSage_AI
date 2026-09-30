# NetSage AI
### *AI-Assisted Network Troubleshooting with Human Review*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![CI](https://github.com/VinayKrishna-7/NetSage_AI/actions/workflows/python-tests.yml/badge.svg)](https://github.com/VinayKrishna-7/NetSage_AI/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-39%20Passing-brightgreen.svg)]()
[![Domain](https://img.shields.io/badge/Domain-Cisco%20Packet%20Tracer-005073.svg)]()

> **In One Sentence:**  
> An AI-assisted troubleshooter for Cisco Packet Tracer lab problems that reads symptoms and `show` command outputs, suggests likely causes and next steps, and **always requires a human to review before accepting the fix**.

---

## 🛡️ Safety & Policy Rules
- **Advisory Role Only:** AI recommendations are purely diagnostic. NetSage AI **never automatically executes or applies configuration changes** to lab hardware or Packet Tracer.
- **Mandatory Human Review:** Every diagnosis must be reviewed, verified, and graded by a human engineer as **`ACCEPTED`**, **`EDITED`**, or **`REJECTED`**.

---

## 🌟 What the Project Does

```
+-------------------------------------------------------------------------+
|                    Cisco Packet Tracer Lab Evidence                     |
|           (Symptom, Topology, Client IP, Show-Command Output)           |
+------------------------------------+------------------------------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
        +-----------------------+         +-----------------------+
        |  Python Rule Checker  |         |  AI Diagnosis Engine  |
        | - Mathematical IP math|         | - Structured JSON     |
        | - 15 non-AI checks    |         | - Cites CLI evidence  |
        | - Zero-cost offline   |         | - Offline Mock Mode   |
        +-----------+-----------+         +-----------+-----------+
                    |                                 |
                    +----------------+----------------+
                                     |
                                     v
                  +-------------------------------------+
                  |    Human Reviewer Oversight Gate    |
                  |       [ACCEPT]  [EDIT]  [REJECT]    |
                  +------------------+------------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
        +-----------------------+         +-----------------------+
        |  Analytics Dashboard  |         |  Responsible AI Log   |
        | - AI Agreement Rate % |         | - 6 documented errors |
        | - Excel KPI Export    |         | - Engineering lessons |
        +-----------------------+         +-----------------------+
```

1. **Deterministic Rule Validation (`rule_checker.py`):** 15 mathematical and syntactic checks using Python's `ipaddress` library (IP format, subnet boundaries, gateway containment, APIPA, VLAN mismatch, trunking CDP mismatch, ACL packet drops, interface down).
2. **Step-by-Step OSI Layer Diagnostic Ladder:** Sequentially evaluates Physical (L1) through Application (L7) layers to pinpoint the exact failure layer.
3. **Structured AI Diagnosis (`ai_diagnosis.py`):** Outputs root cause, confidence score (0–100), OSI layer, verbatim evidence citations, next verification commands, and suggested fixes. Works **100% offline in Mock Mode** (no API key required).
4. **Human Review & Responsible AI (`reviewer.py`):** Tracks reviewer decisions, calculates the **AI Agreement Rate** and **Correction Rate**, and documents 6 educational AI mistakes in `data/responsible_ai_log.csv`.
5. **Interactive CCNA / Viva Quiz Trainer:** Practice all 32 master defense questions directly in the application with revealable answers.
6. **One-Click Case Audit Report:** Export complete Markdown investigation reports for lab portfolios.

---

## 📂 Project Structure

```text
NetSage-AI/
├── app.py                      # Main 9-page interactive Streamlit dashboard
├── rule_checker.py             # 15 deterministic networking rules (ipaddress & regex)
├── ai_diagnosis.py             # AI diagnostic engine (offline Mock mode + API mode)
├── reviewer.py                 # Human review tracking & agreement rate calculations
├── data_loader.py              # Ingestion utilities for cases, reviews, and logs
├── config.py                   # Central settings, paths, and safety disclaimers
├── requirements.txt            # Lightweight project dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
│
├── data/
│   ├── cases.csv               # 32 Cisco Packet Tracer-style troubleshooting cases (10 domains)
│   ├── responsible_ai_log.csv  # 6 documented cases where AI was corrected
│   ├── reviews.csv             # Human reviewer audit records
│   └── netsage_summary_metrics.xlsx # Generated multi-sheet Excel summary
│
├── prompts/
│   ├── diagnose_prompt.md      # Master AI system prompt with 3 worked examples
│   └── helper_prompts.md       # Auxiliary prompt templates
│
├── dashboard/
│   └── dashboard.py            # Analytics charts and Excel export engine
│
├── tests/
│   ├── test_rule_checker.py    # 29 unit tests for deterministic rules
│   ├── test_system_integration.py # 5 end-to-end integration tests
│   ├── test_app_components.py  # 5 component & viva loader tests
│   └── sample_outputs.txt      # PASS / FAIL / WARNING sample outputs
│
├── docs/
│   ├── project_report.md       # 17-section formal academic project report
│   ├── demo_script.md          # Timed 10-minute presentation & video script
│   └── viva_questions.md       # 32 master CCNA viva questions & answers
│
└── screenshots/
    └── README.md               # Screenshot capture guide
```

---

## 🚀 Quick Start Guide

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone <YOUR_REPO_URL>
cd NetSage-AI

# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser. The app runs in offline **Mock Mode** by default—**no API key required!**

### 3. Run Automated Tests
```bash
python -m pytest tests/
```
*All 39 unit and integration tests pass in ~1 second.*

---

## 📋 Assignment Deliverables Checklist

| Deliverable | Location in Project | Status |
| :--- | :--- | :---: |
| **30+ Lab Cases** | `data/cases.csv` (32 realistic cases across 10 domains) | ✅ Complete |
| **Prompt Files** | `prompts/diagnose_prompt.md` with worked examples | ✅ Complete |
| **Python Checker** | `rule_checker.py` + `tests/sample_outputs.txt` | ✅ Complete |
| **Dashboard** | `dashboard/dashboard.py` + `netsage_summary_metrics.xlsx` | ✅ Complete |
| **Responsible AI Log** | `data/responsible_ai_log.csv` (6 documented AI errors) | ✅ Complete |
| **Demo Script** | `docs/demo_script.md` (Timed 0:00–10:00 video script) | ✅ Complete |
| **Project Report** | `docs/project_report.md` (17 academic sections) | ✅ Complete |
| **Viva Prep** | `docs/viva_questions.md` (32 master Q&As with trainer) | ✅ Complete |

---

## ⚙️ Operating Modes

- **🟢 MOCK MODE (Default):** Runs completely offline with zero cost. Includes 6 deliberate educational AI mistakes to demonstrate human review.
- **🔵 API MODE (Optional):** Copy `.env.example` to `.env` and set `OPENAI_API_KEY=your_key` to connect live LLMs.

---

## 🎓 Academic Presentation Tips
- Refer to [`docs/demo_script.md`](docs/demo_script.md) for the timed 10-minute presentation guide.
- Refer to [`docs/viva_questions.md`](docs/viva_questions.md) for 32 master viva questions.
- Use the **Interactive Viva Quiz Trainer** on Page 9 (`About Project`) to demonstrate exam readiness!
