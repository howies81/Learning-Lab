import pandas as pd
import streamlit as st

def check_local_database(barcode):
    try:
        food_df = pd.read_csv("food_item_nutrition_facts.csv", dtype={"barcode": str}) # Force barcodes to stay as Text
        food_item = food_df[food_df['barcode'] == str(barcode)]
        
        if not food_item.empty:
            return food_item.iloc[0].to_dict()
        else:
            return "ITEM NOT FOUND IN DATABASE!"
    except FileNotFoundError:
        #st.warning("Food Item database cannot be found!")
        return "FILE CANNOT BE FOUND!"