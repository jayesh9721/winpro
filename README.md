# ⚡ CampaignIQ — AI Campaign Intelligence Platform
### MATRIX Hackathon 2026 · LS Digital Group · Tata Group

CampaignIQ turns raw campaign-performance exports into an AI-generated executive brief, anomaly report, budget recommendations, a market-aware forecast, competitive benchmarking, creative copy, and a conversational analyst — personalized per client, with saved history and PDF export.

---

## 🚀 Setup

### 1. Install dependencies
```bash
cd campaigniq
pip install -r requirements.txt
```

### 2. Configure API keys
Create/edit `.env` in the project root:
```bash
# Claude — powers every AI section except the Gemini Market Forecast. Either works;
# ANTHROPIC_API_KEY is preferred and tried first.
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-v1-...

# OPENROUTER_API_KEY is also required for the Gemini Market Forecast (Forecast tab) —
# it's used independently of the Claude fallback above, via OpenRouter's Gemini models.

# Supabase — only needed if you want login, business profiles, and saved report history
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```
If the Supabase variables are left out, the app runs with no login, no profiles, and no History — everything else still works against a single anonymous session.

### 3. (Once) Set up Supabase
Run these, in order, in your Supabase project's **SQL Editor** (Dashboard → SQL Editor → paste → Run). API keys alone can't apply these — they need the SQL Editor:
1. [supabase_schema.sql](supabase_schema.sql) — creates `analysis_history` (saved reports), with row-level security so each user only sees their own.
2. [supabase_schema_profiles.sql](supabase_schema_profiles.sql) — creates `business_profiles` (the client-persona system) and links `analysis_history` to a profile.
3. [supabase_schema_chat.sql](supabase_schema_chat.sql) — adds a `chat_transcript` column to `analysis_history` so saved reports include the AI chat too.

### 4. Launch
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your browser. The dark theme (`.streamlit/config.toml`) is already configured — no extra setup needed.

---

## 🔐 Login & session persistence

If Supabase is configured, the app opens on a **Log In / Sign Up** screen (email + password). Once logged in, the session survives a browser refresh — Supabase's access/refresh tokens are saved in a browser cookie and silently restored on load, so you're not asked to log in again every time the page reloads. Logging out clears both the session and the cookie.

---

## 🏢 Business Profiles (client personas)

Every login starts at a **profile picker**. Each profile represents one client and keeps its data, AI cache, chat history, and personalization completely separate from every other profile:

- **Create a profile**: Name, Description, one or more **Goals** (Leads, Awareness, Traffic, Sales/ROAS, Engagement — multi-select), Target (e.g. "CPL ≤ ₹500"), Industry, Monthly Budget.
- On creation, Claude generates a **bespoke system prompt** for that client — defining what "success" means for their specific goal(s), which metrics matter, and how to frame recommendations. This prompt personalizes every AI section for that client (Brief, Anomalies, Recommendations, Forecast, Creative AI, Benchmark, Chat).
- **✏️ Edit** (sidebar) re-opens the profile's inputs, lets you change any field and regenerate (or hand-edit) its system prompt.
- **🔀 Switch** returns to the profile picker — the active profile's data/cache/chat reset cleanly on switch.

---

## 📁 Your data

Upload a **CSV or Excel** file via the sidebar. If it already has these exact columns, it loads instantly:
```
campaign_name, channel, brand, budget, spend, impressions, clicks, conversions, revenue, ctr, cpc, roas, status
```
Any other format works too — an AI-assisted column mapper reads your headers and sample rows, suggests a mapping to the fields above, and lets you confirm or fix it before anything is applied.

An optional `date` column (per-row date, as exported by GA4/Google Ads/Meta/Bing) is auto-detected if present — it unlocks year-over-year comparison in the Forecast tab. Its absence doesn't affect anything else.

A sample file, [sample_test_data.csv](sample_test_data.csv), is included for testing.

---

## 🧭 Sidebar controls

| Control | What it does |
|---|---|
| **CSV/Excel upload** | Loads your campaign data (re-uploading a genuinely new file resets the AI cache) |
| **AI status** | Shows whether a Claude key is connected |
| **Active profile card** | Shows the current client + goal(s)/industry, with ✏️ Edit and 🔀 Switch |
| **Filters** | Brand, Platform (multi-select), Status — applied globally, on top of which each tab layers its own platform filter |
| **Regenerate AI** | Clears the AI cache so every section regenerates fresh |
| **Log Out** | Ends your session and clears the persistence cookie |

---

## 🌟 Features by tab

