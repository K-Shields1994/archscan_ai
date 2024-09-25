import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from model import MODEL_IDS
from file_processing import process_folder
from json_excel_utils import save_to_json, json_to_excel

# Azure Form Recognizer credentials
endpoint = "https://as-lf-ai-01.cognitiveservices.azure.com/"
api_key = "18ce006f0ac44579a36bfaf01653254c"

# Initialize client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))


# Function to handle folder selection and processing
def handle_folder_upload(input_folder_path, output_folder_path):
    model_id = MODEL_IDS["Georgetown_law_09242024"]

    # Generate file paths dynamically based on the output folder
    json_file_path = os.path.join(output_folder_path, "document_results.json")
    excel_file_path = os.path.join(output_folder_path, "document_analysis_results.xlsx")
    unsupported_files_log = os.path.join(output_folder_path, "unsupported_files.txt")

    # Process the uploaded folder (input folder)
    all_results, unsupported_files = process_folder(client, model_id, input_folder_path, json_file_path,
                                                    excel_file_path, unsupported_files_log)

    # Save the results to JSON and Excel
    save_to_json(json_file_path, all_results)
    json_to_excel(json_file_path, excel_file_path)

    return f"Processed folder: {input_folder_path}\nResults saved to {output_folder_path}"


# Function to handle saving the output in the selected folder
def handle_save_output(output_folder_path):
    # This function is no longer needed since the output folder is passed directly during processing
    pass


if __name__ == "__main__":
    from gui import start_gui

    start_gui(handle_folder_upload, handle_save_output)
