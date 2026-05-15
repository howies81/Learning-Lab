""" def PAHO_model_check(sodium_mg, calories):
    
    Returns True if the product exceeds PAHO sodium limits.
    Logic: 1mg sodium per 1 kcal.
    
    if sodium_mg is None or calories is None:
        return False
    return sodium_mg >= calories """

def calculate_paho_warnings(item):
    """
    Calculates warnings with edge-case handling for missing data.
    """
    warnings = []
    
    # Extract values and convert to float, defaulting to None if missing/invalid
    try:
        sodium = float(item.get('sodium_mg')) if item.get('sodium_mg') not in [None, ''] else None
        calories = float(item.get('calories')) if item.get('calories') not in [None, '', 0] else None
    except (ValueError, TypeError):
        sodium = calories = None

    # EDGE CASE: Missing Core Data
    if sodium is None or calories is None:
        return ["INSUFFICIENT DATA"]

    # 1. SODIUM (The 1:1 Rule)
    if sodium >= calories:
        warnings.append("HIGH IN SODIUM")

    # 2. SUGARS (Handle missing sugar data gracefully)
    """ try:
        sugars = float(item.get('sugars_g', 0))
        if (sugars * 4 / calories) >= 0.10:
            warnings.append("EXCESSIVE SUGAR")
    except:
        pass """ # If sugar data is missing, we simply don't add the warning

    # ... Repeat for Fat, Sat Fat, etc. using same try/except block ...

    return warnings

    #FOR FUTURE USE ----------------------------------------------

    # 2. FREE SUGARS: >= 10% of total energy
    # (Total Sugars (g) * 4 kcal/g) / Total Calories
    """ sugar_calories = item.get('sugars_g', 0) * 4
    if item['calories'] > 0 and (sugar_calories / item['calories']) >= 0.10:
        warnings.append("EXCESSIVE SUGAR") """

    # 3. TOTAL FAT: >= 30% of total energy
    # (Total Fat (g) * 9 kcal/g) / Total Calories
    """ fat_calories = item.get('fat_g', 0) * 9
    if item['calories'] > 0 and (fat_calories / item['calories']) >= 0.30:
        warnings.append("EXCESSIVE FAT") """

    # 4. SATURATED FAT: >= 10% of total energy
    """ sat_fat_calories = item.get('sat_fat_g', 0) * 9
    if item['calories'] > 0 and (sat_fat_calories / item['calories']) >= 0.10:
        warnings.append("EXCESSIVE SATURATED FAT") """

    # 5. TRANS FAT: >= 1% of total energy
    """ trans_fat_calories = item.get('trans_fat_g', 0) * 9
    if item['calories'] > 0 and (trans_fat_calories / item['calories']) >= 0.01:
        warnings.append("EXCESSIVE TRANS FAT") """

    #return warnings

