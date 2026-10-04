# HisaabAgent2.0

**Your AI-powered business co-pilot for everyday decisions.**

HisaabAgent2.0 is an AI-powered business assistant built for Pakistani
micro-business owners â€” clothing shops, grocery stores, mobile accessory
stalls, home-based sellers, and small wholesalers. Instead of filling
accounting forms, the owner just describes what happened, in English or
Roman Urdu:

> "Aaj 20 shirts 1500 ki bechi aur 5000 supplier ko diye."

HisaabAgent2.0 understands it, shows what it understood for confirmation,
does the arithmetic in Python (never in the AI model), stores it, and then
uses AI to analyze the business and recommend what to do next.

---

## 1. Features

- **Dashboard** â€” KPIs, Business Health Score, AI-generated insights
- **Record Activity** â€” natural language entry (English/Roman Urdu) with a
  confirm-before-save step
- **Analytics** â€” revenue/expense trends, top products, expense breakdown
- **Inventory** â€” stock table, low-stock flags, AI restocking insights
- **Cash Flow** â€” Udhaar (receivables), supplier payables, cash flow charts
- **AI Business Advisor** â€” ask questions about your business in plain language
- **Action Plan** â€” a prioritized, reasoned daily to-do list
- **Settings** â€” business profile, low-stock threshold, demo data loader

## 2. Tech Stack

- **Python 3.10+**
- **Streamlit** â€” the entire frontend (no React/Node/PHP)
- **Google Gemini API** (`google-genai` SDK) â€” natural language understanding
  and business reasoning only
- **SQLite** â€” local, file-based database
- **Pandas** â€” tabular data handling
- **Plotly** â€” charts

Python handles every calculation (revenue, COGS, profit, margin, health
score). Gemini is never asked to do arithmetic â€” see Section 9 below.

## 3. Project Structure

```
HisaabAgent2.0/
â”œâ”€â”€ app.py                    # entry point: sidebar + page router only
â”œâ”€â”€ config.py                 # model name, currency, thresholds, colors
â”‚
â”œâ”€â”€ database/
â”‚   â”œâ”€â”€ db.py                 # connection + init_db()
â”‚   â”œâ”€â”€ schema.py              # CREATE TABLE statements
â”‚   â””â”€â”€ queries.py             # all raw SQL, one function per operation
â”‚
â”œâ”€â”€ ai/
â”‚   â”œâ”€â”€ gemini_client.py       # single wrapped Gemini client
â”‚   â”œâ”€â”€ schemas.py             # JSON response schemas
â”‚   â”œâ”€â”€ prompts.py             # every prompt template
â”‚   â”œâ”€â”€ extraction.py          # NL -> structured transaction JSON
â”‚   â”œâ”€â”€ finance_agent.py
â”‚   â”œâ”€â”€ inventory_agent.py
â”‚   â”œâ”€â”€ cashflow_agent.py
â”‚   â””â”€â”€ advisor_agent.py       # combines the three + generates Action Plan
â”‚
â”œâ”€â”€ services/
â”‚   â”œâ”€â”€ calculations.py        # pure financial math - the only place it happens
â”‚   â”œâ”€â”€ health_score.py        # deterministic Business Health Score
â”‚   â”œâ”€â”€ transaction_service.py # validates + commits confirmed extractions
â”‚   â”œâ”€â”€ inventory_service.py   # stock status logic
â”‚   â””â”€â”€ analytics_service.py   # aggregations + AI context builders
â”‚
â”œâ”€â”€ views/                     # one file per sidebar page
â”‚   â”œâ”€â”€ dashboard.py
â”‚   â”œâ”€â”€ record_activity.py
â”‚   â”œâ”€â”€ analytics.py
â”‚   â”œâ”€â”€ inventory.py
â”‚   â”œâ”€â”€ cashflow.py
â”‚   â”œâ”€â”€ advisor.py
â”‚   â”œâ”€â”€ action_plan.py
â”‚   â””â”€â”€ settings.py
â”‚
â”œâ”€â”€ ui/
â”‚   â”œâ”€â”€ styles.py               # dark green theme CSS
â”‚   â”œâ”€â”€ components.py           # KPI cards, badges, insight cards, etc.
â”‚   â””â”€â”€ charts.py                # Plotly figure builders
â”‚
â”œâ”€â”€ demo/
â”‚   â””â”€â”€ demo_data.py            # "Ahmed Garments" sample dataset
â”‚
â”œâ”€â”€ utils/
â”‚   â”œâ”€â”€ validators.py            # AI-output validation before DB writes
â”‚   â””â”€â”€ helpers.py                # currency/date formatting
â”‚
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ .env.example
â”œâ”€â”€ .streamlit/secrets.toml.example
â”œâ”€â”€ .gitignore
â””â”€â”€ README.md
```

## 4. Installation (Local)

**Requirements:** Python 3.10 or newer.

