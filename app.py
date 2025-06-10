import streamlit as st
import time
from config.config import Config
from cache.token_cache import TokenCache
from fetcher.fetcher import DexscreenerFetcher
from utils.time_utils import time_ago
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="🚀 Newly Launched Tokens Dashboard", layout="wide")

REFRESH_INTERVALS = {
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "6h": 21600,
    "1D": 3600*24,
    "7D": 604800
}

# ---- Sidebar ----
refresh_choice = st.sidebar.selectbox("Refresh dashboard every:", list(REFRESH_INTERVALS.keys()), index=0)
selected_interval = REFRESH_INTERVALS[refresh_choice]

# Auto refresh setup (in milliseconds)
st_autorefresh(interval=selected_interval * 1000, key="data_refresh")

# ---- UI Header ----
st.title("🚀 Newly Launched Tokens Dashboard")
st.caption(f"Data from Dexscreener. Auto-refresh dashboard every **{refresh_choice}**")

config = Config()
cache = TokenCache(db_path=config.database_path)
fetcher = DexscreenerFetcher(config.dexscreener_api_url)

if time.time() - cache.last_refresh_time >= selected_interval:
    new_tokens = fetcher.fetch_new_tokens()
    cache.update_tokens(new_tokens)
    cache.last_refresh_time = time.time()

all_tokens = cache.get_tokens()
chain_options = sorted({t['chainId'] for t in all_tokens})
selected_chains = st.sidebar.multiselect("Filter by chain(s)", chain_options, default=chain_options)
time_filter = st.sidebar.selectbox("Show tokens launched in last...", ["All", "5m", "15m", "30m", "1h", "6h", "1D", "7D"])
search_term = st.sidebar.text_input("Search by symbol or keyword")

filtered_tokens = all_tokens
if selected_chains:
    filtered_tokens = [t for t in filtered_tokens if t['chainId'] in selected_chains]

if time_filter != "All":
    now = time.time()
    seconds_limit = REFRESH_INTERVALS.get(time_filter, 300)
    filtered_tokens = [t for t in filtered_tokens if now - t['fetched_at'] <= seconds_limit]

if search_term:
    search_term = search_term.lower()
    filtered_tokens = [t for t in filtered_tokens if search_term in t.get("description", "").lower() or search_term in t['tokenAddress'].lower()]

# Sort newest to oldest
filtered_tokens = sorted(filtered_tokens, key=lambda x: x['fetched_at'], reverse=True)

for token in filtered_tokens:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(token.get("icon"), width=64)
    with col2:
        st.subheader(f"[{token['tokenAddress'][:6]}...]({token['url']})")
        st.markdown(f"**Chain:** `{token['chainId']}` | **Launched:** {time_ago(token['fetched_at'])}")
        st.markdown(token.get("description", "No description"))
        if token.get("links"):
            links = " | ".join([f"[{l.get('label', l.get('type', 'link'))}]({l['url']})" for l in token['links']])
            st.markdown(links)

if not filtered_tokens:
    st.info("No tokens match your filters yet. Waiting for new launches...")
