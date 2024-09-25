import os
import json
import pandas as pd


# Function to clean text (removes line breaks and replaces them with spaces)
def clean_text(text):
    if isinstance(text, str):
        # Replace \n or \r (line breaks) with a space
        return text.replace("\n", " ").replace("\r", " ")
    return text


# Function to save results to a JSON file (appending to the existing file if it exists)
def save_to_json(json_file_path, all_results):
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
        all_results = existing_data + all_results

    with open(json_file_path, "w") as json_file:
        json.dump(all_results, json_file, indent=4)
    print(f"All results saved to {json_file_path}")


# Function to convert JSON data to Excel, cleaning text and appending new data
def json_to_excel(json_file_path, excel_file_path):
    with open(json_file_path, "r") as f:
        data = json.load(f)

    # Flatten the JSON data into a format suitable for Excel
    excel_data = []
    for doc in data:
        for page in doc["pages"]:
            document_fields = page.get("document_fields", {})

            # Apply clean_text to all fields
            excel_data.append({
                "File Name": clean_text(doc["file_name"]),
                "Page Number": clean_text(str(page["page_number"])),
                "Tables": clean_text(page["tables"]) if isinstance(page["tables"], str) else "Tables found",
                "Title": clean_text(document_fields.get("Title", {}).get("value", "N/A")),
                "Title Confidence": clean_text(str(document_fields.get("Title", {}).get("confidence", "N/A"))),
                "Date": clean_text(document_fields.get("Date", {}).get("value", "N/A")),
                "Date Confidence": clean_text(str(document_fields.get("Date", {}).get("confidence", "N/A"))),
                "Drawing Number": clean_text(document_fields.get("Drawing_Number", {}).get("value", "N/A")),
                "Drawing Number Confidence": clean_text(
                    str(document_fields.get("Drawing_Number", {}).get("confidence", "N/A"))),
                "Originator": clean_text(document_fields.get("Originator", {}).get("value", "N/A")),
                "Originator Confidence": clean_text(
                    str(document_fields.get("Originator", {}).get("confidence", "N/A"))),
                "Discipline": clean_text(document_fields.get("Discipline", {}).get("value", "N/A")),
                "Discipline Confidence": clean_text(
                    str(document_fields.get("Discipline", {}).get("confidence", "N/A"))),
                "Floor Number": clean_text(document_fields.get("Floor_Number", {}).get("value", "N/A")),
                "Floor Number Confidence": clean_text(
                    str(document_fields.get("Floor_Number", {}).get("confidence", "N/A")))
            })

    # Convert to DataFrame
    df_new = pd.DataFrame(excel_data)

    # If the Excel file exists, append the new data and skip duplicates
    if os.path.exists(excel_file_path):
        df_existing = pd.read_excel(excel_file_path)
        existing_file_names = df_existing['File Name'].unique()

        # Remove rows from the new data where 'File Name' already exists in the Excel file
        df_new = df_new[~df_new['File Name'].isin(existing_file_names)]

        # Append the new data to the existing data
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        # If no Excel file exists, simply write the new data
        df_combined = df_new

    # Write the combined data to the Excel file
    df_combined.to_excel(excel_file_path, index=False)
    print(f"Data written to {excel_file_path}")
