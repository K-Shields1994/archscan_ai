import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeOutputOption, AnalyzeResult

# Load stop words from file
STOP_WORDS_FILE_PATH = 'C:/Users/liams/ArchScan_Capture_Project/archscan_ai/archscan_final/text_files/stop_words.txt'


def load_stop_words(file_path):
    with open(file_path, 'r') as f:
        return set(line.strip().lower() for line in f)


STOP_WORDS = load_stop_words(STOP_WORDS_FILE_PATH)


def process_pdf(file_path, output_folder_path, client):
    """
    Processes a single PDF file and saves the results to the output folder.
    """
    input_file_name = os.path.splitext(os.path.basename(file_path))[0]

    try:
        # Analyze the PDF
        with open(file_path, "rb") as f:
            poller = client.begin_analyze_document(
                "prebuilt-read",
                analyze_request=f,
                output=[AnalyzeOutputOption.PDF],
                content_type="application/octet-stream",
            )
            result: AnalyzeResult = poller.result()

        # Output file paths
        pdf_output_file = os.path.join(output_folder_path, f"{input_file_name}.pdf")
        json_output_file = os.path.join(output_folder_path, f"{input_file_name}.json")
        txt_output_file = os.path.join(output_folder_path, f"{input_file_name}_filtered.txt")

        # Save the analyzed PDF
        response = client.get_analyze_result_pdf(
            model_id=result.model_id, result_id=poller.details["operation_id"]
        )
        with open(pdf_output_file, "wb") as writer:
            writer.writelines(response)

        # Save the JSON output
        result_json = result.as_dict()
        with open(json_output_file, "w") as json_file:
            json.dump(result_json, json_file, indent=4)

        # Extract and filter words, then save to a text file
        with open(txt_output_file, "w") as text_file:
            for page in result_json.get("pages", []):
                for line in page.get("lines", []):
                    content = line.get("content", "")
                    words = content.split()
                    filtered_words = [word for word in words if word.lower() not in STOP_WORDS]
                    text_file.write(" ".join(filtered_words) + "\n")

        return f"Processed: {file_path}\n"
    except Exception as e:
        return f"Failed to process {file_path}: {str(e)}\n"


def handle_folder_upload(input_folder_path, output_folder_path):
    """
    Processes all PDF files in the selected input folder and saves the results to the output folder.
    """
    endpoint = "https://as-lf-ai-01.cognitiveservices.azure.com/"
    key = "18ce006f0ac44579a36bfaf01653254c"
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    result_summary = ""

    # Gather all PDF files from the input folder
    pdf_files = []
    for root, _, files in os.walk(input_folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))

    for file_path in pdf_files:
        result_summary += process_pdf(file_path, output_folder_path, document_intelligence_client)

    return result_summary


def start_gui(handle_folder_upload):
    selected_input_folder = None
    selected_output_folder = None

    def upload_folder():
        nonlocal selected_input_folder
        selected_input_folder = filedialog.askdirectory(
            title="Choose a folder containing files to process"
        )
        input_folder_label.config(
            text=f"Input folder: {os.path.basename(selected_input_folder)}" if selected_input_folder else "No input folder selected."
        )

    def choose_output_folder():
        nonlocal selected_output_folder
        selected_output_folder = filedialog.askdirectory(
            title="Choose a folder to save the output files"
        )
        output_folder_label.config(
            text=f"Output folder: {os.path.basename(selected_output_folder)}" if selected_output_folder else "No output folder selected."
        )

    def run_process():
        if not selected_input_folder or not selected_output_folder:
            messagebox.showwarning("Folders missing", "Please select both input and output folders before running.")
            return
        status_label.config(text="Processing...")
        progress_bar.start()
        root.update_idletasks()

        result = handle_folder_upload(selected_input_folder, selected_output_folder)
        progress_bar.stop()
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, result)
        status_label.config(text="Processing complete.")
        messagebox.showinfo("Success", f"Files saved to {selected_output_folder}")

    root = tk.Tk()
    root.title("OCR File Processor")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')

    # Header Frame
    header_frame = tk.Frame(root, bg='#4a90e2', height=60)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    title_label = tk.Label(header_frame, text="OCR File Processor", font=("Helvetica", 24, "bold"), fg='white',
                           bg='#4a90e2')
    title_label.grid(row=0, column=0, padx=10, pady=20)

    # Main Frame
    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    main_frame.grid_columnconfigure(0, weight=1)

    # Button Frame
    button_frame = tk.Frame(main_frame, bg='#f0f0f0')
    button_frame.grid(row=0, column=0, pady=10)

    # Folder Selection Buttons
    upload_button = tk.Button(button_frame, text="Select Input Folder", command=upload_folder, font=("Helvetica", 12),
                              bg="#4a90e2", fg="white", padx=10, pady=5)
    upload_button.grid(row=0, column=0, padx=10)

    output_button = tk.Button(button_frame, text="Select Output Folder", command=choose_output_folder,
                              font=("Helvetica", 12), bg="#4a90e2", fg="white", padx=10, pady=5)
    output_button.grid(row=0, column=1, padx=10)

    # Labels for Folder Paths
    input_folder_label = tk.Label(button_frame, text="No input folder selected", font=("Helvetica", 12), bg="#f0f0f0")
    input_folder_label.grid(row=1, column=0, pady=5)

    output_folder_label = tk.Label(button_frame, text="No output folder selected", font=("Helvetica", 12), bg="#f0f0f0")
    output_folder_label.grid(row=1, column=1, pady=5)

    # Run Button
    run_button = tk.Button(button_frame, text="Run", command=run_process, font=("Helvetica", 12), bg="#4a90e2",
                           fg="white", padx=10, pady=5)
    run_button.grid(row=0, column=2, pady=10)

    # Output Text Area
    output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=100, height=25, font=("Courier", 10))
    output_text.grid(row=4, column=0, pady=10)

    # Status Label
    status_label = tk.Label(main_frame, text="", font=("Helvetica", 10), bg="#f0f0f0", fg="#4a90e2")
    status_label.grid(row=5, column=0, pady=5)

    # Footer with Progress Bar
    footer_frame = tk.Frame(main_frame, bg='#f0f0f0', height=40)
    footer_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
    footer_frame.grid_columnconfigure(0, weight=1)

    progress_bar = ttk.Progressbar(footer_frame, orient="horizontal", mode="indeterminate", length=400)
    progress_bar.grid(row=0, column=0, pady=10)

    root.mainloop()


# Start the GUI
start_gui(handle_folder_upload)
