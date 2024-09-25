# 1_main.py
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from model import MODEL_IDS
from file_processing import process_folder
from json_excel_utils import save_to_json, json_to_excel
from gui import start_gui
import os

# Azure Form Recognizer credentials
endpoint = "https://as-lf-ai-01.cognitiveservices.azure.com/"
api_key = "18ce006f0ac44579a36bfaf01653254c"

# Initialize client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))


# Function to handle folder selection and processing
def handle_folder_upload(folder_path):
    model_id = MODEL_IDS["Georgetown_law_09242024"]

    # Process the uploaded folder
    all_results, unsupported_files = process_folder(client, model_id, folder_path)

    return all_results


# Function to handle saving the output in selected format and location
def handle_save_output(save_folder_path, file_type):
    # Path for saving
    json_file_path = os.path.join(save_folder_path, "document_results.json")
    excel_file_path = os.path.join(save_folder_path, "document_analysis_results.xlsx")
    unsupported_files_log = os.path.join(save_folder_path, "unsupported_files.txt")

    # Mock results (replace with actual results from your process)
    all_results = {"key": "value"}  # This should come from `handle_folder_upload` function

    # Save the results in selected format
    if file_type == "Excel":
        json_to_excel(json_file_path, excel_file_path)
    elif file_type == "JSON":
        save_to_json(json_file_path, all_results)
    elif file_type == "Text":
        with open(unsupported_files_log, 'w') as text_file:
            text_file.write("Unsupported files log")

    print(f"Files saved in {file_type} format at {save_folder_path}")


# Start the GUI and pass the folder handler function
start_gui(handle_folder_upload, handle_save_output)