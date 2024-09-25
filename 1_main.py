# 1_main.py
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from model import MODEL_IDS
from file_processing import process_folder
from json_excel_utils import save_to_json, json_to_excel
from gui import start_gui

# Azure Form Recognizer credentials
endpoint = "https://as-lf-ai-01.cognitiveservices.azure.com/"
api_key = "18ce006f0ac44579a36bfaf01653254c"
json_file_path = "2_results/document_results.json"
excel_file_path = "2_results/document_analysis_results.xlsx"
unsupported_files_log = "2_results/unsupported_files.txt"  # Log for unsupported files

# Initialize client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))


# Function to handle folder selection and processing
def handle_folder_upload(folder_path):
    model_id = MODEL_IDS["Georgetown_law_09242024"]

    # Process the uploaded folder
    all_results, unsupported_files = process_folder(client, model_id, folder_path, json_file_path, excel_file_path,
                                                    unsupported_files_log)

    # Save the results to JSON and Excel
    save_to_json(json_file_path, all_results)
    json_to_excel(json_file_path, excel_file_path)

    return f"Processed folder: {folder_path}\nResults saved to JSON and Excel."


# Start the GUI and pass the folder handler function
start_gui(handle_folder_upload)