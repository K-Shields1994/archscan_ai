import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from archscan_ai.test.model import MODEL_IDS
from archscan_ai.test.file_processing import process_folder
from archscan_ai.test.json_excel_utils import save_to_json
from archscan_ai.test.gui import run_gui


# Function to read Azure credentials from a text file
def read_credentials(file_path):
    ai_credentials = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(' = ')
            ai_credentials[key] = value.strip('"')
    return ai_credentials


# Read credentials from the azure_credentials.txt file
credentials_file_path = "azure_credentials.txt"
credentials = read_credentials(credentials_file_path)

# Azure Form Recognizer credentials
endpoint = credentials["endpoint"]
api_key = credentials["api_key"]

# Initialize client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))


# Function to handle folder selection and processing
def handle_folder_upload(input_folder_path, output_folder_path):
    model_id = MODEL_IDS["San Jose"]

    # Generate file paths dynamically based on the output folder
    json_file_path = os.path.join(output_folder_path, "document_results.json")
    unsupported_files_log = os.path.join(output_folder_path, "unsupported_files.txt")

    # Process the uploaded folder (input folder)
    all_results, unsupported_files = process_folder(client, model_id, input_folder_path, json_file_path,
                                                    unsupported_files_log)

    # Save the results to JSON
    save_to_json(json_file_path, all_results)

    # Save unsupported file details
    if unsupported_files:
        with open(unsupported_files_log, 'w') as log_file:
            log_file.write("\n".join(unsupported_files))


if __name__ == "__main__":
    run_gui(handle_folder_upload)  # Call the GUI and pass the processing function to it