| Tab | What it does |
|---|---|
| 🤖 **AI Brief** | Portfolio health score + AI executive brief: portfolio health, wins, and 2 urgent actions |
| 📈 **Performance** | 7 interactive charts — spend vs revenue, ROAS by campaign, budget by campaign (top 12), CTR vs CPC, CPA by channel, and a full conversion funnel |
| 🚨 **Anomalies** | Auto-flags campaigns with ROAS < 1.0x or under-performing CTR/budget, with an AI root-cause analysis and a rescue plan for the worst performer |
| 💡 **Recommendations** | 5 numbered AI budget-reallocation recommendations with real ₹ amounts, plus a channel efficiency matrix chart |
| 🔮 **Forecast** | Two forecasts in one tab — see [below](#-forecast-tab-in-depth) |
| 🎨 **Creative AI** | Per-campaign AI generation: ad copy variations, audience targeting refinements, or creative format recommendations |
| 🏁 **Benchmark** | AI comparison of your ROAS/CTR/CPC against Indian industry benchmarks by sector |
| 💬 **AI Chat** | Free-form Q&A about your campaign data, with 6 one-click starter questions |
| 🕘 **History** | *(requires login)* Every saved report, with its own platform filter and one-click PDF re-download — available even before you upload any data |

Every AI section is **click-to-generate**: nothing calls the AI automatically on load or on filter changes — you always press "⚡ Generate …" explicitly, and the result is cached per platform-filter combination so revisiting a filter you've already generated is instant.

Every tab (including History) runs as its own isolated Streamlit fragment — clicking "Generate" in one tab only re-renders that tab, not the whole page. Nothing elsewhere flashes, reloads, or appears to regenerate.

---

## 🔮 Forecast tab in depth

**1. 30-Day Revenue Forecast (Claude)** — adjust next-period budget and channel mix with sliders; see deterministic projected Revenue, Profit, **Conversions**, and **Cost/Conversion** (all computed from your historical per-channel ROAS/CPA, not guessed), plus an AI read on whether the mix is optimal.

**2. 🌐 Gemini Market Forecast** — a second, independent forecast powered by Google Gemini (via OpenRouter), built from your own "Universal AI Campaign Forecaster" template:
- **Market and Competitor Trends** — recommends the target audience for the client's service, analyzes keyword quality score/rank/landing-page experience, breaks down impression share lost to rank vs. lost to budget (and how to recover it), and covers competitor performance — all grounded in your uploaded reports below where available.
- **KPI Predictions** — presents the Python-calculated projection (not an AI guess) compared against your historical numbers.
- **Past Wins and Losses** — uses year-over-year data if your file has a `date` column spanning 2+ years (same day-of-year window, for a fair comparison).
- **Seasonal Pivot and Campaign Adjustments** — backup plan if a product/service is expected to dip seasonally.

Three **optional** supplementary uploads (each with its own AI column-mapper) sharpen this forecast further — leave any of them out and Gemini is told plainly not to invent numbers for that part:
- **Keyword report** — Keyword, Avg. position, Quality Score, Landing page experience, Impr./Clicks/Cost/Conversions.
- **Impression share report** — Impr. share, Impr. share lost (rank), Impr. share lost (budget), and optional competitor overlap/outranking rows (Google Ads auction-insights style).
- **Audience report** — Segment/Age/Gender/Device performance, used to recommend which audience to prioritize.

Add free-text **market context** (e.g. an upcoming promo or a competitor launch) to factor into the forecast.

---

## 🎯 Platform filtering

Every tab has its **own** "Platform filter" (Meta Ads, Google Ads, YouTube, Instagram, etc.), independent of every other tab — narrowing Recommendations to Google Ads doesn't affect what Forecast shows. This sits on top of the global Platform filter in the sidebar. AI text is cached per platform combination per tab, so switching between filter selections you've already viewed is instant.

---

## 💾 Saving & revisiting reports (History)

Right after the KPI row, "💾 Save Session to History" stores a full snapshot to Supabase — your campaign data, every generated AI section (with "All platforms" selected), and the AI chat transcript. The **History** tab (accessible even before uploading any data) lists every saved report per active profile, each with:
- **📄 Prepare PDF → ⬇ Download PDF** — a branded PDF with KPI summary, all AI sections (rendered from Markdown, not raw `##`/`**`), the chat transcript, and the full campaign data table.
- **👁 View full report** — expands every saved AI section and the chat inline, without needing to download anything.

---

## 🔑 Getting API keys

- **Claude**: https://console.anthropic.com → API Keys → Create Key → add as `ANTHROPIC_API_KEY`.
- **Gemini (via OpenRouter)**: https://openrouter.ai → Keys → Create Key → add as `OPENROUTER_API_KEY`. (Also used as a Claude fallback if `ANTHROPIC_API_KEY` is absent.) Note: some OpenRouter accounts have a data-policy setting that blocks all model calls with a 404 — check Settings → Privacy on openrouter.ai if you get errors.
- **Supabase**: https://supabase.com → your project → Settings → API, for the URL/anon key/service-role key.

---

*CampaignIQ · Built for MATRIX Hackathon 2026 · Powered by Anthropic Claude & Google Gemini*
