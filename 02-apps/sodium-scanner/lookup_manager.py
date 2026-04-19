import streamlit as st
from local_food_database import check_local_database

def fetch_product_data(barcode):
    # 1. Check the Local CSV first (Priority)
    #st.info(f"Searching local records for {barcode}...")
    
    local_result = check_local_database(barcode)
    return local_result