import os
import json
import pandas as pd
import re
import threading
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


# Function to read Azure credentials from a text file
def read_credentials(file_path):
    ai_credentials = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(' = ')
            ai_credentials[key] = value.strip('"')
    return ai_credentials


# Read credentials from the azure_credentials.txt file
credentials_file_path = "C:/Users/liams/ArchScan_Capture_Project/archscan_ai/archscan_final/text_files/credentials.txt"  # Ensure this is correct
credentials = read_credentials(credentials_file_path)
endpoint = credentials["endpoint"]
key = credentials["key"]

# Initialize the Azure Form Recognizer client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))


# Function to read model IDs from a text file
def get_model_ids_from_file(file_path="C:/Users/liams/ArchScan_Capture_Project/archscan_ai/test/model_ids.txt"):
    model_ids = []
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return model_ids

    with open(file_path, 'r') as file:
        for line in file:
            model_id = line.strip()
            if model_id:  # Avoid empty lines
                model_ids.append(model_id)

    print(f"Retrieved model IDs from file: {model_ids}")  # Debugging statement
    return model_ids


# Function to clean text values and replace pilcrow-like symbols
def clean_text(value):
    if isinstance(value, str):
        value = re.sub(r'[\u00b6\u2029\r\n]+', ' ', value)  # Handles ¶, paragraph separators, and newlines
        return value.strip()
    return value


# Function to analyze a document
def analyze_document(client, model_id, document_path):
    try:
        with open(document_path, "rb") as f:
            poller = client.begin_analyze_document(model_id=model_id, document=f)
        result = poller.result()

        document_result = {
            "file_name": os.path.basename(document_path),
            "pages": []
        }

        for page in result.pages:
            page_info = {"page_number": page.page_number, "tables": "No tables found on this page."}
            if hasattr(page, "tables"):
                page_info["tables"] = [{"table_data": table.cells} for table in page.tables]

            document_fields = {
                name: {"value": field.value, "confidence": field.confidence}
                for document in result.documents
                for name, field in document.fields.items()
            }

            page_info["document_fields"] = document_fields
            document_result["pages"].append(page_info)

        return document_result
    except Exception as e:
        raise Exception(f"Error processing {document_path}: {str(e)}")


# Function to filter new files for processing
def filter_new_files(folder_path, json_file_path, excel_file_path):
    existing_file_names = set()

    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
        existing_file_names.update(doc["file_name"] for doc in existing_data)

    if os.path.exists(excel_file_path):
        df_existing = pd.read_excel(excel_file_path)
        existing_file_names.update(df_existing['File Name'].unique())

    pdf_files = [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(folder_path)
        for filename in filenames
        if filename.endswith(".pdf") and filename not in existing_file_names
    ]

    return pdf_files


# Function to ensure log file existence
def ensure_log_file_exists(log_file_path):
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            log_file.write("Unsupported or Corrupted Files:\n")


# Function to process a folder of documents
def process_folder(client, model_id, folder_path, json_file_path, excel_file_path, unsupported_files_log):
    pdf_files = filter_new_files(folder_path, json_file_path, excel_file_path)
    if not pdf_files:
        print("No new files to process.")
        return [], []

    all_results = []
    unsupported_files = []

    ensure_log_file_exists(unsupported_files_log)

    with open(unsupported_files_log, "a") as log_file:
        log_file.write("\nProcessing new batch:\n")

    with ThreadPoolExecutor() as executor:
        future_to_file = {
            executor.submit(analyze_document, client, model_id, file): file for file in pdf_files
        }

        with tqdm(total=len(pdf_files), desc="Processing Documents", unit="file") as progress_bar:
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    all_results.append(result)
                except Exception as e:
                    unsupported_files.append(file)
                    with open(unsupported_files_log, "a") as log_file:
                        log_file.write(f"{file}\n")
                progress_bar.update(1)

    return all_results, unsupported_files


# New JSON to Excel function
def json_to_excel(json_file_path, excel_file_path):
    with open(json_file_path, "r") as f:
        data = json.load(f)

    excel_data = []
    for doc in data:
        for page in doc["pages"]:
            document_fields = page.get("document_fields", {})
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
                "Floor Number": clean_text(document_fields.get("Floor Number", {}).get("value", "N/A")),
                "Floor Number Confidence": clean_text(
                    str(document_fields.get("Floor Number", {}).get("confidence", "N/A")))
            })

    df_new = pd.DataFrame(excel_data)
    if os.path.exists(excel_file_path):
        df_existing = pd.read_excel(excel_file_path)
        existing_file_names = df_existing['File Name'].unique()
        df_new = df_new[~df_new['File Name'].isin(existing_file_names)]
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_excel(excel_file_path, index=False)
    print(f"Data written to {excel_file_path}")


