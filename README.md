# HisaabAgent

**Your AI-powered business co-pilot for everyday decisions.**

HisaabAgent is an AI-powered business assistant built for Pakistani
micro-business owners — clothing shops, grocery stores, mobile accessory
stalls, home-based sellers, and small wholesalers. Instead of filling
accounting forms, the owner just describes what happened, in English or
Roman Urdu:

> "Aaj 20 shirts 1500 ki bechi aur 5000 supplier ko diye."

HisaabAgent understands it, shows what it understood for confirmation,
does the arithmetic in Python (never in the AI model), stores it, and then
uses AI to analyze the business and recommend what to do next.

---

## 1. Features

- **Dashboard** — KPIs, Business Health Score, AI-generated insights
- **Record Activity** — natural language entry (English/Roman Urdu) with a
  confirm-before-save step
- **Analytics** — revenue/expense trends, top products, expense breakdown
- **Inventory** — stock table, low-stock flags, AI restocking insights
- **Cash Flow** — Udhaar (receivables), supplier payables, cash flow charts
- **AI Business Advisor** — ask questions about your business in plain language
- **Action Plan** — a prioritized, reasoned daily to-do list
- **Settings** — business profile, low-stock threshold, demo data loader

## 2. Tech Stack

- **Python 3.10+**
- **Streamlit** — the entire frontend (no React/Node/PHP)
- **Google Gemini API** (`google-genai` SDK) — natural language understanding
  and business reasoning only
- **SQLite** — local, file-based database
- **Pandas** — tabular data handling
- **Plotly** — charts

Python handles every calculation (revenue, COGS, profit, margin, health
score). Gemini is never asked to do arithmetic — see Section 9 below.

## 3. Project Structure

```
hisaabagent/
├── app.py                    # entry point: sidebar + page router only
├── config.py                 # model name, currency, thresholds, colors
│
├── database/
│   ├── db.py                 # connection + init_db()
│   ├── schema.py              # CREATE TABLE statements
│   └── queries.py             # all raw SQL, one function per operation
│
├── ai/
│   ├── gemini_client.py       # single wrapped Gemini client
│   ├── schemas.py             # JSON response schemas
│   ├── prompts.py             # every prompt template
│   ├── extraction.py          # NL -> structured transaction JSON
│   ├── finance_agent.py
│   ├── inventory_agent.py
│   ├── cashflow_agent.py
│   └── advisor_agent.py       # combines the three + generates Action Plan
│
├── services/
│   ├── calculations.py        # pure financial math - the only place it happens
│   ├── health_score.py        # deterministic Business Health Score
│   ├── transaction_service.py # validates + commits confirmed extractions
│   ├── inventory_service.py   # stock status logic
│   └── analytics_service.py   # aggregations + AI context builders
│
├── views/                     # one file per sidebar page
│   ├── dashboard.py
│   ├── record_activity.py
│   ├── analytics.py
│   ├── inventory.py
│   ├── cashflow.py
│   ├── advisor.py
│   ├── action_plan.py
│   └── settings.py
│
├── ui/
│   ├── styles.py               # dark green theme CSS
│   ├── components.py           # KPI cards, badges, insight cards, etc.
│   └── charts.py                # Plotly figure builders
│
├── demo/
│   └── demo_data.py            # "Ahmed Garments" sample dataset
│
├── utils/
│   ├── validators.py            # AI-output validation before DB writes
│   └── helpers.py                # currency/date formatting
│
├── requirements.txt
├── .env.example
├── .streamlit/secrets.toml.example
├── .gitignore
└── README.md
```

## 4. Installation (Local)

**Requirements:** Python 3.10 or newer.

