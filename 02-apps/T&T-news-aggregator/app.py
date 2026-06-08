import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TT News Hub",
    page_icon="🇹🇹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=DM+Sans:wght@400;600&display=swap');
 
/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
 
/* Hide default Streamlit header chrome */
#MainMenu, footer, header {visibility: hidden;}
 
/* App background */
.stApp {
    background-color: #F5F0E8;
}
 
/* Masthead */
.masthead {
    background-color: #1A1A1A;
    color: #F5F0E8;
    padding: 2rem 2.5rem 1.5rem 2.5rem;
    margin: -1rem -1rem 2rem -1rem;
    border-bottom: 4px solid #C8102E;
}
.masthead-title {
    font-family: 'Oswald', sans-serif;
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: -1px;
    margin: 0;
    line-height: 1;
}
.masthead-flag {
    font-size: 2rem;
    margin-right: 0.5rem;
}
.masthead-sub {
    font-size: 0.9rem;
    color: #AAA;
    margin-top: 0.4rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.masthead-rule {
    border: none;
    border-top: 1px solid #333;
    margin: 1rem 0 0.5rem 0;
}
 
/* Section label */
.section-label {
    font-family: 'Oswald', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #1A1A1A;
    border-bottom: 3px solid #C8102E;
    padding-bottom: 0.3rem;
    margin-bottom: 1.2rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
 
/* Source badge */
.source-badge {
    display: inline-block;
    background-color: #C8102E;
    color: white;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 2px;
    margin-bottom: 0.4rem;
}
 
/* News card */
.news-card {
    background: #FFFFFF;
    border: 1px solid #E0D8CC;
    border-left: 4px solid #C8102E;
    padding: 1rem 1.2rem;
    margin-bottom: 0.85rem;
    border-radius: 2px;
    transition: box-shadow 0.15s ease;
}
.news-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.news-card a {
    font-family: 'Oswald', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #1A1A1A;
    text-decoration: none;
    line-height: 1.35;
}
.news-card a:hover {
    color: #C8102E;
}
.news-meta {
    font-size: 0.75rem;
    color: #888;
    margin-top: 0.35rem;
}
 
/* Source filter pills */
.stMultiSelect span {
    background-color: #C8102E !important;
    color: white !important;
}
 
/* Stats bar */
.stats-bar {
    background: #1A1A1A;
    color: #F5F0E8;
    padding: 0.6rem 1.2rem;
    border-radius: 2px;
    margin-bottom: 1.5rem;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    display: flex;
    gap: 2rem;
}
</style>
""", unsafe_allow_html=True)
 
# ── Masthead ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="masthead">
    <div class="masthead-title"> TT News Hub</div>
    <div class="masthead-sub">Trinidad &amp; Tobago · Local News Aggregator</div>
    <hr class="masthead-rule">
</div>
""", unsafe_allow_html=True)


application_path = os.getcwd()
year_month_day = datetime.today().strftime("%Y-%m-%d")


st.subheader("Your centralized dashboard for local current affairs, sports, opinion and\
             media updates.")


#Look at the folder and find all your archived news files
data_dir = os.path.join(os.getcwd(),"data")

if os.path.exists(data_dir):
    all_files = os.listdir(data_dir)
    csv_archives = [f for f in all_files if f.startswith("trinidad_news_") and f.endswith(".csv")]
    csv_archives.sort(reverse=True)

    # Make a list of the dates from the names of the archived news files, starting with the 
    #latest date
    date_options = [f for f in csv_archives]
    date_options = [f.replace("trinidad_news_","") for f in date_options]
    date_options = [f.replace(".csv","") for f in date_options]
else:
    date_options =[]

# ── Controls (inline, no sidebar) ────────────────────────────────────────────
col_date, col_filter = st.columns([1, 2])
 
with col_date:
    file_selected = st.selectbox(
        "📅 Select date:",
        options=date_options,
    )

if file_selected:
    file_name = f"trinidad_news_{file_selected}.csv"
    final_path_int = os.path.join(application_path, "data")
    final_path = os.path.join(final_path_int, file_name)
    news_df = pd.read_csv(final_path)

    st.subheader(f"📰 Headlines for {file_selected}")

    # Source filter
    sources = sorted(news_df["news_source"].unique().tolist())
    with col_filter:
        selected_sources = st.multiselect(
            "📡 Filter by source:",
            options=sources,
            default=sources,
        )
 
    filtered_df = news_df[news_df["news_source"].isin(selected_sources)]
 
    # Stats bar
    st.markdown(f"""
    <div style="background:#1A1A1A;color:#F5F0E8;padding:0.6rem 1.2rem;
                border-radius:2px;margin-bottom:1.5rem;font-size:0.8rem;
                letter-spacing:0.05em;">
        📰 &nbsp;<strong>{len(filtered_df)}</strong> articles &nbsp;·&nbsp;
        🗓 &nbsp;<strong>{file_selected}</strong> &nbsp;·&nbsp;
        📡 &nbsp;<strong>{len(selected_sources)}</strong> sources
    </div>
    """, unsafe_allow_html=True)

     # Group by source
    for source in selected_sources:
        source_df = filtered_df[filtered_df["news_source"] == source]
        if source_df.empty:
            continue
 
        st.markdown(f'<div class="section-label">{source}</div>', unsafe_allow_html=True)
 
        for _, row in source_df.iterrows():
            title = row.get("news_title", "No title")
            link = row.get("news_link", "#")
            pub_date = row.get("news_publish_date", "")
 
            st.markdown(f"""
            <div class="news-card">
                <div class="source-badge">{source}</div><br>
                <a href="{link}" target="_blank">{title}</a>
                <div class="news-meta">🕐 {pub_date}</div>
            </div>
            """, unsafe_allow_html=True)
 
        st.markdown("<br>", unsafe_allow_html=True)
 
elif not date_options:
    st.info("No news archives found.")

   