# Function to handle folder selection and processing in a separate thread
def handle_folder_upload(input_folder_path, output_folder_path, model_id):
    json_file_path = os.path.join(output_folder_path, "document_results.json")
    excel_file_path = os.path.join(output_folder_path, "document_analysis_results.xlsx")
    unsupported_files_log = os.path.join(output_folder_path, "unsupported_files.txt")

    all_results, unsupported_files = process_folder(
        client, model_id, input_folder_path, json_file_path, excel_file_path, unsupported_files_log
    )
    save_to_json(json_file_path, all_results)
    json_to_excel(json_file_path, excel_file_path)

    return f"Processed folder: {input_folder_path}\nResults saved to {output_folder_path}"


# Function to save results to a JSON file
def save_to_json(json_file_path, all_results):
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
        all_results = existing_data + all_results

    with open(json_file_path, "w") as json_file:
        json.dump(all_results, json_file, indent=4)
    print(f"All results saved to {json_file_path}")


# Function to start the Tkinter GUI
def start_gui(handle_folder_upload):
    selected_input_folder = None
    selected_output_folder = None
    selected_model_id = None

    # Populate model dropdown on GUI initialization
    model_ids = get_model_ids_from_file("C:/Users/liams/ArchScan_Capture_Project/archscan_ai/test/model_ids.txt")

    # Show an alert if no models are retrieved
    if not model_ids:
        messagebox.showerror("No Models Found", "No models found in model_ids.txt. Please add model IDs to continue.")

    def upload_folder():
        nonlocal selected_input_folder
        selected_input_folder = filedialog.askdirectory(
            title="Choose a folder containing files to process"
        )
        folder_label.config(
            text=f"Input folder: {os.path.basename(selected_input_folder)}" if selected_input_folder else "No input folder selected."
        )

    def choose_output_folder():
        nonlocal selected_output_folder
        selected_output_folder = filedialog.askdirectory(
            title="Choose a folder to save the output files"
        )
        destination_label.config(
            text=f"Output folder: {os.path.basename(selected_output_folder)}" if selected_output_folder else "No output folder selected."
        )

    def run_process():
        if not selected_input_folder or not selected_output_folder or not selected_model_id:
            messagebox.showwarning("Selections missing",
                                   "Please select an input folder, output folder, and model before running.")
            return
        status_label.config(text="Processing...")

        def background_task():
            result = handle_folder_upload(selected_input_folder, selected_output_folder, selected_model_id)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, result)
            status_label.config(text="Processing complete.")
            root.after(0, lambda: messagebox.showinfo("Success", f"Files saved to {selected_output_folder}"))

        threading.Thread(target=background_task).start()

    root = tk.Tk()
    root.title("File Processor")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')

    header_frame = tk.Frame(root, bg='#4a90e2', height=60)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    title_label = tk.Label(header_frame, text="File Processor", font=("Helvetica", 24, "bold"), fg='white',
                           bg='#4a90e2')
    title_label.grid(row=0, column=0, padx=10, pady=20)

    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    button_frame = tk.Frame(main_frame, bg='#f0f0f0')
    button_frame.grid(row=0, column=0, pady=10)

    # Model selection dropdown
    model_label = tk.Label(button_frame, text="Select Model:", font=("Helvetica", 12), bg="#f0f0f0")
    model_label.grid(row=0, column=0, padx=10)

    model_combo = ttk.Combobox(button_frame, values=model_ids, font=("Helvetica", 12))
    model_combo.grid(row=0, column=1, padx=10)
    model_combo.bind("<<ComboboxSelected>>", lambda e: select_model())

    def select_model():
        nonlocal selected_model_id
        selected_model_id = model_combo.get()

    upload_button = tk.Button(button_frame, text="Select Input Folder", command=upload_folder, font=("Helvetica", 12),
                              bg="#4a90e2", fg="white", padx=10, pady=5)
    upload_button.grid(row=1, column=0, padx=10)

    output_button = tk.Button(button_frame, text="Select Output Folder", command=choose_output_folder,
                              font=("Helvetica", 12), bg="#4a90e2", fg="white", padx=10, pady=5)
    output_button.grid(row=1, column=1, padx=10)

    folder_label = tk.Label(button_frame, text="No input folder selected", font=("Helvetica", 12), bg="#f0f0f0")
    folder_label.grid(row=2, column=0, pady=5)

    destination_label = tk.Label(button_frame, text="No output folder selected", font=("Helvetica", 12), bg="#f0f0f0")
    destination_label.grid(row=2, column=1, pady=5)

    run_button = tk.Button(button_frame, text="Run", command=run_process, font=("Helvetica", 12), bg="#4a90e2",
                           fg="white", padx=10, pady=5)
    run_button.grid(row=0, column=2, pady=10)

    output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=100, height=25, font=("Courier", 10))
    output_text.grid(row=4, column=0, pady=10)

    status_label = tk.Label(main_frame, text="", font=("Helvetica", 10), bg="#f0f0f0", fg="#4a90e2")
    status_label.grid(row=5, column=0, pady=5)

    root.mainloop()


# Entry point
if __name__ == "__main__":
    start_gui(handle_folder_upload)