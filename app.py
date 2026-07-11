import truststore
truststore.inject_into_ssl()  # use the OS certificate store — fixes SSL verify failures behind corporate proxies

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import json, os, io, math, re
from datetime import datetime
from fpdf import FPDF
from dotenv import load_dotenv
from supabase import create_client
from streamlit_cookies_controller import CookieController
from streamlit.errors import StreamlitAPIException

load_dotenv()

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CampaignIQ · MATRIX Hackathon",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased;}
#MainMenu,footer,header{visibility:hidden;}
.stApp{background:linear-gradient(160deg,#0F172A 0%,#1E293B 100%);background-attachment:fixed;}
.block-container{padding-top:1.25rem;padding-bottom:2.5rem;max-width:1200px;}
[class*="css"]{color:#E2E8F0;}

.navbar{
  background:rgba(30,41,59,.65);backdrop-filter:blur(8px);
  border-radius:18px;padding:1.25rem 1.75rem;margin-bottom:1.5rem;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;
  border:1px solid rgba(99,102,241,.2);box-shadow:0 4px 24px rgba(0,0,0,.25);}
.nb-brand{font-size:22px;font-weight:800;color:#F1F5F9;letter-spacing:-.03em;}
.nb-brand span{color:#6366F1;}
.nb-sub{font-size:12px;color:#94A3B8;margin-top:3px;font-weight:500;}
.nb-badges{display:flex;gap:8px;flex-wrap:wrap;}
.badge{background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.35);color:#A5B4FC;
  font-size:11.5px;font-weight:600;padding:5px 14px;border-radius:20px;letter-spacing:.02em;}
.badge.g{background:rgba(16,185,129,.15);border-color:rgba(16,185,129,.35);color:#6EE7B7;}
.badge.r{background:rgba(239,68,68,.15);border-color:rgba(239,68,68,.35);color:#FCA5A5;}
.badge.y{background:rgba(245,158,11,.15);border-color:rgba(245,158,11,.35);color:#FCD34D;}

.kcard{background:rgba(30,41,59,.65);border:1px solid rgba(99,102,241,.18);
  border-radius:16px;padding:1.15rem 1.25rem;transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease;
  box-shadow:0 1px 2px rgba(0,0,0,.15);
  min-height:132px;display:flex;flex-direction:column;justify-content:flex-start;}
.kcard:hover{transform:translateY(-2px);border-color:rgba(99,102,241,.4);
  box-shadow:0 12px 24px -8px rgba(0,0,0,.4),0 0 0 1px rgba(99,102,241,.15);}
.klabel{font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:.05em;
  margin-bottom:8px;line-height:1.35;min-height:2.7em;display:flex;align-items:flex-start;}
.kval{font-size:24px;font-weight:800;color:#F1F5F9;line-height:1.15;letter-spacing:-.02em;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.kdelta{font-size:12px;margin-top:6px;font-weight:600;}
.up{color:#10B981;}.down{color:#EF4444;}.neu{color:#64748B;}

.sh{font-size:14.5px;font-weight:700;color:#F1F5F9;margin:1.75rem 0 1rem;display:flex;align-items:center;gap:8px;
  letter-spacing:-.01em;}
.sh::after{content:'';flex:1;height:1px;background:rgba(99,102,241,.2);margin-left:8px;}

.aibox{background:rgba(30,41,59,.65);border:1px solid rgba(6,182,212,.25);border-left:3px solid #06B6D4;
  border-radius:16px;padding:1.35rem 1.6rem;margin-bottom:1rem;box-shadow:0 1px 2px rgba(0,0,0,.15);}
.aihdr{display:flex;align-items:center;gap:8px;margin-bottom:12px;font-size:11.5px;font-weight:700;
  color:#22D3EE;text-transform:uppercase;letter-spacing:.06em;}
.aibody{font-size:13.5px;color:#CBD5E1;line-height:1.8;}
.aibody p{margin:.5em 0;}
.aibody ul,.aibody ol{margin:.3em 0;padding-left:1.3em;}
.aibody li{margin-bottom:.4em;}
.aibody p:first-child{margin-top:0;}
.aibody p:last-child{margin-bottom:0;}
.aibody strong{color:#F1F5F9;}

.ab-h{background:rgba(239,68,68,.15);color:#FCA5A5;border:1px solid rgba(239,68,68,.35);
  padding:3px 11px;border-radius:20px;font-size:11px;font-weight:700;}
.ab-m{background:rgba(245,158,11,.15);color:#FCD34D;border:1px solid rgba(245,158,11,.35);
  padding:3px 11px;border-radius:20px;font-size:11px;font-weight:700;}
.ab-o{background:rgba(16,185,129,.15);color:#6EE7B7;border:1px solid rgba(16,185,129,.35);
  padding:3px 11px;border-radius:20px;font-size:11px;font-weight:700;}

.div{height:1px;background:rgba(99,102,241,.18);margin:1.75rem 0;}

section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0F172A 0%,#1E293B 100%);
  border-right:1px solid rgba(99,102,241,.15);}

.stButton>button{
  background:#6366F1;color:#fff;border:none;
  border-radius:10px;font-weight:700;font-size:13.5px;padding:.6rem 1.5rem;transition:all .15s ease;
  box-shadow:0 1px 2px rgba(99,102,241,.2);}
.stButton>button:hover{background:#4F46E5;transform:translateY(-1px);box-shadow:0 6px 20px rgba(99,102,241,.4);}
.stButton>button:active{transform:translateY(0);}

div[data-testid="stExpander"]{
  border:1px solid rgba(99,102,241,.18);border-radius:14px;background:rgba(30,41,59,.65);
  box-shadow:0 1px 2px rgba(0,0,0,.15);overflow:hidden;}
div[data-testid="stExpander"] summary{font-weight:600;color:#E2E8F0;}

.score-ring{display:inline-flex;align-items:center;justify-content:center;
  width:90px;height:90px;border-radius:50%;font-size:28px;font-weight:800;}

/* Native widgets — Streamlit's theme.toml covers the base colors; these round out
   the pieces that stay stubbornly light (file uploader chip, captions, tab bar). */
[data-testid="stFileUploaderDropzone"]{
  background:rgba(30,41,59,.5);border:1px dashed rgba(99,102,241,.35);border-radius:14px;}
[data-testid="stFileUploaderFile"]{background:transparent;color:#E2E8F0;}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small{color:#94A3B8;}

div[data-baseweb="select"] > div{
  background:rgba(15,23,42,.55) !important;border-color:rgba(99,102,241,.3) !important;}
div[data-baseweb="tag"]{background:rgba(99,102,241,.25) !important;}

[data-testid="stCaptionContainer"], .stCaption, small{color:#64748B !important;}

[data-testid="stTabs"] button[data-baseweb="tab"]{color:#94A3B8;font-weight:600;}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"]{color:#F1F5F9;}
[data-testid="stTabs"] div[data-baseweb="tab-highlight"]{background-color:#6366F1;}
[data-testid="stTabs"] div[data-baseweb="tab-border"]{background:rgba(99,102,241,.15);}

textarea, input[type="text"], input[type="password"], input[type="number"]{
  background:rgba(15,23,42,.55) !important;color:#E2E8F0 !important;
  border-color:rgba(99,102,241,.3) !important;}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]{background:rgba(15,23,42,.6);}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,.4)",
    font_color="#94A3B8", font_family="Inter",
    colorway=["#6366F1","#06B6D4","#10B981","#F59E0B","#EF4444","#818CF8","#67E8F9","#A78BFA"],
)

def inr(v):
    if v >= 1_00_00_000: return f"₹{v/1_00_00_000:.2f}Cr"
    if v >= 1_00_000:    return f"₹{v/1_00_000:.1f}L"
    return f"₹{v:,.0f}"

def num(v):
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return str(int(v))

AI_MODEL = "anthropic/claude-sonnet-5"

def get_client():
    global AI_MODEL
    ak = os.getenv("ANTHROPIC_API_KEY","").strip()
    if ak:
        AI_MODEL = "claude-sonnet-4-5"
        return OpenAI(api_key=ak, base_url="https://api.anthropic.com/v1/")
    ok = os.getenv("OPENROUTER_API_KEY","").strip()
    if ok:
        AI_MODEL = "anthropic/claude-sonnet-5"
        return OpenAI(api_key=ok, base_url="https://openrouter.ai/api/v1")
    return None

GEMINI_MODEL = "google/gemini-2.5-flash"

def get_gemini_client():
    """Separate OpenRouter-backed client used only for the Gemini market forecast —
    independent of get_client()/AI_MODEL, which stay on Claude for every other section."""
    key = os.getenv("OPENROUTER_API_KEY","").strip()
    return OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1") if key else None

def load_csv(up):
    return pd.read_csv(up)

# ──────────────────────────────────────────────────────────────
# UNIVERSAL CSV MAPPING (AI-assisted)
# ──────────────────────────────────────────────────────────────
CANONICAL_FIELDS = ["campaign_name","channel","brand","budget","spend","impressions",
                     "clicks","conversions","revenue","ctr","cpc","roas","status"]
OPTIONAL_FIELDS  = ["date"]
REQUIRED_FIELDS  = ["campaign_name","channel","spend","revenue"]

def ai_map_columns(client, headers, sample_rows, fields=None, optional_fields=None):
    fields = fields if fields is not None else CANONICAL_FIELDS
    optional_fields = optional_fields if optional_fields is not None else (OPTIONAL_FIELDS if fields is CANONICAL_FIELDS else [])
    all_fields = fields + optional_fields
    prompt = f"""You're normalizing a marketing report CSV/Excel so it can be analyzed automatically.

COLUMN HEADERS: {json.dumps(headers)}
SAMPLE ROWS: {json.dumps(sample_rows, default=str)}

Map each of these fields to the single best-matching header above, or null if there's no reasonable match:
{json.dumps(all_fields)}

{f"These fields are optional — map them only if the file actually has an equivalent column: {json.dumps(optional_fields)}" if optional_fields else ""}

Respond with ONLY a JSON object mapping field -> header (or null), no other text, no markdown fence."""
    resp = client.chat.completions.create(model=AI_MODEL, max_tokens=400,
        messages=[{"role":"user","content":prompt}])
    text = re.sub(r"^```(json)?|```$", "", resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
    mapping = json.loads(text)
    return {f: mapping.get(f) for f in all_fields}

def load_any(upload):
    name = upload.name.lower()
    return pd.read_excel(upload) if name.endswith((".xlsx",".xls")) else pd.read_csv(upload)

def map_report_df(raw_df, mapping, numeric_fields=()):
    """Lightweight select+rename+coerce for supplementary reports (keyword/impression-share/
    audience) — unlike build_canonical_df, no derived-metric logic since each report's shape differs."""
    df = pd.DataFrame(index=raw_df.index)
    for field, col in mapping.items():
        if col and col in raw_df.columns:
            df[field] = raw_df[col]
    for c in numeric_fields:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def optional_report_upload(label, caption, session_key, fields, numeric_fields, client):
    """Click-to-map optional supplementary report uploader — used for keyword/impression-share/
    audience reports in the Forecast tab. Returns the mapped DataFrame, or None if nothing usable."""
    st.caption(caption)
    up = st.file_uploader(label, type=["csv","xlsx","xls"], key=f"{session_key}_uploader")
    if up is not None:
        sig = (up.name, up.size)
        if st.session_state.get(f"{session_key}_sig") != sig:
            st.session_state[f"{session_key}_sig"] = sig
            try:
                raw = load_any(up)
                if client:
                    mapping = ai_map_columns(client, raw.columns.tolist(), raw.head(3).to_dict("records"),
                                              fields=fields, optional_fields=[])
                    mapped = map_report_df(raw, mapping, numeric_fields)
                    mapped = mapped.dropna(axis=1, how="all")
                    st.session_state[session_key] = mapped if len(mapped.columns) else None
                else:
                    st.warning("Add a Claude API key to auto-map this report")
                    st.session_state[session_key] = None
            except Exception as e:
                st.error(f"Could not read/map file: {e}")
                st.session_state[session_key] = None
    result = st.session_state.get(session_key)
    if result is not None and len(result):
        st.success(f"✓ {len(result)} rows mapped ({', '.join(result.columns)})")
    return result

KEYWORD_FIELDS = ["keyword","channel","campaign_name","avg_position","quality_score",
                   "landing_page_experience","expected_ctr","ad_relevance",
                   "impressions","clicks","cost","conversions"]
KEYWORD_NUMERIC = ["avg_position","quality_score","impressions","clicks","cost","conversions"]

IMPRESSION_SHARE_FIELDS = ["campaign_name","channel","impression_share","is_lost_rank",
                            "is_lost_budget","competitor","overlap_rate","outranking_share"]
IMPRESSION_SHARE_NUMERIC = ["impression_share","is_lost_rank","is_lost_budget","overlap_rate","outranking_share"]

AUDIENCE_FIELDS = ["segment","age","gender","device","channel",
                    "impressions","clicks","conversions","spend","revenue"]
AUDIENCE_NUMERIC = ["impressions","clicks","conversions","spend","revenue"]

def build_canonical_df(raw_df, mapping):
    df = pd.DataFrame(index=raw_df.index)
    for field, col in mapping.items():
        if col and col in raw_df.columns:
            df[field] = raw_df[col]

    for c in ["spend","revenue","impressions","clicks","conversions","budget","ctr","cpc","roas"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if "brand" not in df.columns or df["brand"].isna().all():
        df["brand"] = "All"
    if "status" not in df.columns or df["status"].isna().all():
        df["status"] = "active"
    if "budget" not in df.columns and "spend" in df.columns:
        df["budget"] = df["spend"]
    if "ctr" not in df.columns and {"clicks","impressions"} <= set(df.columns):
        df["ctr"] = (df["clicks"]/df["impressions"].replace(0, pd.NA)*100).fillna(0)
    if "cpc" not in df.columns and {"spend","clicks"} <= set(df.columns):
        df["cpc"] = (df["spend"]/df["clicks"].replace(0, pd.NA)).fillna(0)
    if "roas" not in df.columns and {"revenue","spend"} <= set(df.columns):
        df["roas"] = (df["revenue"]/df["spend"].replace(0, pd.NA)).fillna(0)
    for c in ["impressions","clicks","conversions"]:
        if c not in df.columns:
            df[c] = 0

    df = df.dropna(subset=[f for f in REQUIRED_FIELDS if f in df.columns])
    return df.reset_index(drop=True)

CHANNEL_NAME_HINTS = [
    ("google", "Google Ads"), ("meta", "Meta Ads"), ("facebook", "Meta Ads"),
    ("bing", "Bing Ads"), ("youtube", "YouTube Ads"), ("instagram", "Instagram Ads"),
    ("linkedin", "LinkedIn Ads"), ("tiktok", "TikTok Ads"), ("ga4", "GA4"), ("analytics", "GA4"),
]

def guess_channel_from_filename(filename):
    name = filename.lower()
    for hint, label in CHANNEL_NAME_HINTS:
        if hint in name:
            return label
    return os.path.splitext(filename)[0][:40]

def finalize_file_df(raw_df, mapping, filename):
    """build_canonical_df, plus a filename-based channel fallback for files with no
    channel column at all — common when a platform's raw export assumes the whole
    file IS that one platform (e.g. a plain Google Ads export)."""
    cdf = build_canonical_df(raw_df, mapping)
    if "channel" not in cdf.columns or cdf["channel"].isna().all() or (cdf["channel"].astype(str).str.strip() == "").all():
        cdf["channel"] = guess_channel_from_filename(filename)
    return cdf

@st.cache_data
def summary(df):
    sp = df["spend"].sum(); rv = df["revenue"].sum()
    return {
        "n": len(df), "spend": sp, "revenue": rv,
        "impressions": df["impressions"].sum(),
        "clicks": df["clicks"].sum(),
        "conversions": df["conversions"].sum(),
        "roas": rv/sp if sp else 0,
        "ctr": df["ctr"].mean(), "cpc": df["cpc"].mean(),
        "top_ch": df.groupby("channel")["roas"].mean().idxmax(),
        "best": df.loc[df["roas"].idxmax(),"campaign_name"],
        "worst": df.loc[df["roas"].idxmin(),"campaign_name"],
        "brands": df["brand"].unique().tolist(),
        "channels": df["channel"].unique().tolist(),
    }

@st.cache_data
def anomalies(df):
    ar, ac = df["roas"].mean(), df["ctr"].mean()
    rows = []
    for _, r in df.iterrows():
        issues, sev = [], "OK"
        if r["roas"] < 1.0:
            issues.append(f"ROAS {r['roas']:.2f}x — losing money"); sev = "HIGH"
        elif r["roas"] < ar * 0.5:
            issues.append(f"ROAS {r['roas']:.2f}x — 50% below portfolio avg"); sev = "MED"
        if r["ctr"] < ac * 0.4:
            issues.append(f"CTR {r['ctr']:.2f}% — very low")
            if sev=="OK": sev="MED"
        util = r["spend"]/r["budget"]*100 if r["budget"]>0 else 0
        if util>99: issues.append(f"Budget fully exhausted ({util:.0f}%)")
        if not issues: issues.append("Performing within normal range")
        rows.append({"campaign":r["campaign_name"],"channel":r["channel"],
                     "brand":r["brand"],"severity":sev,
                     "issues":"; ".join(issues),"roas":r["roas"],"spend":r["spend"]})
    return pd.DataFrame(rows)

def health_score(s, adf):
    high = len(adf[adf["severity"]=="HIGH"])
    score = min(100, max(0, int(
        (s["roas"]/10)*40 + (s["ctr"]/5)*30 + ((s["n"]-high)/max(1,s["n"]))*30
    )))
    return score

# ──────────────────────────────────────────────────────────────
# AI STREAMING
# ──────────────────────────────────────────────────────────────
DEFAULT_SYSTEM_PROMPT = ("You are a senior digital marketing analyst. "
    "Be specific, data-driven, and actionable. Use ₹ for currency. No filler phrases.")

def active_system_prompt():
    """The active profile's AI-generated persona prompt, or a generic fallback if none is set."""
    profile = st.session_state.get("active_profile")
    if profile and profile.get("system_prompt"):
        return profile["system_prompt"]
    return DEFAULT_SYSTEM_PROMPT

def profile_context_block():
    """Explicit client-facts block appended to every generation prompt — on top of (not instead
    of) the profile's system prompt, so each output is anchored to concrete specifics every time."""
    profile = st.session_state.get("active_profile")
    if not profile:
        return ""
    budget = profile.get("monthly_budget")
    return f"""
CLIENT CONTEXT:
- Industry: {profile.get("industry") or "Not specified"}
- Description: {profile.get("description") or "Not specified"}
- Primary Goal(s): {profile.get("goal") or "Not specified"}
- Target: {profile.get("target_value") or "Not specified"}
- Monthly Budget: {f"Rs. {budget:,.0f}" if budget else "Not specified"}
"""

def stream_ai(prompt, client, ph, header="⚡ AI Analyst", system=None):
    if system is None:
        system = active_system_prompt()
    full = ""
    stream = client.chat.completions.create(
        model=AI_MODEL, max_tokens=800, stream=True,
        messages=[{"role":"system","content":system},{"role":"user","content":prompt}]
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            full += delta
            ph.markdown(f'<div class="aibox"><div class="aihdr">🟣 {header} — generating…</div>'
                        f'<div class="aibody">{full}▌</div></div>', unsafe_allow_html=True)
    ph.markdown(f'<div class="aibox"><div class="aihdr">✅ {header}</div>'
                f'<div class="aibody">{full}</div></div>', unsafe_allow_html=True)
    return full

def call_ai_plain(prompt, client, system=None, model=None):
    """Non-streaming call — safe to run inside a worker thread (no st.* calls here)."""
    if system is None:
        system = active_system_prompt()
    resp = client.chat.completions.create(
        model=model or AI_MODEL, max_tokens=800,
        messages=[{"role":"system","content":system},{"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content

def generate_and_cache(key, prompt, header, client, model=None):
    """Runs synchronously, with a spinner scoped to wherever it's called —
    so the loader only ever shows inside the section that was actually triggered."""
    with st.spinner(f"⚡ Generating {header}…"):
        try:
            result = call_ai_plain(prompt, client, active_system_prompt(), model=model)
        except Exception as e:
            result = f"⚠️ AI request failed: {e}"
    st.session_state.setdefault("ai_cache", {})[key] = result
    try:
        st.rerun(scope="fragment")  # scoped rerun when called from inside an @st.fragment tab
    except StreamlitAPIException:
        st.rerun()  # plain tabs (not yet fragment-wrapped) fall back to a full rerun

def chat_reply(client, df, chat_history, ph, max_tokens=400, style="Be concise, specific, data-driven."):
    """Streams the assistant's reply token-by-token into ph, like a real chat client."""
    data_ctx = df[["campaign_name","channel","brand","spend","revenue",
                   "roas","ctr","cpc","conversions"]].to_dict("records")
    sys = (f"{active_system_prompt()} Data: {json.dumps(data_ctx)}. {style} Use ₹.")
    msgs = [{"role":m["role"],"content":m["content"]} for m in chat_history]
    try:
        full = ""
        stream = client.chat.completions.create(model=AI_MODEL, max_tokens=max_tokens, stream=True,
                                    messages=[{"role":"system","content":sys}]+msgs)
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                full += delta
                ph.markdown(full + "▌")
        ph.markdown(full)
        return full
    except Exception as e:
        err = f"⚠️ AI request failed: {e}"
        ph.markdown(err)
        return err

# ──────────────────────────────────────────────────────────────
# PDF GENERATOR
# ──────────────────────────────────────────────────────────────
def pdf_safe(text):
    repl = {"—":"-","–":"-","‘":"'","’":"'","“":'"',"”":'"',"…":"...","·":"-","₹":"Rs. ","•":"-"}
    text = str(text)
    for a,b in repl.items(): text = text.replace(a,b)
    return text.encode('latin-1','replace').decode('latin-1')

def _pdf_write_inline(pdf, line, size, color):
    """Write one line, rendering **bold** spans inline, wrapping via write()."""
    parts = re.split(r"(\*\*[^*]+\*\*)", line)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("Helvetica", "B", size); pdf.set_text_color(*color)
            pdf.write(5.5, part[2:-2])
        else:
            pdf.set_font("Helvetica", "", size); pdf.set_text_color(*color)
            pdf.write(5.5, part)
    pdf.ln(6)

def write_markdown(pdf, text, base_size=10, color=(40,40,70)):
    """Render simple Markdown (headers, bullets, **bold**) into the PDF instead of raw syntax."""
    for raw_line in pdf_safe(text).split("\n"):
        line = raw_line.strip()
        if not line:
            pdf.ln(3)
            continue
        if line in ("---", "***", "___"):
            pdf.set_draw_color(210,210,230)
            pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
            pdf.ln(5)
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            size = {1: base_size+4, 2: base_size+3, 3: base_size+1}[level]
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", size); pdf.set_text_color(20,20,60)
            pdf.multi_cell(0, size*0.6, m.group(2))
            pdf.ln(1)
            continue
        bullet_text = None
        indent = 0
        if line.startswith("- ") or line.startswith("* "):
            bullet_text = line[2:]
        else:
            m2 = re.match(r"^\d+\.\s+(.*)", line)
            if m2:
                bullet_text = m2.group(1)
        if bullet_text is not None:
            pdf.set_x(pdf.l_margin + 4)
            _pdf_write_inline(pdf, "- " + bullet_text, base_size, color)
            continue
        _pdf_write_inline(pdf, line, base_size, color)

def make_pdf(df, s, ai_texts, chat_transcript=None):
    pdf = FPDF(); pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page()
    pdf.set_fill_color(10,10,30); pdf.rect(0,0,210,42,'F')
    pdf.set_font("Helvetica","B",20); pdf.set_text_color(255,255,255)
    pdf.set_y(12); pdf.cell(0,10,pdf_safe("CampaignIQ — AI Campaign Intelligence Report"),align="C")
    pdf.set_font("Helvetica","",9); pdf.set_text_color(150,150,200); pdf.set_y(27)
    pdf.cell(0,8,pdf_safe(f"MATRIX Hackathon 2026  |  {datetime.now().strftime('%d %b %Y %H:%M')}  |  Powered by Anthropic Claude"),align="C")
    pdf.set_y(50)
    pdf.set_font("Helvetica","B",13); pdf.set_text_color(20,20,60)
    pdf.cell(0,8,"Executive Summary",ln=True)
    pdf.set_draw_color(99,102,241); pdf.set_line_width(0.5)
    pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
    kpis=[("Total Spend",inr(s["spend"])),("Total Revenue",inr(s["revenue"])),
          ("Overall ROAS",f"{s['roas']:.2f}x"),("Avg CTR",f"{s['ctr']:.2f}%"),
          ("Total Conversions",num(s["conversions"])),("Best Campaign",s["best"][:40]),
          ("Needs Attention",s["worst"][:40]),("Top Channel",s["top_ch"])]
    pdf.set_font("Helvetica","",11)
    for i,(k,v) in enumerate(kpis):
        pdf.set_fill_color(245,245,255) if i%2==0 else pdf.set_fill_color(255,255,255)
        pdf.set_text_color(80,80,100); pdf.cell(80,8,pdf_safe(f"  {k}"),fill=True)
        pdf.set_text_color(20,20,60); pdf.set_font("Helvetica","B",11)
        pdf.cell(0,8,pdf_safe(v),ln=True,fill=True); pdf.set_font("Helvetica","",11)
    pdf.ln(5)
    for title,text in ai_texts.items():
        if not text: continue
        pdf.set_font("Helvetica","B",13); pdf.set_text_color(20,20,60)
        pdf.cell(0,8,pdf_safe(title),ln=True)
        pdf.set_draw_color(99,102,241); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
        write_markdown(pdf, text)
        pdf.ln(4)

    if chat_transcript:
        pdf.set_font("Helvetica","B",13); pdf.set_text_color(20,20,60)
        pdf.cell(0,8,"AI Chat Transcript",ln=True)
        pdf.set_draw_color(99,102,241); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
        for msg in chat_transcript:
            label = "You" if msg["role"]=="user" else "AI Analyst"
            pdf.set_font("Helvetica","B",10); pdf.set_text_color(60,60,120)
            pdf.cell(0,6,pdf_safe(f"{label}:"),ln=True)
            write_markdown(pdf, msg["content"], base_size=10, color=(40,40,70))
            pdf.ln(2)
        pdf.ln(4)

    pdf.add_page()
    pdf.set_font("Helvetica","B",13); pdf.set_text_color(20,20,60)
    pdf.cell(0,8,"Campaign Data",ln=True)
    pdf.set_draw_color(99,102,241); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
    hdrs=["Campaign","Channel","Spend","Revenue","ROAS","CTR","Conv."]; ws=[52,28,22,22,18,14,14]
    pdf.set_fill_color(99,102,241); pdf.set_text_color(255,255,255); pdf.set_font("Helvetica","B",9)
    for h,w in zip(hdrs,ws): pdf.cell(w,8,pdf_safe(h),border=0,fill=True)
    pdf.ln(); pdf.set_font("Helvetica","",8)
    for i,row in df.iterrows():
        pdf.set_fill_color(245,245,255) if i%2==0 else pdf.set_fill_color(255,255,255)
        pdf.set_text_color(30,30,60)
        vals=[str(row["campaign_name"])[:30],str(row["channel"])[:16],
              inr(row["spend"]),inr(row["revenue"]),
              f"{row['roas']:.2f}x",f"{row['ctr']:.2f}%",str(int(row["conversions"]))]
        for v,w in zip(vals,ws): pdf.cell(w,7,pdf_safe(v),border=0,fill=True)
        pdf.ln()
    pdf.ln(8); pdf.set_font("Helvetica","I",9); pdf.set_text_color(120,120,140)
    pdf.cell(0,6,pdf_safe("CampaignIQ · LS Digital Group · MATRIX Hackathon 2026"),align="C")
    return io.BytesIO(bytes(pdf.output()))

# ──────────────────────────────────────────────────────────────
# SUPABASE AUTH
# ──────────────────────────────────────────────────────────────
def get_sb_auth():
    url = os.getenv("SUPABASE_URL","").strip()
    key = os.getenv("SUPABASE_ANON_KEY","").strip()
    return create_client(url, key) if url and key else None

def get_sb_admin():
    url = os.getenv("SUPABASE_URL","").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY","").strip()
    return create_client(url, key) if url and key else None

COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days — matches Supabase's refresh token lifetime

def require_auth():
    sb_auth = get_sb_auth()
    if sb_auth is None:
        return None  # Supabase not configured — app runs without auth

    if st.session_state.get("sb_user"):
        return st.session_state.sb_user

    # Page refresh wipes session_state — try to silently restore the session from
    # tokens saved in a browser cookie before falling back to the login form.
    # (Not gated to "try once": the cookie component only delivers real values
    # a rerun after mount, so this must stay live across the first couple of reruns.)
    controller = CookieController()
    access_token = controller.get("sb_access_token")
    refresh_token = controller.get("sb_refresh_token")
    if access_token and refresh_token:
        try:
            res = sb_auth.auth.set_session(access_token, refresh_token)
            st.session_state.sb_user = res.user
            return res.user
        except Exception:
            controller.remove("sb_access_token")
            controller.remove("sb_refresh_token")

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem">
      <div style="font-size:44px">⚡</div>
      <div style="font-size:26px;font-weight:800;color:#F1F5F9;letter-spacing:-1px">Campaign<span style="color:#4F46E5">IQ</span></div>
      <div style="font-size:12px;color:#94A3B8;margin-top:4px">Sign in to continue</div>
    </div>
    """, unsafe_allow_html=True)

    lcol, mcol, rcol = st.columns([1,1.4,1])
    with mcol:
        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Log In", use_container_width=True):
                    try:
                        res = sb_auth.auth.sign_in_with_password({"email": email, "password": pw})
                        st.session_state.sb_user = res.user
                        controller.set("sb_access_token", res.session.access_token, max_age=COOKIE_MAX_AGE)
                        controller.set("sb_refresh_token", res.session.refresh_token, max_age=COOKIE_MAX_AGE)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")

        with tab_signup:
            with st.form("signup_form"):
                email2 = st.text_input("Email", key="su_email")
                pw2 = st.text_input("Password", type="password", key="su_pw")
                if st.form_submit_button("Sign Up", use_container_width=True):
                    try:
                        sb_auth.auth.sign_up({"email": email2, "password": pw2})
                        st.success("Account created. If email confirmation is enabled, check your inbox — then log in.")
                    except Exception as e:
                        st.error(f"Sign up failed: {e}")
    st.stop()

sb_user = require_auth()

# ──────────────────────────────────────────────────────────────
# BUSINESS PROFILES (PERSONA SYSTEM)
# ──────────────────────────────────────────────────────────────
GOAL_OPTIONS = ["Leads", "Awareness", "Traffic", "Sales / ROAS", "Engagement"]

def generate_profile_system_prompt(client, name, description, goal, target_value, industry, monthly_budget):
    goal_text = ", ".join(goal) if isinstance(goal, (list, tuple)) else goal
    meta_prompt = f"""You are configuring an AI marketing analyst for a specific client account.

CLIENT: {name}
INDUSTRY: {industry or "Not specified"}
DESCRIPTION: {description or "Not specified"}
PRIMARY GOALS: {goal_text}
TARGET: {target_value or "Not specified"}
MONTHLY BUDGET: {f"Rs. {monthly_budget:,.0f}" if monthly_budget else "Not specified"}

Write a system prompt (an instruction set, not a report) that an AI marketing analyst should use for ALL future analysis of this client's campaign data. It should specify:
1. What "success" means for this client given their goal and target
2. Which metrics to prioritize and which to treat as secondary guardrails
3. How to frame recommendations (tone, depth, what matters to this business)
4. Anything specific to their industry worth keeping in mind

Write it as a direct instruction to the analyst (e.g. "You are a senior marketing analyst for..."), 150-250 words, ready to paste as a system prompt. Output ONLY the system prompt text, no preamble."""
    resp = client.chat.completions.create(
        model=AI_MODEL, max_tokens=500,
        messages=[{"role":"user","content":meta_prompt}]
    )
    return resp.choices[0].message.content.strip()

def clear_ai_cache():
    st.session_state.ai_cache = {}

def _activate_profile(profile):
    """Switching profiles starts fresh — each client's data/cache/chat stays separate."""
    st.session_state.active_profile = profile
    st.session_state.pop("df_raw", None)
    clear_ai_cache()
    st.session_state.chat = []
    st.session_state.pop("file_batch_sig", None)
    st.session_state.pop("file_states", None)
    st.session_state.pop("df_built_for_sig", None)

def require_profile(sb_admin, user_id):
    if st.session_state.get("active_profile"):
        return st.session_state.active_profile

    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem">
      <div style="font-size:20px;font-weight:800;color:#F1F5F9">Choose a client profile</div>
      <div style="font-size:12px;color:#94A3B8;margin-top:4px">Each profile keeps one client's data, history, and AI personalization separate</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        profiles = (sb_admin.table("business_profiles").select("*")
                    .eq("user_id", user_id).order("created_at", desc=True).execute().data)
    except Exception as e:
        st.error(f"Could not load profiles: {e}")
        profiles = []

    if profiles:
        cols = st.columns(3)
        for i, p in enumerate(profiles):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="kcard" style="margin-bottom:.75rem">
                  <div class="klabel">{p['name']}</div>
                  <div class="kdelta neu">{p['goal']} · {p.get('industry') or 'General'}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Select {p['name']}", key=f"sel_profile_{p['id']}", use_container_width=True):
                    _activate_profile(p)
                    st.rerun()
        st.markdown('<hr style="border-color:rgba(99,102,241,.2);margin:1.5rem 0">', unsafe_allow_html=True)

    with st.expander("➕ Create new profile", expanded=not profiles):
        name = st.text_input("Client Name")
        description = st.text_area("Description", placeholder="What does this business do, who's the audience?")
        goal = st.multiselect("Primary Goal(s)", GOAL_OPTIONS)
        target_value = st.text_input("Target", placeholder="e.g. CPL <= Rs.500, or ROAS >= 4x")
        industry = st.text_input("Industry", placeholder="e.g. D2C fashion, insurance, real estate")
        monthly_budget = st.number_input("Monthly Budget (Rs., optional)", min_value=0, value=0, step=10000)

        if st.button("✨ Generate personalized system prompt", use_container_width=True):
            if not name or not goal:
                st.warning("Name and at least one Goal are required.")
            else:
                client = get_client()
                if not client:
                    st.error("Add a Claude API key first — needed to generate the profile's system prompt.")
                else:
                    with st.spinner("Generating personalized system prompt…"):
                        st.session_state.generated_prompt = generate_profile_system_prompt(
                            client, name, description, goal, target_value, industry, monthly_budget or None)
                        st.session_state.generated_prompt_meta = {
                            "name": name, "description": description, "goal": ", ".join(goal),
                            "target_value": target_value, "industry": industry,
                            "monthly_budget": monthly_budget or None,
                        }

        if st.session_state.get("generated_prompt"):
            edited_prompt = st.text_area("Review / edit the generated system prompt before saving",
                                          value=st.session_state.generated_prompt, height=180)
            if st.button("💾 Save Profile", use_container_width=True):
                meta = st.session_state.generated_prompt_meta
                try:
                    result = sb_admin.table("business_profiles").insert({
                        "user_id": user_id, "name": meta["name"], "description": meta["description"],
                        "goal": meta["goal"], "target_value": meta["target_value"],
                        "industry": meta["industry"], "monthly_budget": meta["monthly_budget"],
                        "system_prompt": edited_prompt,
                    }).execute()
                    st.session_state.pop("generated_prompt", None)
                    st.session_state.pop("generated_prompt_meta", None)
                    _activate_profile(result.data[0])
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save profile: {e}")

    st.stop()

def render_edit_profile_screen(sb_admin, profile):
    st.markdown('<div class="sh">✏️ Edit Profile</div>', unsafe_allow_html=True)

    name = st.text_input("Client Name", value=profile.get("name",""))
    description = st.text_area("Description", value=profile.get("description") or "",
                                placeholder="What does this business do, who's the audience?")
    _saved_goals = [g.strip() for g in (profile.get("goal") or "").split(",") if g.strip()]
    goal = st.multiselect("Primary Goal(s)", GOAL_OPTIONS,
                           default=[g for g in _saved_goals if g in GOAL_OPTIONS])
    target_value = st.text_input("Target", value=profile.get("target_value") or "",
                                  placeholder="e.g. CPL <= Rs.500, or ROAS >= 4x")
    industry = st.text_input("Industry", value=profile.get("industry") or "",
                              placeholder="e.g. D2C fashion, insurance, real estate")
    monthly_budget = st.number_input("Monthly Budget (Rs., optional)", min_value=0,
                                      value=int(profile.get("monthly_budget") or 0), step=10000)

    if st.button("🔄 Regenerate System Prompt", use_container_width=True):
        if not name or not goal:
            st.warning("Name and at least one Goal are required.")
        else:
            client = get_client()
            if not client:
                st.error("Add a Claude API key first — needed to regenerate the profile's system prompt.")
            else:
                with st.spinner("Regenerating personalized system prompt…"):
                    st.session_state.edited_prompt_draft = generate_profile_system_prompt(
                        client, name, description, goal, target_value, industry, monthly_budget or None)
                    st.session_state.edited_prompt_meta = {
                        "name": name, "description": description, "goal": ", ".join(goal),
                        "target_value": target_value, "industry": industry,
                        "monthly_budget": monthly_budget or None,
                    }

    draft = st.session_state.get("edited_prompt_draft", profile.get("system_prompt") or "")
    edited_prompt = st.text_area("System prompt (regenerate above, or edit directly)", value=draft, height=180)

    save_col, cancel_col = st.columns(2)
    with save_col:
        if st.button("💾 Save Changes", use_container_width=True):
            meta = st.session_state.get("edited_prompt_meta", {
                "name": name, "description": description, "goal": ", ".join(goal),
                "target_value": target_value, "industry": industry,
                "monthly_budget": monthly_budget or None,
            })
            try:
                sb_admin.table("business_profiles").update({
                    "name": meta["name"], "description": meta["description"],
                    "goal": meta["goal"], "target_value": meta["target_value"],
                    "industry": meta["industry"], "monthly_budget": meta["monthly_budget"],
                    "system_prompt": edited_prompt,
                }).eq("id", profile["id"]).execute()
                updated = dict(profile)
                updated.update(meta)
                updated["system_prompt"] = edited_prompt
                st.session_state.active_profile = updated
                st.session_state.pop("edited_prompt_draft", None)
                st.session_state.pop("edited_prompt_meta", None)
                st.session_state.editing_profile = False
                st.success("Profile updated.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not save changes: {e}")
    with cancel_col:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pop("edited_prompt_draft", None)
            st.session_state.pop("edited_prompt_meta", None)
            st.session_state.editing_profile = False
            st.rerun()

    st.stop()

active_profile = require_profile(get_sb_admin(), sb_user.id) if sb_user else None
client_label = active_profile["name"] if active_profile else "this client"

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.2rem 0 .5rem">
      <div style="font-size:36px">⚡</div>
      <div style="font-size:20px;font-weight:800;color:#F1F5F9;letter-spacing:-1px">CampaignIQ</div>
      <div style="font-size:11px;color:#64748B;margin-top:2px">MATRIX Hackathon 2026</div>
    </div>
    <hr style="border-color:rgba(99,102,241,.2);margin:.75rem 0">
    """, unsafe_allow_html=True)

    is_client = False  # View Mode toggle removed — profile goal/industry now carries this context

    st.markdown('<p style="color:#CBD5E1;font-size:12px;font-weight:600;margin-bottom:4px">📂 DATA</p>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Campaign data upload", type=["csv","xlsx","xls"],
                                       accept_multiple_files=True, label_visibility="collapsed")
    st.markdown('<p style="color:#64748B;font-size:10px;margin-top:2px">Upload one or more files (CSV/Excel) — different exports with different columns are each understood on their own, then merged.</p>', unsafe_allow_html=True)

    client = get_client()
    if client:
        st.markdown('<p style="color:#10B981;font-size:12px;margin-top:8px">✓ AI Connected</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#EF4444;font-size:12px;margin-top:8px">✗ AI Offline — set ANTHROPIC_API_KEY or OPENROUTER_API_KEY in .env</p>', unsafe_allow_html=True)

    if active_profile:
        st.markdown('<hr style="border-color:rgba(99,102,241,.2);margin:.75rem 0">', unsafe_allow_html=True)
        st.markdown(f"""<p style="color:#CBD5E1;font-size:12px;font-weight:600;margin-bottom:2px">🏢 {active_profile['name']}</p>
        <p style="color:#64748B;font-size:11px;margin-bottom:6px">{active_profile['goal']} · {active_profile.get('industry') or 'General'}</p>""",
                    unsafe_allow_html=True)
        ep_col, sp_col = st.columns(2)
        with ep_col:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.editing_profile = True
        with sp_col:
            if st.button("🔀 Switch", use_container_width=True):
                st.session_state.pop("active_profile", None)
                st.rerun()

    st.markdown('<hr style="border-color:rgba(99,102,241,.2);margin:.75rem 0">', unsafe_allow_html=True)
    st.markdown('<p style="color:#CBD5E1;font-size:12px;font-weight:600;margin-bottom:4px">🔧 FILTERS</p>', unsafe_allow_html=True)

    if "df_raw" in st.session_state:
        d = st.session_state.df_raw
        sel_brand    = st.selectbox("Brand",   ["All"]+sorted(d["brand"].unique().tolist()))
        sel_channels = st.multiselect("Platform", sorted(d["channel"].unique().tolist()),
                                       default=[], placeholder="All platforms")
        sel_status   = st.selectbox("Status",  ["All"]+sorted(d["status"].unique().tolist()))
    else:
        sel_brand = sel_status = "All"
        sel_channels = []

    st.markdown('<hr style="border-color:rgba(99,102,241,.2);margin:.75rem 0">', unsafe_allow_html=True)
    if st.button("🔄 Regenerate AI", use_container_width=True):
        clear_ai_cache()
        st.success("Cache cleared — click 'Generate' on any section to run it again")

    st.markdown('<hr style="border-color:rgba(99,102,241,.2);margin:.75rem 0">', unsafe_allow_html=True)
    if sb_user:
        st.markdown(f'<p style="color:#94A3B8;font-size:11px">👤 {sb_user.email}</p>', unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            get_sb_auth().auth.sign_out()
            CookieController().remove("sb_access_token")
            CookieController().remove("sb_refresh_token")
            st.session_state.sb_user = None
            st.session_state.pop("active_profile", None)
            st.rerun()

if st.session_state.get("editing_profile") and active_profile:
    render_edit_profile_screen(get_sb_admin(), active_profile)

# ──────────────────────────────────────────────────────────────
# LOAD DATA — one or more files, each understood on its own, then merged
# ──────────────────────────────────────────────────────────────
if uploaded_files:
    batch_sig = tuple(sorted((f.name, f.size) for f in uploaded_files))
    if st.session_state.get("file_batch_sig") != batch_sig:
        st.session_state.file_batch_sig = batch_sig
        st.session_state.df_built_for_sig = None
        file_states = {}
        for f in uploaded_files:
            try:
                raw_df = load_any(f)
            except Exception as e:
                file_states[f.name] = {"status": "error", "error": str(e)}
                continue
            if all(c in raw_df.columns for c in CANONICAL_FIELDS):
                cdf = raw_df.copy()
                if "date" in cdf.columns:
                    cdf["date"] = pd.to_datetime(cdf["date"], errors="coerce")
                if "channel" not in cdf.columns or cdf["channel"].isna().all():
                    cdf["channel"] = guess_channel_from_filename(f.name)
                file_states[f.name] = {"status": "done", "canonical_df": cdf}
            else:
                file_states[f.name] = {"status": "pending", "raw_df": raw_df, "mapping": None}
        st.session_state.file_states = file_states
        st.session_state.pop("df_raw", None)

    file_states = st.session_state.get("file_states", {})

    error_names = [n for n, s in file_states.items() if s["status"] == "error"]
    for n in error_names:
        st.error(f"Could not read {n}: {file_states[n]['error']}")

    pending_names = [n for n, s in file_states.items() if s["status"] == "pending"]
    if pending_names:
        st.markdown('<div class="sh">🧭 Map your file columns</div>', unsafe_allow_html=True)
        st.caption(f"{len(pending_names)} of {len(file_states)} file(s) don't match our exact format — "
                   "confirm (or fix) each mapping below, then continue. Files already in our format are ready automatically.")
        cl = get_client()
        for fname in pending_names:
            fstate = file_states[fname]
            raw_df = fstate["raw_df"]
            with st.expander(f"🧾 {fname}", expanded=True):
                if fstate["mapping"] is None:
                    if cl:
                        with st.spinner(f"Reading {fname}'s structure…"):
                            try:
                                fstate["mapping"] = ai_map_columns(
                                    cl, raw_df.columns.tolist(), raw_df.head(3).to_dict("records"))
                            except Exception as e:
                                st.error(f"AI mapping failed for {fname}, map manually below: {e}")
                                fstate["mapping"] = {fl: None for fl in CANONICAL_FIELDS + OPTIONAL_FIELDS}
                    else:
                        st.info("🔑 Add a Claude API key for automatic mapping — map manually below meanwhile.")
                        fstate["mapping"] = {fl: None for fl in CANONICAL_FIELDS + OPTIONAL_FIELDS}

                options = ["(none)"] + raw_df.columns.tolist()
                mapping = {}
                cols = st.columns(3)
                for i, field in enumerate(CANONICAL_FIELDS + OPTIONAL_FIELDS):
                    with cols[i % 3]:
                        guess = fstate["mapping"].get(field)
                        idx = options.index(guess) if guess in options else 0
                        label = field + (" *" if field in REQUIRED_FIELDS else " (optional)" if field in OPTIONAL_FIELDS else "")
                        sel = st.selectbox(label, options, index=idx, key=f"map_{fname}_{field}")
                        mapping[field] = None if sel == "(none)" else sel

                missing_required = [f for f in REQUIRED_FIELDS if not mapping.get(f)]
                if missing_required:
                    st.warning(f"Required fields not mapped yet: {', '.join(missing_required)}")

                if st.button(f"✅ Confirm {fname}", key=f"confirm_{fname}", disabled=bool(missing_required)):
                    fstate["canonical_df"] = finalize_file_df(raw_df, mapping, fname)
                    fstate["status"] = "done"
                    st.rerun()
        st.stop()

    if file_states and st.session_state.get("df_built_for_sig") != st.session_state.get("file_batch_sig"):
        good_dfs = [s["canonical_df"] for s in file_states.values() if s["status"] == "done"]
        if good_dfs:
            st.session_state.df_raw = pd.concat(good_dfs, ignore_index=True)
            clear_ai_cache()
        st.session_state.df_built_for_sig = st.session_state.file_batch_sig

@st.fragment
def render_history_section():
    st.markdown('<div class="sh">🕘 Saved Reports</div>', unsafe_allow_html=True)

    if not sb_user:
        st.info("Log in to save and view report history.")
        return

    try:
        sb_admin = get_sb_admin()
        q = sb_admin.table("analysis_history").select("*").eq("user_id", sb_user.id)
        if active_profile:
            q = q.eq("profile_id", active_profile["id"])
        hist_rows = q.order("created_at", desc=True).execute().data
    except Exception as e:
        hist_rows = []
        st.error(f"Could not load history: {e}")

    if not hist_rows:
        st.info("No saved reports yet — generate AI insights, then use '💾 Save Session to History' above.")
        return

    SECTION_LABELS = [
        ("ai_brief",   "🤖 Executive Brief"),
        ("ai_anomaly", "🚨 Anomaly Analysis"),
        ("ai_recs",    "💡 Budget Recommendations"),
        ("ai_forecast","🔮 Forecast Commentary"),
        ("ai_bench",   "🏁 Competitive Benchmarking"),
    ]

    for row in hist_rows:
        created = (row.get("created_at") or "")[:16].replace("T", " ")
        k = row.get("kpis") or {}
        st.markdown(f"""
        <div class="kcard" style="margin-bottom:.5rem">
          <div class="klabel">{row.get("filename","report")} — {created}</div>
          <div class="kval" style="font-size:16px">
            {inr(k.get("spend",0))} spend · {inr(k.get("revenue",0))} revenue ·
            {k.get("roas",0):.2f}x ROAS
          </div>
        </div>""", unsafe_allow_html=True)

        pdf_key = f"hist_pdf_bytes_{row.get('id')}"
        if st.session_state.get(pdf_key):
            st.download_button("⬇ Download PDF", data=st.session_state[pdf_key],
                               file_name=f"CampaignIQ_{str(row.get('id',''))[:8]}.pdf",
                               mime="application/pdf", key=f"dl_{row.get('id')}")
        elif row.get("campaign_data"):
            if st.button("📄 Prepare PDF", key=f"genpdf_{row.get('id')}"):
                hist_df = pd.DataFrame(row.get("campaign_data") or [])
                hist_S = summary(hist_df)
                hist_ai_texts = {
                    "Executive Brief":          row.get("ai_brief") or "",
                    "Anomaly Analysis":         row.get("ai_anomaly") or "",
                    "Budget Recommendations":   row.get("ai_recs") or "",
                    "Forecast Commentary":      row.get("ai_forecast") or "",
                    "Competitive Benchmarking": row.get("ai_bench") or "",
                }
                pdf_bytes = make_pdf(hist_df, hist_S, hist_ai_texts, row.get("chat_transcript")).getvalue()
                st.session_state[pdf_key] = pdf_bytes
                st.rerun(scope="fragment")

        with st.expander("👁 View full report"):
            for field, label in SECTION_LABELS:
                text = row.get(field)
                if text:
                    st.markdown(f'<div class="aibox"><div class="aihdr">{label}</div>'
                                f'<div class="aibody">{text}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="aibox" style="opacity:.55"><div class="aihdr">{label}</div>'
                                f'<div class="aibody"><i>No data — not generated for this session.</i></div></div>',
                                unsafe_allow_html=True)

            st.markdown('<div class="sh">💬 AI Chat</div>', unsafe_allow_html=True)
            transcript = row.get("chat_transcript") or []
            if transcript:
                for msg in transcript:
                    with st.chat_message(msg["role"], avatar="⚡" if msg["role"]=="assistant" else None):
                        st.markdown(msg["content"])
            else:
                st.markdown('<div class="aibox" style="opacity:.55"><div class="aibody"><i>No chat messages for this session.</i></div></div>',
                            unsafe_allow_html=True)

        st.markdown('<div class="div"></div>', unsafe_allow_html=True)

if "df_raw" not in st.session_state:
    st.markdown('<div class="sh">📂 Upload your campaign data to get started</div>', unsafe_allow_html=True)
    st.info("Upload one or more campaign CSV/Excel files in the sidebar — each is understood on its own and merged, so files with different columns are fine.")
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    render_history_section()
    st.stop()

df_raw = st.session_state.df_raw
df = df_raw.copy()
if sel_brand   != "All": df = df[df["brand"]   == sel_brand]
if sel_channels:         df = df[df["channel"].isin(sel_channels)]
if sel_status  != "All": df = df[df["status"]  == sel_status]

def platform_filter(base_df, key):
    """Per-section platform filter, layered on top of the global filter."""
    opts = sorted(base_df["channel"].unique().tolist())
    sel = st.multiselect("🎯 Platform filter", opts, default=[], placeholder="All platforms",
                         key=f"pf_{key}")
    tag = "-".join(s.lower().replace(" ", "") for s in sorted(sel)) if sel else "all"
    return (base_df[base_df["channel"].isin(sel)] if sel else base_df), tag

S   = summary(df)
adf = anomalies(df)
high_n = len(adf[adf["severity"]=="HIGH"])
med_n  = len(adf[adf["severity"]=="MED"])
ok_n   = len(adf[adf["severity"]=="OK"])
hs     = health_score(S, adf)

# ──────────────────────────────────────────────────────────────
# NAVBAR
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="navbar">
  <div>
    <div class="nb-brand">⚡ Campaign<span>IQ</span></div>
    <div class="nb-sub">AI Campaign Intelligence Platform{f" · {active_profile['name']}" if active_profile else ""}</div>
  </div>
  <div class="nb-badges">
    <span class="badge">{"👔 Client View" if is_client else "📊 Analyst View"}</span>
    <span class="badge {'g' if client else 'r'}">{"🟢 AI Active" if client else "🔴 AI Offline"}</span>
    {'<span class="badge r">🚨 '+str(high_n)+' Critical</span>' if high_n else '<span class="badge g">✅ No Critical Issues</span>'}
    <span class="badge y">Health: {hs}/100</span>
    <span class="badge">MATRIX 2026</span>
  </div>
</div>
""", unsafe_allow_html=True)

if not client:
    st.warning("🔑 **Add your Claude API key in the sidebar** to activate real-time AI analysis, recommendations, forecasts, and chat.")

# ──────────────────────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────────────────────
kpi_items = [
    ("Total Spend",    inr(S["spend"]),         "Across all campaigns","neu"),
    ("Total Revenue",  inr(S["revenue"]),        f"{'↑' if S['revenue']>S['spend'] else '↓'} vs spend","up" if S["revenue"]>S["spend"] else "down"),
    ("Overall ROAS",   f"{S['roas']:.2f}x",      "Return per ₹1 spent","up" if S["roas"]>3 else "down"),
    ("Impressions",    num(S["impressions"]),     "Total ad reach","neu"),
    ("Avg CTR",        f"{S['ctr']:.2f}%",        "Click-through rate","up" if S["ctr"]>2 else "down"),
    ("Conversions",    num(S["conversions"]),     "Total conversions","up"),
]
kpi_cols = st.columns(3) + st.columns(3)
for col,(lbl,val,delta,cls) in zip(kpi_cols, kpi_items):
    with col:
        st.markdown(f"""
        <div class="kcard">
          <div class="klabel">{lbl}</div>
          <div class="kval">{val}</div>
          <div class="kdelta {cls}">{delta}</div>
        </div>""", unsafe_allow_html=True)

if sb_user:
    save_col, _ = st.columns([1,3])
    with save_col:
        if st.button("💾 Save Session to History", use_container_width=True):
            try:
                sb_admin = get_sb_admin()
                _batch_names = [n for n, s in st.session_state.get("file_states", {}).items() if s["status"] == "done"]
                filename = ", ".join(_batch_names) if _batch_names else "session_data.csv"
                hs_all = health_score(S, adf)
                kpis = {
                    "spend": float(S["spend"]), "revenue": float(S["revenue"]),
                    "roas": float(S["roas"]), "ctr": float(S["ctr"]), "cpc": float(S["cpc"]),
                    "conversions": int(S["conversions"]), "impressions": int(S["impressions"]),
                    "health_score": int(hs_all), "campaigns": int(S["n"]),
                }
                campaign_data = json.loads(df.to_json(orient="records"))
                cache = st.session_state.get("ai_cache", {})
                sb_admin.table("analysis_history").insert({
                    "user_id": sb_user.id,
                    "profile_id": active_profile["id"] if active_profile else None,
                    "filename": filename,
                    "kpis": kpis,
                    "campaign_data": campaign_data,
                    "ai_brief": cache.get("brief_all", ""),
                    "ai_anomaly": cache.get("anomaly_all", ""),
                    "ai_recs": cache.get("recs_all", ""),
                    "ai_forecast": cache.get("forecast_all", ""),
                    "ai_bench": cache.get("bench_all", ""),
                    "chat_transcript": st.session_state.get("chat", []),
                }).execute()
                st.success("Saved — view it under the History tab.")
            except Exception as e:
                st.error(f"Could not save to history: {e}")
    st.caption("Saves whatever's been generated with 'All platforms' selected on each tab, plus your chat — sections not yet generated are simply skipped.")

st.markdown('<div class="div"></div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB NAVIGATION
# ──────────────────────────────────────────────────────────────
tabs = st.tabs(["🤖 AI Brief", "📈 Performance", "🚨 Anomalies", "💡 Recommendations",
                "🔮 Forecast", "🎨 Creative AI", "🏁 Benchmark", "💬 AI Chat", "🕘 History"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — AI EXECUTIVE BRIEF
# ══════════════════════════════════════════════════════════════
def render_brief_cards(S, hs, high):
    hcol1, hcol2 = st.columns([1,3])
    with hcol1:
        color = "#10B981" if hs>=70 else "#F59E0B" if hs>=40 else "#EF4444"
        st.markdown(f"""
        <div class="kcard" style="text-align:center;padding:1.5rem 1rem">
          <div class="klabel">Portfolio Health</div>
          <div style="font-size:52px;font-weight:800;color:{color};line-height:1">{hs}</div>
          <div style="font-size:13px;color:#64748B;margin-top:4px">out of 100</div>
          <div style="margin-top:8px;font-size:12px;color:{color}">
            {"🟢 Excellent" if hs>=70 else "🟡 Needs Attention" if hs>=40 else "🔴 Critical"}
          </div>
        </div>""", unsafe_allow_html=True)
    with hcol2:
        col_a, col_b, col_c, col_d = st.columns(4)
        for c, lbl, val, cls in [
            (col_a, "Best Campaign",    S["best"][:25],           "neu"),
            (col_b, "Top Channel",      S["top_ch"],              "up"),
            (col_c, "Critical Issues",  str(high),                "down" if high else "up"),
            (col_d, "Campaigns",        str(S["n"]),              "neu"),
        ]:
            with c:
                st.markdown(f"""
                <div class="kcard">
                  <div class="klabel">{lbl}</div>
                  <div class="kval" style="font-size:18px">{val}</div>
                </div>""", unsafe_allow_html=True)

@st.fragment
def brief_tab():
    st.markdown('<div class="sh">🤖 AI Executive Brief</div>', unsafe_allow_html=True)
    b_df, b_tag = platform_filter(df, "brief")
    b_key = f"brief_{b_tag}"
    cache = st.session_state.setdefault("ai_cache", {})

    if not client:
        st.info("🔑 Add Claude API key to generate AI Executive Brief")
    elif b_key in cache:
        b_S   = summary(b_df)
        b_adf = anomalies(b_df)
        b_high = len(b_adf[b_adf["severity"]=="HIGH"])
        b_hs  = health_score(b_S, b_adf)
        render_brief_cards(b_S, b_hs, b_high)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="aibox"><div class="aihdr">✅ Executive Brief</div>'
                    f'<div class="aibody">{cache[b_key]}</div></div>', unsafe_allow_html=True)
    else:
        if st.button("⚡ Generate Executive Brief", key=f"gen_{b_key}", use_container_width=True):
            b_S   = summary(b_df)
            b_adf = anomalies(b_df)
            b_high = len(b_adf[b_adf["severity"]=="HIGH"])
            b_hs  = health_score(b_S, b_adf)
            top3   = b_df.nlargest(3,"roas")[["campaign_name","channel","roas"]].to_dict("records")
            bot3   = b_df.nsmallest(3,"roas")[["campaign_name","channel","roas"]].to_dict("records")
            prompt = f"""
Analyse {client_label}'s digital marketing portfolio:
{profile_context_block()}
PORTFOLIO METRICS:
- Campaigns: {b_S['n']} across brands: {', '.join(b_S['brands'])}
- Total Spend: {inr(b_S['spend'])} | Revenue: {inr(b_S['revenue'])} | ROAS: {b_S['roas']:.2f}x
- Avg CTR: {b_S['ctr']:.2f}% | Avg CPC: ₹{b_S['cpc']:.2f}
- Portfolio Health Score: {b_hs}/100
- Critical anomalies: {b_high} campaigns losing money

TOP 3 PERFORMERS: {json.dumps(top3)}
BOTTOM 3 PERFORMERS: {json.dumps(bot3)}
TOP CHANNEL: {b_S['top_ch']}

AUDIENCE: {"Brand manager / client — focus on business outcomes, ROI, brand growth." if is_client else "Internal marketing analyst — include tactical details, anomaly causes, specific optimisation actions."}

Write a sharp executive brief with exactly 3 sections. Use bullet points, not paragraphs —
every line must be a short, specific, standalone point a reader can scan in seconds:
1. PORTFOLIO HEALTH — 3-4 bullets, overall assessment with key metrics in context
2. WINS — 2-3 bullets, what is working and why, with specific campaign names and numbers
3. URGENT ACTIONS — exactly 2 bullets, one action each, with expected revenue impact

Each bullet: lead with the specific number or campaign name, one sentence max. No filler, no restating the question.
"""
            generate_and_cache(b_key, prompt, "Executive Brief", client)

with tabs[0]:
    brief_tab()

# ══════════════════════════════════════════════════════════════
# TAB 2 — PERFORMANCE CHARTS
# ══════════════════════════════════════════════════════════════
@st.fragment
def performance_tab():
    st.markdown('<div class="sh">📈 Performance Analytics</div>', unsafe_allow_html=True)
    p_df, p_tag = platform_filter(df, "perf")
    p_S = summary(p_df)

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        ch = p_df.groupby("channel").agg(spend=("spend","sum"), revenue=("revenue","sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Spend",   x=ch["channel"], y=ch["spend"],   marker_color="#6366f1", opacity=.85))
        fig.add_trace(go.Bar(name="Revenue", x=ch["channel"], y=ch["revenue"], marker_color="#34d399", opacity=.85))
        fig.update_layout(**CHART, title="Spend vs Revenue by Channel", barmode="group",
                          legend=dict(orientation="h",y=-0.25), height=320,
                          margin=dict(l=0,r=0,t=40,b=0), xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        fig2 = px.scatter(p_df, x="spend", y="revenue", size="conversions", color="channel",
                          hover_name="campaign_name", title="Spend vs Revenue (bubble = conversions)")
        mn,mx = p_df["spend"].min(), p_df["spend"].max()
        fig2.add_shape(type="line",x0=mn,y0=mn,x1=mx,y1=mx,
                       line=dict(color="rgba(31,41,55,.18)",width=1.5,dash="dot"))
        fig2.update_layout(**CHART, height=320, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        rdf = p_df.sort_values("roas").tail(12)
        colors = ["#f87171" if r<2 else "#fbbf24" if r<5 else "#34d399" for r in rdf["roas"]]
        fig3 = go.Figure(go.Bar(x=rdf["roas"], y=rdf["campaign_name"], orientation="h",
                                marker_color=colors,
                                text=[f"{r:.2f}x" for r in rdf["roas"]], textposition="outside"))
        fig3.update_layout(**CHART, title="ROAS by Campaign (red<2x, amber<5x, green≥5x)",
                           height=380, margin=dict(l=0,r=70,t=40,b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with r2c2:
        bdf = p_df.groupby("campaign_name").agg(budget=("budget","sum")).reset_index().sort_values("budget").tail(12)
        fig4 = go.Figure(go.Bar(x=bdf["budget"], y=bdf["campaign_name"], orientation="h",
                                marker_color="#6366f1",
                                text=[inr(v) for v in bdf["budget"]], textposition="outside"))
        fig4.update_layout(**CHART, title="Budget by Campaign (Top 12)",
                           height=380, margin=dict(l=0,r=80,t=40,b=0))
        st.plotly_chart(fig4, use_container_width=True)

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        ch2 = p_df.groupby("channel").agg(ctr=("ctr","mean"), cpc=("cpc","mean"), spend=("spend","sum")).reset_index()
        fig5 = px.scatter(ch2, x="ctr", y="cpc", size="spend", color="channel", text="channel",
                          title="CTR vs CPC by Channel (bubble = spend)")
        fig5.update_traces(textposition="top center")
        fig5.update_layout(**CHART, height=320, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig5, use_container_width=True)

    with r3c2:
        cpa_df = p_df.groupby("channel").agg(conv=("conversions","sum"), spend=("spend","sum")).reset_index()
        cpa_df["cpa"] = cpa_df["spend"] / cpa_df["conv"]
        fig6 = go.Figure(go.Bar(
            x=cpa_df["channel"], y=cpa_df["cpa"],
            marker_color=["#34d399" if c<500 else "#fbbf24" if c<1500 else "#f87171" for c in cpa_df["cpa"]],
            text=[f"₹{c:.0f}" for c in cpa_df["cpa"]], textposition="outside"))
        fig6.update_layout(**CHART, title="Cost Per Acquisition by Channel",
                           height=320, margin=dict(l=0,r=0,t=40,b=0), yaxis_title="CPA (₹)")
        st.plotly_chart(fig6, use_container_width=True)

    # Funnel
    st.markdown('<div class="sh">🔽 Conversion Funnel</div>', unsafe_allow_html=True)
    stages = ["Impressions","Clicks","Conversions"]
    vals   = [p_S["impressions"], p_S["clicks"], p_S["conversions"]]
    fig7 = go.Figure(go.Funnel(y=stages, x=vals,
                                textinfo="value+percent initial",
                                marker_color=["#6366f1","#818cf8","#34d399"]))
    fig7.update_layout(**CHART, title="Full-Funnel Conversion Analysis", height=320,
                       margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig7, use_container_width=True)

with tabs[1]:
    performance_tab()

# ══════════════════════════════════════════════════════════════
# TAB 3 — ANOMALY DETECTION
# ══════════════════════════════════════════════════════════════
def render_anomaly_list(an_S, an_adf, an_high, an_med, an_ok):
    a1,a2,a3 = st.columns(3)
    with a1:
        st.markdown(f'<div class="kcard" style="text-align:center"><div class="klabel">Critical Issues</div><div class="kval" style="color:#EF4444">{an_high}</div><div class="kdelta down">ROAS below 1.0x — losing money</div></div>', unsafe_allow_html=True)
    with a2:
        st.markdown(f'<div class="kcard" style="text-align:center"><div class="klabel">Warnings</div><div class="kval" style="color:#F59E0B">{an_med}</div><div class="kdelta neu">Below portfolio average</div></div>', unsafe_allow_html=True)
    with a3:
        st.markdown(f'<div class="kcard" style="text-align:center"><div class="klabel">Healthy</div><div class="kval" style="color:#10B981">{an_ok}</div><div class="kdelta up">Performing well</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    for _, row in an_adf.sort_values("severity", key=lambda x: x.map({"HIGH":0,"MED":1,"OK":2})).iterrows():
        badge = (f'<span class="ab-h">● CRITICAL</span>' if row["severity"]=="HIGH"
                 else f'<span class="ab-m">● WARNING</span>' if row["severity"]=="MED"
                 else f'<span class="ab-o">● HEALTHY</span>')
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:14px;padding:10px 4px;border-bottom:1px solid rgba(99,102,241,.18)">
          <div style="min-width:100px;padding-top:2px">{badge}</div>
          <div style="flex:1">
            <div style="font-size:13px;font-weight:700;color:#F1F5F9">{row['campaign']}</div>
            <div style="font-size:12px;color:#64748B;margin-top:2px">{row['channel']} · {row['brand']} · ROAS {row['roas']:.2f}x · Spend {inr(row['spend'])}</div>
            <div style="font-size:12px;color:#94A3B8;margin-top:4px">{row['issues']}</div>
          </div>
        </div>""", unsafe_allow_html=True)

@st.fragment
def anomaly_tab():
    st.markdown('<div class="sh">🚨 AI Anomaly Detection</div>', unsafe_allow_html=True)
    an_df, an_tag = platform_filter(df, "anomaly")
    an_key = f"anomaly_{an_tag}"
    cache = st.session_state.setdefault("ai_cache", {})

    an_S    = summary(an_df)
    an_adf  = anomalies(an_df)
    an_high = len(an_adf[an_adf["severity"]=="HIGH"])
    an_med  = len(an_adf[an_adf["severity"]=="MED"])
    an_ok   = len(an_adf[an_adf["severity"]=="OK"])

    if an_high == 0 or not client:
        # Nothing to generate (no critical campaigns, or no AI key) — just show the rule-based list
        render_anomaly_list(an_S, an_adf, an_high, an_med, an_ok)
    elif an_key in cache:
        render_anomaly_list(an_S, an_adf, an_high, an_med, an_ok)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="aibox"><div class="aihdr">✅ Anomaly Root Cause Analysis</div>'
                    f'<div class="aibody">{cache[an_key]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="kcard" style="text-align:center"><div class="klabel">Critical Issues Found</div><div class="kval" style="color:#EF4444">{an_high}</div></div>', unsafe_allow_html=True)
        if st.button("⚡ Generate Anomaly Report", key=f"gen_{an_key}", use_container_width=True):
            critical = an_adf[an_adf["severity"]=="HIGH"][["campaign","channel","roas","spend"]].to_dict("records")
            prompt = f"""
Root cause analysis for {client_label}'s campaign anomalies:
{profile_context_block()}
CRITICAL campaigns (ROAS < 1.0x, losing money): {json.dumps(critical)}
Total portfolio avg ROAS: {an_S['roas']:.2f}x

Use bullet points, not paragraphs — short, specific, scannable lines:
1. ROOT CAUSES — 3-4 bullets, one cause each (channel characteristics, audience targeting, creative fatigue, bidding issues), naming the specific campaign it applies to
2. RESCUE PLAN for {an_adf[an_adf['severity']=='HIGH']['campaign'].iloc[0]} — exactly 3 numbered bullets, one tactic each, with expected ROAS improvement timeline

Each bullet: one sentence max, lead with the specific number or campaign name. No filler.
"""
            generate_and_cache(an_key, prompt, "Anomaly Root Cause Analysis", client)

with tabs[2]:
    anomaly_tab()

# ══════════════════════════════════════════════════════════════
# TAB 4 — AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════
@st.fragment
def recommendations_tab():
    st.markdown('<div class="sh">💡 AI Budget Reallocation Recommendations</div>', unsafe_allow_html=True)
    r_df, r_tag = platform_filter(df, "recs")
    r_S   = summary(r_df)
    r_adf = anomalies(r_df)

    r_key = f"recs_{r_tag}"
    cache = st.session_state.setdefault("ai_cache", {})
    if not client:
        st.info("🔑 Add Claude API key to generate AI budget recommendations")
    elif r_key in cache:
        st.markdown(f'<div class="aibox"><div class="aihdr">✅ Budget Recommendations</div>'
                    f'<div class="aibody">{cache[r_key]}</div></div>', unsafe_allow_html=True)
    else:
        if st.button("⚡ Generate Budget Recommendations", key=f"gen_{r_key}", use_container_width=True):
            poor = r_adf[r_adf["severity"]=="HIGH"][["campaign","channel","roas","spend"]].to_dict("records")
            good = r_df.nlargest(3,"roas")[["campaign_name","channel","roas","spend"]].to_dict("records")
            ch_roas = r_df.groupby("channel")["roas"].mean().to_dict()
            prompt = f"""
Budget reallocation strategy for {client_label}'s digital marketing:
{profile_context_block()}
TOTAL PORTFOLIO SPEND: {inr(r_S['spend'])}
CHANNEL ROAS: {json.dumps({k:round(v,2) for k,v in ch_roas.items()})}
POOR PERFORMERS: {json.dumps(poor)}
TOP PERFORMERS: {json.dumps(good)}

AUDIENCE: {"Client brand manager — focus on business ROI and brand outcomes." if is_client else "Internal analyst — include specific bid strategy changes and channel tactics."}

Provide exactly 5 numbered budget recommendations as short bullet points, not paragraphs. Format each as:
**[CAMPAIGN/CHANNEL]:** [Specific action with ₹ amount or % shift] — [one line of reasoning with a projected impact number]

Use actual campaign names and real numbers from the data. One bullet, one line each — no multi-sentence explanations.
"""
            generate_and_cache(r_key, prompt, "Budget Recommendations", client)

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sh">📊 Channel Efficiency Matrix</div>', unsafe_allow_html=True)

    ch_matrix = r_df.groupby("channel").agg(
        spend=("spend","sum"), revenue=("revenue","sum"),
        roas=("roas","mean"), ctr=("ctr","mean"),
        conversions=("conversions","sum"), campaigns=("campaign_name","count")
    ).reset_index()
    ch_matrix["cpa"] = ch_matrix["spend"] / ch_matrix["conversions"]
    ch_matrix["profit"] = ch_matrix["revenue"] - ch_matrix["spend"]

    fig_m = px.scatter(ch_matrix, x="roas", y="ctr", size="spend", color="channel",
                       text="channel", title="Channel Efficiency: ROAS vs CTR (bubble = total spend)",
                       labels={"roas":"Average ROAS","ctr":"Average CTR (%)"})
    fig_m.update_traces(textposition="top center")
    fig_m.add_vline(x=ch_matrix["roas"].mean(), line_dash="dot", line_color="rgba(31,41,55,.2)")
    fig_m.add_hline(y=ch_matrix["ctr"].mean(), line_dash="dot", line_color="rgba(31,41,55,.2)")
    fig_m.update_layout(**CHART, height=400, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig_m, use_container_width=True)

with tabs[3]:
    recommendations_tab()

# ══════════════════════════════════════════════════════════════
# TAB 5 — FORECAST
# ══════════════════════════════════════════════════════════════
@st.fragment
def forecast_tab():
    st.markdown('<div class="sh">🔮 30-Day Revenue Forecast</div>', unsafe_allow_html=True)
    f_df, f_tag = platform_filter(df, "forecast")

    fc1, fc2 = st.columns([1,2])
    ch_roas_map = f_df.groupby("channel")["roas"].mean().to_dict()
    g_roas = ch_roas_map.get("Google Ads", 7.0)
    m_roas = ch_roas_map.get("Meta Ads", 4.5)
    y_roas = ch_roas_map.get("YouTube Ads", 10.0)
    i_roas = ch_roas_map.get("Instagram Ads", 4.8)
    o_roas = sum(v for k,v in ch_roas_map.items() if k not in ["Google Ads","Meta Ads","YouTube Ads","Instagram Ads"]) / max(1,len([k for k in ch_roas_map if k not in ["Google Ads","Meta Ads","YouTube Ads","Instagram Ads"]]))

    with fc1:
        budget_in = st.number_input("Next 30-day budget (₹)", min_value=50000,
                                     max_value=50000000, value=1000000, step=50000)
        st.markdown('<p style="font-size:12px;color:#94A3B8;margin-bottom:4px">Channel mix (%)</p>', unsafe_allow_html=True)
        g_pct = st.slider(f"Google Ads (ROAS {g_roas:.1f}x)",  0, 100, 40)
        m_pct = st.slider(f"Meta Ads (ROAS {m_roas:.1f}x)",    0, 100, 25)
        y_pct = st.slider(f"YouTube Ads (ROAS {y_roas:.1f}x)", 0, 100, 20)
        i_pct = st.slider(f"Instagram (ROAS {i_roas:.1f}x)",   0, 100, 10)
        o_pct = max(0, 100 - g_pct - m_pct - y_pct - i_pct)
        st.markdown(f'<p style="font-size:12px;color:#64748B">Other channels: {o_pct}%</p>', unsafe_allow_html=True)

        proj_rev  = (budget_in*g_pct/100*g_roas + budget_in*m_pct/100*m_roas +
                     budget_in*y_pct/100*y_roas + budget_in*i_pct/100*i_roas +
                     budget_in*o_pct/100*o_roas)
        proj_roas = proj_rev/budget_in if budget_in else 0
        proj_profit = proj_rev - budget_in

        # Deterministic conversions/CPL projection — same channel-mix-weighted method as
        # the revenue projection above, just using historical CPA instead of ROAS.
        ch_cpa_map = {}
        for ch_name, d in f_df.groupby("channel"):
            conv = d["conversions"].sum()
            ch_cpa_map[ch_name] = (d["spend"].sum()/conv) if conv else None
        blended_conv, blended_spend = f_df["conversions"].sum(), f_df["spend"].sum()
        blended_cpa = (blended_spend/blended_conv) if blended_conv else None
        def _cpa(name): return ch_cpa_map.get(name) or blended_cpa
        def _alloc_conv(pct, cpa): return (budget_in*pct/100)/cpa if cpa else 0
        other_names = [k for k in ch_cpa_map if k not in ["Google Ads","Meta Ads","YouTube Ads","Instagram Ads"]]
        o_cpa = (sum(ch_cpa_map[k] for k in other_names if ch_cpa_map[k]) / max(1, len([k for k in other_names if ch_cpa_map[k]]))) or blended_cpa

        proj_conversions = (_alloc_conv(g_pct,_cpa("Google Ads")) + _alloc_conv(m_pct,_cpa("Meta Ads")) +
                            _alloc_conv(y_pct,_cpa("YouTube Ads")) + _alloc_conv(i_pct,_cpa("Instagram Ads")) +
                            _alloc_conv(o_pct,o_cpa))
        proj_cpl = (budget_in/proj_conversions) if proj_conversions else None

        st.markdown(f"""
        <div class="kcard" style="margin-top:1rem">
          <div class="klabel">Projected Revenue</div>
          <div class="kval">{inr(proj_rev)}</div>
          <div class="kdelta up">Est. ROAS: {proj_roas:.2f}x</div>
        </div>
        <div class="kcard" style="margin-top:.75rem">
          <div class="klabel">Projected Profit</div>
          <div class="kval">{inr(proj_profit)}</div>
          <div class="kdelta {'up' if proj_profit>0 else 'down'}">Net return on ad spend</div>
        </div>
        <div class="kcard" style="margin-top:.75rem">
          <div class="klabel">Projected Conversions</div>
          <div class="kval">{int(proj_conversions):,}</div>
          <div class="kdelta neu">Blended historical CPA: {inr(blended_cpa) if blended_cpa else '—'}</div>
        </div>
        <div class="kcard" style="margin-top:.75rem">
          <div class="klabel">Projected Cost / Conversion</div>
          <div class="kval">{inr(proj_cpl) if proj_cpl else '—'}</div>
          <div class="kdelta neu">Weighted by planned channel mix</div>
        </div>""", unsafe_allow_html=True)

    with fc2:
        days = list(range(1,31))
        c_spend = [budget_in*d/30 for d in days]
        c_rev   = [budget_in*d/30*proj_roas*(1+0.04*math.sin(d/2.5)) for d in days]

        fig_f = go.Figure()
        fig_f.add_trace(go.Scatter(x=days, y=c_spend, name="Cumulative Spend",
            line=dict(color="#EF4444",width=2), fill="tozeroy", fillcolor="rgba(239,68,68,.12)"))
        fig_f.add_trace(go.Scatter(x=days, y=c_rev, name="Projected Revenue",
            line=dict(color="#10B981",width=2.5), fill="tozeroy", fillcolor="rgba(16,185,129,.12)"))
        fig_f.update_layout(**CHART, title="30-Day Forecast — Projected Spend vs Revenue",
                            xaxis_title="Day", yaxis_title="₹", height=380,
                            margin=dict(l=0,r=0,t=40,b=0),
                            legend=dict(orientation="h",y=-0.28))
        st.plotly_chart(fig_f, use_container_width=True)

    f_key = f"forecast_{f_tag}"
    cache = st.session_state.setdefault("ai_cache", {})
    if not client:
        st.info("🔑 Add Claude API key to generate forecast intelligence")
    elif f_key in cache:
        st.markdown(f'<div class="aibox"><div class="aihdr">✅ Forecast Intelligence</div>'
                    f'<div class="aibody">{cache[f_key]}</div></div>', unsafe_allow_html=True)
    else:
        if st.button("⚡ Generate Forecast Intelligence", key=f"gen_{f_key}", use_container_width=True):
            prompt = f"""
30-day forecast analysis for {client_label}'s campaign portfolio:
{profile_context_block()}
BUDGET: {inr(budget_in)}
CHANNEL MIX: Google {g_pct}%, Meta {m_pct}%, YouTube {y_pct}%, Instagram {i_pct}%, Other {o_pct}%
PROJECTED REVENUE: {inr(proj_rev)}
PROJECTED ROAS: {proj_roas:.2f}x
PROJECTED PROFIT: {inr(proj_profit)}
HISTORICAL CHANNEL ROAS: {json.dumps({k:round(v,2) for k,v in ch_roas_map.items()})}

Use bullet points, not paragraphs — short, specific, scannable lines:
1. IS THIS MIX OPTIMAL? — 2-3 bullets comparing to historical performance, stating what the data predicts
2. RECOMMENDED ADJUSTMENT — exactly 1 bullet with exact % numbers that would increase projected ROAS by at least 15%, plus one line of reasoning

Each bullet: one sentence max, lead with the number.
"""
            generate_and_cache(f_key, prompt, "Forecast Intelligence", client)

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sh">🌐 Gemini Market Forecast</div>', unsafe_allow_html=True)
    st.caption("Market & competitor trends are reasoned from Gemini's trained knowledge — not live search or paid trend-data APIs.")

    market_context = st.text_area(
        "Add market context (optional)",
        placeholder="e.g. upcoming festive season, a new competitor launch, a planned promo...",
        key="forecast_market_context")

    rep1, rep2, rep3 = st.columns(3)
    with rep1:
        with st.expander("🔑 Keyword report (optional)"):
            kw_df = optional_report_upload(
                "Upload keyword report",
                "Google Ads / Bing keyword report — Keyword, Avg. position, Quality Score, Landing page experience, Impr., Clicks, Cost, Conversions.",
                "kw_report", KEYWORD_FIELDS, KEYWORD_NUMERIC, client)
    with rep2:
        with st.expander("📶 Impression share report (optional)"):
            is_df = optional_report_upload(
                "Upload impression share / auction insights report",
                "Google Ads campaign or auction-insights export — Impr. share, Impr. share lost (rank), Impr. share lost (budget), competitor overlap/outranking share.",
                "is_report", IMPRESSION_SHARE_FIELDS, IMPRESSION_SHARE_NUMERIC, client)
    with rep3:
        with st.expander("👥 Audience report (optional)"):
            aud_df = optional_report_upload(
                "Upload audience report",
                "Audience/demographics export — Segment, Age, Gender, Device, Impr., Clicks, Conversions, Spend.",
                "aud_report", AUDIENCE_FIELDS, AUDIENCE_NUMERIC, client)

    kw_summary = None
    if kw_df is not None and len(kw_df):
        d = kw_df
        kw_summary = {
            "keywords_analyzed": len(d),
            "avg_quality_score": round(d["quality_score"].mean(),1) if "quality_score" in d else None,
            "lowest_quality_keywords": d.nsmallest(5,"quality_score")[[c for c in ["keyword","quality_score","avg_position"] if c in d.columns]].to_dict("records") if "quality_score" in d and "keyword" in d else [],
            "top_converting_keywords": d.nlargest(5,"conversions")[[c for c in ["keyword","conversions","cost"] if c in d.columns]].to_dict("records") if "conversions" in d and "keyword" in d else [],
            "poor_landing_page_keywords": d[d["landing_page_experience"].astype(str).str.contains("below average", case=False, na=False)]["keyword"].tolist()[:5] if "landing_page_experience" in d and "keyword" in d else [],
            "avg_position": round(d["avg_position"].mean(),1) if "avg_position" in d else None,
        }

    is_summary = None
    if is_df is not None and len(is_df):
        d = is_df
        is_summary = {
            "avg_impression_share_pct": round(d["impression_share"].mean(),1) if "impression_share" in d else None,
            "avg_lost_to_rank_pct": round(d["is_lost_rank"].mean(),1) if "is_lost_rank" in d else None,
            "avg_lost_to_budget_pct": round(d["is_lost_budget"].mean(),1) if "is_lost_budget" in d else None,
            "biggest_share_opportunities": d.nsmallest(5,"impression_share")[[c for c in ["campaign_name","impression_share"] if c in d.columns]].to_dict("records") if "impression_share" in d and "campaign_name" in d else [],
            "competitor_rows": d[[c for c in ["competitor","overlap_rate","outranking_share"] if c in d.columns]].to_dict("records") if "competitor" in d else [],
        }

    aud_summary = None
    if aud_df is not None and len(aud_df):
        d = aud_df.copy()
        seg_cols = [c for c in ["segment","age","gender","device"] if c in d.columns]
        aud_summary = {
            "best_segments_by_conversions": d.nlargest(5,"conversions")[seg_cols+["conversions"]].to_dict("records") if "conversions" in d and seg_cols else [],
            "highest_spend_zero_conversion_segments": (d[d.get("conversions",1)==0].nlargest(5,"spend")[seg_cols+["spend"]].to_dict("records")
                if "spend" in d and "conversions" in d and seg_cols else []),
        }

    yoy_this = yoy_last = None
    if "date" in f_df.columns and f_df["date"].notna().any():
        years = sorted(f_df["date"].dt.year.dropna().unique().tolist())
        if len(years) >= 2:
            latest_year, prior_year = years[-1], years[-2]
            this_yr_df = f_df[f_df["date"].dt.year == latest_year]
            last_yr_df = f_df[f_df["date"].dt.year == prior_year]
            max_doy = this_yr_df["date"].dt.dayofyear.max()
            last_yr_df = last_yr_df[last_yr_df["date"].dt.dayofyear <= max_doy]
            def _yr_summary(d):
                sp, rv = d["spend"].sum(), d["revenue"].sum()
                return {
                    "spend": round(sp, 2), "revenue": round(rv, 2),
                    "conversions": int(d["conversions"].sum()),
                    "roas": round(rv/sp, 2) if sp else 0,
                    "roas_by_channel": {k: round(v, 2) for k, v in d.groupby("channel")["roas"].mean().to_dict().items()},
                }
            if len(this_yr_df) and len(last_yr_df):
                yoy_this, yoy_last = _yr_summary(this_yr_df), _yr_summary(last_yr_df)

    gem_key = f"gemini_forecast_{f_tag}"
    gem_cache = st.session_state.setdefault("ai_cache", {})
    gemini_client = get_gemini_client()
    if not gemini_client:
        st.info("🔑 Add OPENROUTER_API_KEY in .env to generate the Gemini market forecast")
    elif gem_key in gem_cache:
        st.markdown(f'<div class="aibox"><div class="aihdr">🌐 Gemini Market Forecast</div>'
                    f'<div class="aibody">{gem_cache[gem_key]}</div></div>', unsafe_allow_html=True)
    else:
        if st.button("🔮 Generate Gemini Market Forecast", key=f"gen_{gem_key}", use_container_width=True):
            goal_text = active_profile.get("goal") if active_profile else "Not specified"
            industry_text = active_profile.get("industry") if active_profile else "Not specified"
            description_text = active_profile.get("description") if active_profile else "Not specified"

            yoy_block = (
                f"THIS YEAR (same period so far): {json.dumps(yoy_this)}\nLAST YEAR (same period): {json.dumps(yoy_last)}"
                if yoy_this and yoy_last else
                "No prior-year data available in the uploaded file for a fair year-over-year comparison — skip it and say so plainly, don't invent one."
            )
            kw_block = (f"KEYWORD PERFORMANCE DATA: {json.dumps(kw_summary, default=str)}" if kw_summary
                        else "No keyword report was provided — skip keyword rank/quality-score/landing-page specifics, don't invent them.")
            is_block = (f"IMPRESSION SHARE DATA: {json.dumps(is_summary, default=str)}" if is_summary
                        else "No impression-share/auction-insights report was provided — skip impression-share and competitor-overlap specifics, don't invent them.")
            aud_block = (f"AUDIENCE SEGMENT DATA: {json.dumps(aud_summary, default=str)}" if aud_summary
                         else "No audience report was provided — base the audience recommendation on the client's industry/description/goal instead of segment-level data.")
            kpi_block = f"""PYTHON-CALCULATED PROJECTION (use these exact numbers verbatim in section 2 — do not recompute or alter them, just explain/contextualize them):
- Projected revenue: {inr(proj_rev)} (ROAS {proj_roas:.2f}x)
- Projected profit: {inr(proj_profit)}
- Projected conversions: {int(proj_conversions):,}
- Projected cost per conversion: {inr(proj_cpl) if proj_cpl else "not calculable — no historical conversions in the data"}
- Blended historical cost per conversion: {inr(blended_cpa) if blended_cpa else "not available"}"""

            prompt = f"""You are a marketing expert who helps businesses analyze market trends, predict performance, and adapt their ad campaigns. Your job is to look at our historical data and current live trends for an upcoming month to predict our performance and give us a strategy.

Structure your answer using these four clear sections, in this order:

1. Market and Competitor Trends
- Recommend the target audience this client's service/product should focus on — use the audience segment data if given, otherwise reason from their industry/description/goal.
- Cover keyword performance: quality score, average rank/position, landing page experience — using KEYWORD PERFORMANCE DATA if provided.
- Cover impression share: current share, how much is being lost to rank vs. lost to budget, what that split means, and concrete steps to recover lost share — using IMPRESSION SHARE DATA if provided. If competitor rows are present, comment on how competitors are performing (overlap rate / outranking share).
- Cover general market/seasonal/industry trends. You do not have live search access — for this general-trends part only, reason from trained knowledge and say so briefly; do NOT caveat the keyword/impression-share/audience findings this way since those come from the client's real uploaded data.

2. KPI Predictions
Present the PYTHON-CALCULATED PROJECTION numbers below exactly as given — these are the "what we will be able to deliver" figures, not estimates you invent. Compare them plainly against the historical portfolio numbers (CURRENT PORTFOLIO ROAS BY CHANNEL, blended cost per conversion) so it's clear whether this projection is an improvement or decline and why.

3. Past Wins and Losses
Look at our past data for this same time period or season (use the YEAR-OVER-YEAR DATA below if present). Tell us what tactics worked well last time that we should repeat, and what failed or wasted budget that we must avoid.

4. Seasonal Pivot and Campaign Adjustments
If the data shows our primary service or product will drop due to seasonal factors, weather, or market shifts, give us an immediate backup plan. Tell us what alternative services or products to push to fill the revenue gap, what keywords to target for them, what ad angles to use, and how to shift our budget.

CLIENT: {client_label}
INDUSTRY: {industry_text}
DESCRIPTION: {description_text}
PRIMARY GOAL(S): {goal_text}
NEXT-PERIOD BUDGET: {inr(budget_in)}, PLANNED CHANNEL MIX: Google {g_pct}%, Meta {m_pct}%, YouTube {y_pct}%, Instagram {i_pct}%, Other {o_pct}%
CURRENT PORTFOLIO ROAS BY CHANNEL: {json.dumps({k: round(v,2) for k,v in ch_roas_map.items()})}
{kpi_block}
YEAR-OVER-YEAR DATA: {yoy_block}
{kw_block}
{is_block}
{aud_block}
USER-PROVIDED MARKET CONTEXT: {market_context or "None provided"}

Use bullet points under each of the 4 numbered section headers above, not paragraphs — short, specific, scannable lines, leading with numbers where relevant."""
            generate_and_cache(gem_key, prompt, "Gemini Market Forecast", gemini_client, model=GEMINI_MODEL)

with tabs[4]:
    forecast_tab()

# ══════════════════════════════════════════════════════════════
# TAB 6 — CREATIVE AI
# ══════════════════════════════════════════════════════════════
@st.fragment
def creative_tab():
    st.markdown('<div class="sh">🎨 Creative Intelligence & Copy Generator</div>', unsafe_allow_html=True)
    c_df, c_tag = platform_filter(df, "creative")

    if client:
        cr_sel = st.selectbox("Select campaign to analyse", c_df["campaign_name"].tolist())
        cr_row = c_df[c_df["campaign_name"]==cr_sel].iloc[0]

        r1,r2,r3,r4 = st.columns(4)
        for col,lbl,val in [
            (r1,"Channel",cr_row["channel"]),
            (r2,"ROAS",f"{cr_row['roas']:.2f}x"),
            (r3,"CTR",f"{cr_row['ctr']:.2f}%"),
            (r4,"Status",cr_row["status"]),
        ]:
            with col:
                st.markdown(f'<div class="kcard"><div class="klabel">{lbl}</div><div class="kval" style="font-size:18px">{val}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        cr_type = st.radio("What do you need?", [
            "📝 Ad Copy Variations",
            "🎯 Audience Targeting Refinements",
            "🖼 Creative Format Recommendations",
        ], horizontal=True)

        cr_key = f"creative_{cr_sel}_{cr_type}"
        cache = st.session_state.setdefault("ai_cache", {})

        if cr_key in cache:
            st.markdown(f'<div class="aibox"><div class="aihdr">✅ Creative AI — {cr_type}</div>'
                        f'<div class="aibody">{cache[cr_key]}</div></div>', unsafe_allow_html=True)
        else:
            if st.button("⚡ Generate with AI", key="cr_btn", use_container_width=True):
                perf  = ("POOR — losing money, ROAS below 1x" if cr_row["roas"]<1
                         else "AVERAGE — below portfolio norm" if cr_row["roas"]<4
                         else "STRONG — top performer")

                prompts = {
                    "📝 Ad Copy Variations": f"""
Generate ad copy for campaign "{cr_sel}":
Channel: {cr_row['channel']} | Brand: {cr_row['brand']} | Performance: {perf}
CTR: {cr_row['ctr']:.2f}% | ROAS: {cr_row['roas']:.2f}x
{profile_context_block()}
Create:
1. THREE headline variations optimised for {cr_row['channel']} (include character count for each)
2. TWO description/body copy variations (with CTAs)
3. ONE A/B test recommendation with hypothesis

Make them specific to {cr_row['brand']} and the Indian market.
""",
                    "🎯 Audience Targeting Refinements": f"""
Audience targeting strategy for campaign "{cr_sel}":
Channel: {cr_row['channel']} | Brand: {cr_row['brand']} | CTR: {cr_row['ctr']:.2f}% | ROAS: {cr_row['roas']:.2f}x
{profile_context_block()}
Provide:
1. THREE specific audience segments to add or refine on {cr_row['channel']} for Indian market
2. TWO audience segments to exclude (negative targeting) with reasoning
3. Recommended lookalike or similar audience strategy with expected CTR improvement
""",
                    "🖼 Creative Format Recommendations": f"""
Creative format strategy for campaign "{cr_sel}":
Channel: {cr_row['channel']} | Brand: {cr_row['brand']} | Performance: {perf}
{profile_context_block()}
Recommend:
1. Best performing ad format for {cr_row['channel']} in 2024-25 with specific dimensions
2. Video vs static recommendation with reasoning based on the channel and brand
3. Specific creative elements (colours, tone, CTA style) that work for {cr_row['brand']} in India
""",
                }
                generate_and_cache(cr_key, prompts[cr_type], f"Creative AI — {cr_type}", client)
    else:
        st.info("🔑 Add Claude API key to use Creative AI")

with tabs[5]:
    creative_tab()

# ══════════════════════════════════════════════════════════════
# TAB 7 — COMPETITIVE BENCHMARKING
# ══════════════════════════════════════════════════════════════
@st.fragment
def benchmark_tab():
    st.markdown('<div class="sh">🏁 Competitive Benchmarking</div>', unsafe_allow_html=True)
    bn_df, bn_tag = platform_filter(df, "bench")
    bn_S = summary(bn_df)

    bn_key = f"bench_{bn_tag}"
    cache = st.session_state.setdefault("ai_cache", {})
    if not client:
        st.info("🔑 Add Claude API key to generate competitive benchmarking")
    elif bn_key in cache:
        st.markdown(f'<div class="aibox"><div class="aihdr">✅ Competitive Benchmark Analysis</div>'
                    f'<div class="aibody">{cache[bn_key]}</div></div>', unsafe_allow_html=True)
    else:
        if st.button("⚡ Generate Competitive Benchmark", key=f"gen_{bn_key}", use_container_width=True):
            prompt = f"""
Competitive benchmark analysis for {client_label}'s digital marketing (India market, 2024-2025):
{profile_context_block()}
OUR PERFORMANCE:
- Overall ROAS: {bn_S['roas']:.2f}x
- Avg CTR: {bn_S['ctr']:.2f}%
- Avg CPC: ₹{bn_S['cpc']:.2f}
- Channels used: {', '.join(bn_S['channels'])}
- Brands: {', '.join(bn_S['brands'])}

Provide a competitive benchmark as short bullet points, not paragraphs — every bullet under 20 words, leading with the number:

1. ROAS COMPARISON — 2-3 bullets, our {bn_S['roas']:.2f}x ROAS vs Indian industry benchmarks by sector (use real published benchmarks you know for e-commerce, insurance, automotive, health/pharma)

2. CTR & CPC BENCHMARKS — 2 bullets comparing our {bn_S['ctr']:.2f}% CTR and ₹{bn_S['cpc']:.2f} CPC to channel averages in India

3. CHANNEL GAPS — 2 bullets naming specific channels we're underutilising and why

4. EMERGING OPPORTUNITY — 1 bullet naming one specific emerging tactic (CTV, WhatsApp Commerce, vernacular video, influencer marketing) with a pilot recommendation

Be specific with numbers. 250 words max total.
"""
            generate_and_cache(bn_key, prompt, "Competitive Benchmark Analysis", client)

with tabs[6]:
    benchmark_tab()

# ══════════════════════════════════════════════════════════════
# TAB 8 — AI CHAT
# ══════════════════════════════════════════════════════════════
@st.fragment
def chat_tab():
    st.markdown('<div class="sh">💬 AI Analyst Chat</div>', unsafe_allow_html=True)
    ch_df, ch_tag = platform_filter(df, "chat")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    # Existing conversation, rendered as real chat bubbles
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"], avatar="⚡" if msg["role"]=="assistant" else None):
            st.markdown(msg["content"])

    # Quick questions — only before the conversation starts
    new_msg = None
    if not st.session_state.chat:
        st.caption("Quick questions:")
        qs = [
            "Which campaign should I pause and why?",
            "Compare Google Ads vs Meta Ads",
            "Best channel for Tata Motors?",
            "How to improve ROAS by 20%?",
            "Which brand has best efficiency?",
            "What's my conversion rate by channel?",
        ]
        cols = st.columns(3)
        for i, q in enumerate(qs):
            with cols[i % 3]:
                if st.button(q, key=f"sq_{i}", use_container_width=True):
                    new_msg = q

    typed = st.chat_input("Ask anything about your campaigns…")
    if typed:
        new_msg = typed

    if new_msg:
        st.session_state.chat.append({"role":"user","content":new_msg})
        with st.chat_message("user"):
            st.markdown(new_msg)
        with st.chat_message("assistant", avatar="⚡"):
            ph = st.empty()
            if client:
                ans = chat_reply(client, ch_df, st.session_state.chat, ph, max_tokens=500,
                                 style="Be specific, reference actual campaign names and numbers. Max 250 words.")
            else:
                ans = "⚠️ Add a Claude API key in the sidebar to chat with the AI analyst."
                ph.markdown(ans)
        st.session_state.chat.append({"role":"assistant","content":ans})
        st.rerun(scope="fragment")  # re-render so the input box lands below this exchange, not sandwiched above it

    if st.session_state.chat:
        if st.button("🗑 Clear Chat"):
            st.session_state.chat = []
            st.rerun(scope="fragment")

with tabs[7]:
    chat_tab()

# ══════════════════════════════════════════════════════════════
# TAB 9 — HISTORY
# ══════════════════════════════════════════════════════════════
with tabs[8]:
    render_history_section()

# FOOTER
st.markdown("""
<div style="text-align:center;padding:2rem 0 .5rem;font-size:12px;color:#D1D5DB">
  ⚡ CampaignIQ · MATRIX Hackathon 2026 · LS Digital Group · Powered by Anthropic Claude AI
</div>""", unsafe_allow_html=True)
