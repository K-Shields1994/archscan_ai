import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import json


def analyze_document(client, model_id, document_path):
    try:
        with open(document_path, "rb") as f:
            poller = client.begin_analyze_document(model_id=model_id, document=f)

        # Wait for the result
        result = poller.result()

        # Initialize results dictionary
        document_result = {
            "file_name": os.path.basename(document_path),
            "pages": []
        }

        # Iterate through pages and gather the results
        for page in result.pages:
            page_info = {"page_number": page.page_number, "tables": "No tables found on this page."}

            # Check if tables exist
            if hasattr(page, "tables"):
                page_info["tables"] = [{"table_data": table.cells} for table in page.tables]

            # Add document fields (like Title, Date, etc.) if available
            document_fields = {}
            for document in result.documents:
                for name, field in document.fields.items():
                    document_fields[name] = {
                        "value": field.value,
                        "confidence": field.confidence
                    }

            # Append document fields to page_info
            page_info["document_fields"] = document_fields

            # Add page info to result
            document_result["pages"].append(page_info)

        return document_result
    except Exception as e:
        raise Exception(f"Error processing {document_path}: {str(e)}")


def filter_new_files(folder_path, json_file_path, excel_file_path):
    existing_file_names = set()

    # Check if JSON file exists and load file names
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
        existing_file_names.update(doc["file_name"] for doc in existing_data)

    # Check if Excel file exists and load file names
    if os.path.exists(excel_file_path):
        import pandas as pd
        df_existing = pd.read_excel(excel_file_path)
        existing_file_names.update(df_existing['File Name'].unique())

    # Step 2: Gather all PDF file paths and filter out those already processed
    pdf_files = []
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(".pdf"):
                file_path = os.path.join(dirpath, filename)
                if filename not in existing_file_names:  # Filter out already processed files
                    pdf_files.append(file_path)

    return pdf_files


def ensure_log_file_exists(log_file_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # Create the log file if it doesn't exist
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            log_file.write("Unsupported or Corrupted Files:\n")


def process_folder(client, model_id, folder_path, json_file_path, excel_file_path, unsupported_files_log):
    pdf_files = filter_new_files(folder_path, json_file_path, excel_file_path)

    if not pdf_files:
        print("No new files to process.")
        return [], []

    all_results = []
    unsupported_files = []

    # Ensure log file exists before proceeding
    ensure_log_file_exists(unsupported_files_log)

    # Append mode for unsupported files log
    with open(unsupported_files_log, "a") as log_file:
        log_file.write("\nProcessing new batch:\n")

    # Use ThreadPoolExecutor to process files in parallel
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(analyze_document, client, model_id, file): file for file in pdf_files}

        # Create tqdm progress bar
        with tqdm(total=len(pdf_files), desc="Processing Documents", unit="file") as progress_bar:
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    all_results.append(result)
                except Exception as e:
                    print(f"Error: {e}")
                    unsupported_files.append(file)
                    # Log unsupported files
                    with open(unsupported_files_log, "a") as log_file:
                        log_file.write(f"{file}\n")
                # Update progress bar after each file is processed
                progress_bar.update(1)

    return all_results, unsupported_files
