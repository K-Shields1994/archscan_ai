#Function to parse through title, if floor value is found in title, assign it to floor field 
#TODO Implement this function with existing code

import re

def extract_floor_number(title, multiple_floors_detected=False):
    # Mapping from floor names and keywords to numerical values or identifiers
    floor_mapping = {
        "Ground": "0",
        "First": "1",
        "1st": "1",
        "Second": "2",
        "2nd": "2",
        "Third": "3",
        "3rd": "3",
        "Fourth": "4",
        "4th": "4",
        "Basement": "-1",
        "Roof": "Roof",  
        # Add more mappings as necessary
    }
    
    # Regular expression to find floor names or keywords like "Roof"
    pattern = r"\b(?:Ground|First|1st|Second|2nd|Third|3rd|Fourth|4th|Basement|Basement \d+|Roof)\b"
    
    # Check if the title contains "Riser"
    if "Riser" in title:
        return "Riser"
    
    # Check if multiple floors are detected
    if multiple_floors_detected:
        return "Riser"
    
    # Otherwise, search for standard floor keywords
    match = re.search(pattern, title, re.IGNORECASE)
    if match:
        floor_name = match.group(0)
        return floor_mapping.get(floor_name, None)
    
    return None  # If no floor number is found

# Example usage
title1 = "Riser Plan for Building"
title2 = "Third Floor Plan"
title3 = "Building Riser Document"

floor_value1 = extract_floor_number(title1)
floor_value2 = extract_floor_number(title2, multiple_floors_detected=True)  # Assume multiple floors were detected
floor_value3 = extract_floor_number(title3)

print(f"Extracted floor value from title1: {floor_value1}")  # Output: Riser
print(f"Extracted floor value from title2: {floor_value2}")  # Output: Riser
print(f"Extracted floor value from title3: {floor_value3}")  # Output: Riser