```bash
# 1. Clone or download the project, then move into it
cd hisaabagent

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 5. Gemini API Setup

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. **For local development**, set it as an environment variable:

   ```bash
   export GEMINI_API_KEY=your_key_here      # macOS/Linux
   set GEMINI_API_KEY=your_key_here         # Windows (cmd)
   ```

   Or copy `.env.example` to `.env` and load it with your shell/tooling of choice.

3. **Never** commit your real API key. `.env` and `.streamlit/secrets.toml`
   are already in `.gitignore`.

## 6. Running Locally

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

On first run, the app creates `hisaabagent.db` (SQLite) automatically —
no manual database setup needed.

**To see the app fully populated immediately:** go to Settings →
"Load Demo Business". This loads a realistic clothing-shop dataset
("Ahmed Garments") with two weeks of sales, an outstanding receivable, a
supplier payable, and a low-stock product.

## 7. Streamlit Community Cloud Deployment

1. Push this project to a GitHub repository (`.env` and `secrets.toml`
   will not be included, since they're gitignored).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new
   app pointing at your repo, with `app.py` as the entry point.
3. In the app's **Settings → Secrets**, paste:

   ```toml
   [gemini]
   api_key = "your_actual_gemini_api_key"
   ```

4. Deploy. The app reads the key via `st.secrets["gemini"]["api_key"]`
   automatically — no code changes needed between local and deployed runs.

## 8. Secrets Configuration Summary

| Environment | Where the key lives | How it's read |
|---|---|---|
| Local dev | `GEMINI_API_KEY` environment variable | `os.environ.get(...)` |
| Streamlit Cloud | App Secrets (`[gemini] api_key = "..."`) | `st.secrets["gemini"]["api_key"]` |

`ai/gemini_client.py` checks the environment variable first, then falls
back to Streamlit secrets, so the same code runs in both places.

## 9. Architecture: Why Python Calculates and Gemini Reasons

This is the core design rule of HisaabAgent:

```
HUMAN LANGUAGE → GEMINI UNDERSTANDS → STRUCTURED DATA →
PYTHON VALIDATES + CALCULATES → DATABASE → AI ANALYZES → RECOMMENDATIONS
```

**Gemini is responsible for:** understanding messy natural language
(English/Roman Urdu/Urdu), extracting entities (product, quantity, price,
customer, supplier), and reasoning over already-correct numbers to produce
insights, explanations, and recommendations.

**Python is responsible for:** every arithmetic operation — revenue,
COGS, profit, margin, inventory value, cash flow, and the Business Health
Score. Gemini's extracted `quantity` and `unit_price` are multiplied in
`services/calculations.py`; Gemini's own `total_amount` guess (if any) is
discarded and recomputed.

**Why:** LLMs are unreliable at consistent arithmetic and can silently
drift on edge cases (rounding, missing fields, adversarial phrasing).
A business ledger cannot tolerate that. Keeping arithmetic in
deterministic, testable Python functions means every number in the app is
auditable and reproducible — a judge (or an actual business owner) can
verify `20 × 1500 = 30,000` in the code, not trust it disappeared into a
model's internal reasoning.

The Business Health Score follows the same rule: `services/health_score.py`
computes all four sub-scores and the overall score with plain arithmetic.
Gemini only ever receives the finished numbers and writes a sentence
explaining them — it is never asked to invent or adjust the score itself.

## 10. AI Agent Architecture

```
                     HISAABAGENT
                          │
                    AI ORCHESTRATOR
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
       Finance        Inventory      Cash Flow
        Agent           Agent          Agent
           │              │              │
           └──────────────┼──────────────┘
                          ▼
                   Business Advisor
                          │
                          ▼
                     Action Plan
```

Each agent (`ai/finance_agent.py`, `ai/inventory_agent.py`,
`ai/cashflow_agent.py`) has exactly one job: take a small, pre-computed
context dict from `services/analytics_service.py` (never raw database
access, and never the whole database — see Section 53 of the original
brief) and return a short, data-grounded insight. `ai/advisor_agent.py` is
the only agent that takes the *other agents' outputs* as input, combining
them into a synthesized recommendation or a prioritized Action Plan.

Every analysis prompt in `ai/prompts.py` includes the same
anti-hallucination instruction: state only what the data supports, and
say "not enough data" rather than inventing a trend.

## 11. Demo Flow (for a hackathon presentation)

1. Open **Dashboard** — show Revenue, Expenses, Profit, Health Score.
2. Go to **Record Activity**, type:
   *"Aaj 20 shirts 1500 ki bechi, 5000 supplier ko diye aur Ali se 3000 lene hain."*
3. Click **Analyze Activity** — Gemini extracts the sale, payable, and receivable.
4. Review the confirmation card, click **Confirm & Save**.
5. Return to **Dashboard** — the KPIs and Health Score update immediately.
6. Go to **AI Business Advisor**, click **Analyze My Business**.
7. Go to **Action Plan** to see the prioritized recommendations.
8. Ask a question: *"Mera business kaisa perform kar raha hai?"*

## 12. Known Limitations / Future Improvements

- No multi-user auth — this is a single-business MVP by design.
- No offline queue for AI calls; a failed Gemini call surfaces a friendly
  retry message rather than being queued.
- Custom date-range analytics filtering was deliberately cut from this MVP
  (see project scope review) in favor of fixed periods (Today/7d/30d/Month).
- Currency is fixed to PKR; multi-currency support would require rework of
  `config.py` and every formatting call site.
- Editing an already-confirmed transaction isn't supported yet — only
  adding new ones and recording payments against receivables/payables.
- The Action Plan is regenerated on demand rather than scheduled/cached;
  a production version would likely cache it per-day to reduce API calls.

---

**Disclaimer:** HisaabAgent provides AI-generated business insights and
decision support. It is not a professional accountant or financial
advisor. Verify important financial decisions independently.
