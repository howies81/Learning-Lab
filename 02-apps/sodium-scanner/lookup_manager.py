import streamlit as st
from local_food_database import check_local_database

def fetch_product_data(barcode):
    # 1. Check the Local CSV first (Priority)
    #st.info(f"Searching local records for {barcode}...")
    
    local_result = check_local_database(barcode)
    if local_result["status"] == "success":
        return local_result
    
    if local_result["status"] == "not_found":
         # Simulated global lookup
         #Fetch Result from OpenFoodFacts database
         #global_result = check_global_database(barcode)
         #if global_result["status"] == "success":
            #return global_result
         global_result = {"status": "not_found"}
    
    return global_result