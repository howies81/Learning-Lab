import streamlit as st
import pandas as pd
from datetime import datetime
import os

application_path = os.getcwd()
year_month_day = datetime.today().strftime("%Y-%m-%d")



st.title("Trinidad and Tobago News Hub")
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

#Create a clean dropdown selector in the Streamlit Sidebar
st.sidebar.header("📅 News Archive")
file_selected = st.sidebar.selectbox(
    "Choose the date you want to view:",
    options=date_options,
)

if file_selected:
    file_name = f"trinidad_news_{file_selected}.csv"
    final_path_int = os.path.join(application_path, "data")
    final_path = os.path.join(final_path_int, file_name)
    news_df = pd.read_csv(final_path)

    st.subheader(f"📰 Headlines for {file_selected}")
    st.dataframe(
        news_df,
        column_config={
            "news_link": st.column_config.LinkColumn("Article Link")
        },
        hide_index=True,
        width="stretch"
    ) 