```bash
# 1. Clone or download the project, then move into it
cd HisaabAgent2.0

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

On first run, the app creates `HisaabAgent2.0.db` (SQLite) automatically â€”
no manual database setup needed.

**To see the app fully populated immediately:** go to Settings â†’
"Load Demo Business". This loads a realistic clothing-shop dataset
("Ahmed Garments") with two weeks of sales, an outstanding receivable, a
supplier payable, and a low-stock product.

## 7. Streamlit Community Cloud Deployment

1. Push this project to a GitHub repository (`.env` and `secrets.toml`
   will not be included, since they're gitignored).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new
   app pointing at your repo, with `app.py` as the entry point.
3. In the app's **Settings â†’ Secrets**, paste:

   ```toml
   [gemini]
   api_key = "your_actual_gemini_api_key"
   ```

4. Deploy. The app reads the key via `st.secrets["gemini"]["api_key"]`
   automatically â€” no code changes needed between local and deployed runs.

## 8. Secrets Configuration Summary

| Environment | Where the key lives | How it's read |
|---|---|---|
| Local dev | `GEMINI_API_KEY` environment variable | `os.environ.get(...)` |
| Streamlit Cloud | App Secrets (`[gemini] api_key = "..."`) | `st.secrets["gemini"]["api_key"]` |

`ai/gemini_client.py` checks the environment variable first, then falls
back to Streamlit secrets, so the same code runs in both places.

## 9. Architecture: Why Python Calculates and Gemini Reasons

This is the core design rule of HisaabAgent2.0:

```
HUMAN LANGUAGE â†’ GEMINI UNDERSTANDS â†’ STRUCTURED DATA â†’
PYTHON VALIDATES + CALCULATES â†’ DATABASE â†’ AI ANALYZES â†’ RECOMMENDATIONS
```

**Gemini is responsible for:** understanding messy natural language
(English/Roman Urdu/Urdu), extracting entities (product, quantity, price,
customer, supplier), and reasoning over already-correct numbers to produce
insights, explanations, and recommendations.

**Python is responsible for:** every arithmetic operation â€” revenue,
COGS, profit, margin, inventory value, cash flow, and the Business Health
Score. Gemini's extracted `quantity` and `unit_price` are multiplied in
`services/calculations.py`; Gemini's own `total_amount` guess (if any) is
discarded and recomputed.

**Why:** LLMs are unreliable at consistent arithmetic and can silently
drift on edge cases (rounding, missing fields, adversarial phrasing).
A business ledger cannot tolerate that. Keeping arithmetic in
deterministic, testable Python functions means every number in the app is
auditable and reproducible â€” a judge (or an actual business owner) can
verify `20 Ã— 1500 = 30,000` in the code, not trust it disappeared into a
model's internal reasoning.

The Business Health Score follows the same rule: `services/health_score.py`
computes all four sub-scores and the overall score with plain arithmetic.
Gemini only ever receives the finished numbers and writes a sentence
explaining them â€” it is never asked to invent or adjust the score itself.

## 10. AI Agent Architecture

```
                     HisaabAgent2.0
                          â”‚
                    AI ORCHESTRATOR
                          â”‚
           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
           â”‚              â”‚              â”‚
           â–¼              â–¼              â–¼
       Finance        Inventory      Cash Flow
        Agent           Agent          Agent
           â”‚              â”‚              â”‚
           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                          â–¼
                   Business Advisor
                          â”‚
                          â–¼
                     Action Plan
```

Each agent (`ai/finance_agent.py`, `ai/inventory_agent.py`,
`ai/cashflow_agent.py`) has exactly one job: take a small, pre-computed
context dict from `services/analytics_service.py` (never raw database
access, and never the whole database â€” see Section 53 of the original
brief) and return a short, data-grounded insight. `ai/advisor_agent.py` is
the only agent that takes the *other agents' outputs* as input, combining
them into a synthesized recommendation or a prioritized Action Plan.

Every analysis prompt in `ai/prompts.py` includes the same
anti-hallucination instruction: state only what the data supports, and
say "not enough data" rather than inventing a trend.

## 11. Demo Flow (for a hackathon presentation)

1. Open **Dashboard** â€” show Revenue, Expenses, Profit, Health Score.
2. Go to **Record Activity**, type:
   *"Aaj 20 shirts 1500 ki bechi, 5000 supplier ko diye aur Ali se 3000 lene hain."*
3. Click **Analyze Activity** â€” Gemini extracts the sale, payable, and receivable.
4. Review the confirmation card, click **Confirm & Save**.
5. Return to **Dashboard** â€” the KPIs and Health Score update immediately.
6. Go to **AI Business Advisor**, click **Analyze My Business**.
7. Go to **Action Plan** to see the prioritized recommendations.
8. Ask a question: *"Mera business kaisa perform kar raha hai?"*

## 12. Known Limitations / Future Improvements

- No multi-user auth â€” this is a single-business MVP by design.
- No offline queue for AI calls; a failed Gemini call surfaces a friendly
  retry message rather than being queued.
- Custom date-range analytics filtering was deliberately cut from this MVP
  (see project scope review) in favor of fixed periods (Today/7d/30d/Month).
- Currency is fixed to PKR; multi-currency support would require rework of
  `config.py` and every formatting call site.
- Editing an already-confirmed transaction isn't supported yet â€” only
  adding new ones and recording payments against receivables/payables.
- The Action Plan is regenerated on demand rather than scheduled/cached;
  a production version would likely cache it per-day to reduce API calls.

---

**Disclaimer:** HisaabAgent2.0 provides AI-generated business insights and
decision support. It is not a professional accountant or financial
advisor. Verify important financial decisions independently.

