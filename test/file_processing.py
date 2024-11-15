import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import AnalyzeDocumentLROPoller


def process_folder(client, model_id, input_folder, json_output_path, unsupported_log_path):
    results = []
    unsupported_files = []

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        if file_name.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            with open(file_path, "rb") as f:
                poller = client.begin_analyze_document(model_id, document=f)
                result = poller.result()

                # Append result data to list
                results.append(result.to_dict())

                # Save the OCR-ed PDF if applicable
                if file_name.endswith('.pdf'):
                    ocr_pdf_path = os.path.join(json_output_path.replace(".json", ""), file_name)
                    with open(ocr_pdf_path, 'wb') as pdf_file:
                        pdf_file.write(f.read())  # Saving the processed PDF

        else:
            unsupported_files.append(file_name)

    return results, unsupported_files
