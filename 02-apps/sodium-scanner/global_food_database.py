import requests
import streamlit as st

@st.cache_data(ttl=300)
def check_global_database(barcode):
    # The full, correct path to the JSON data
    url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}.json"

    try:
        response = requests.get(url, timeout= 5) # check connection status. 200 is good, 404 is bad
    except requests.exceptions.RequestException: #If error occurs, return API error dictionary
        return {"status": "api_error", "data": None} 

    # API responded, but not OK
    if response.status_code != 200:
        return {"status": "api_error", "data": None}

      
    
    try:
        data = response.json()
    except ValueError:
        return {"status": "parse_error", "data": None}
    
    if data.get('status') == 0:
        return {"status": "not_found", "data": None}
    

    if data.get('status') == 1:
        #Get product name and quantity
        product = data['product']
        product_name = product.get('product_name', 'Unknown Item')
        product_quantity = product.get('product_quantity')  # total container size
        #product_quantity_unit = product.get('product_quantity_unit', '').lower()

        # Get sodium (stored in grams per serving)
        nutriments = product.get('nutriments', {})
        sodium_g = nutriments.get('sodium_100g')
        if sodium_g is not None:
            sodium_mg = sodium_g * 1000
        else:
            sodium_mg = None
        
        #Get calories, added sugars, fat, saturated fat per serving
        calories = nutriments.get('energy-kcal_100g')
        fat_g = nutriments.get('fat_100g')
        sat_fat_g = nutriments.get('saturated-fat_100g')
        sugars_g = nutriments.get('sugars_100g')

        #Get product name, product type and determine if the product is a solid or liquid
        brands_raw = product.get('brands', 'Unknown Brand')
        brand = brands_raw.split(',')[0].strip()

        
        #Get Product Type (Categories)
        categories = product.get('categories', '')
        # We'll take the first major category listed
        if categories:
            product_type = categories.split(',')[0]
        else:
            product_type = "General Food"
        
        #Determine of product is solid or liquid
        # Check if 'Beverages' is in categories OR if serving size uses 'ml'
        serving_quantity = float(product.get('serving_quantity', 0.0))
        serving_quantity_unit = product.get('serving_quantity_unit', '').lower()
        if serving_quantity_unit == 'ml' or 'beverage' in categories.lower():
            is_liquid = 1
        else:
            is_liquid = 0

        return {
            "status": "success",
            "data": {
                "barcode": barcode,
                "product_type": product_type,
                "is_liquid": is_liquid,
                "brand": brand,
                #"product_name": product_name,
                "weight_g": product_quantity if not is_liquid else 0,
                "amount_mL": product_quantity if is_liquid else 0,
                "serving_weight_g": serving_quantity if not is_liquid else 0,
                "serving_amt_mL": serving_quantity if is_liquid else 0,
                "sodium_mg": sodium_mg,
                "sugars_g": sugars_g,
                "added_sugars_g": 0,
                "fat_g": fat_g,
                "sat_fat_g": sat_fat_g,
                "trans_fat_g": 0,
                "calories": calories                
                
            }
        }
            
    return {"status": "parse_error", "data": None}