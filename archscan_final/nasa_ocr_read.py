#!/usr/bin/env python3
"""
NASA-Style Python Script for OCR and Text Filtering Using Azure Document Intelligence
"""

import os
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk
from typing import Set
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeOutputOption, AnalyzeResult

# -----------------------------------------------------------------------------
# Global Constants
# -----------------------------------------------------------------------------
STOP_WORDS_FILE_PATH = "text_files/stop_words.txt"
AZURE_ENDPOINT = "https://as-lf-ai-01.cognitiveservices.azure.com/"
AZURE_KEY = "18ce006f0ac44579a36bfaf01653254c"


# -----------------------------------------------------------------------------
# Load Stop Words
# -----------------------------------------------------------------------------
def load_stop_words_from_file(file_path: str) -> Set[str]:
    """
    Load stop words from a text file. If the file is not found,
    display an error and return an empty set.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file_handle:
            return {line.strip().lower() for line in file_handle}
    except FileNotFoundError:
        messagebox.showerror("Error", f"Stop words file not found: {file_path}")
        return set()


STOP_WORDS = load_stop_words_from_file(STOP_WORDS_FILE_PATH)


# -----------------------------------------------------------------------------
# Process Single PDF
# -----------------------------------------------------------------------------
def process_single_pdf(
        file_path: str,
        output_folder: str,
        client: DocumentIntelligenceClient
) -> str:
    """
    Process a single PDF file for OCR using Azure Document Intelligence,
    save output as PDF, JSON, and filtered text.

    :param file_path: Full path to the input PDF file
    :param output_folder: Output directory to save results
    :param client: DocumentIntelligenceClient instance
    :return: A status message indicating success or failure
    """
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    pdf_path_out = os.path.join(output_folder, f"{base_name}.pdf")
    json_path_out = os.path.join(output_folder, f"{base_name}.json")
    text_path_out = os.path.join(output_folder, f"{base_name}_filtered.txt")

    try:
        with open(file_path, "rb") as handle_in:
            poller = client.begin_analyze_document(
                model_id="prebuilt-read",
                analyze_request=handle_in,
                output=[AnalyzeOutputOption.PDF],
                content_type="application/octet-stream",
            )
            analyze_result: AnalyzeResult = poller.result()

        response = client.get_analyze_result_pdf(
            model_id=analyze_result.model_id,
            result_id=poller.details["operation_id"],
        )
        with open(pdf_path_out, "wb") as handle_out_pdf:
            handle_out_pdf.writelines(response)

        as_dict_result = analyze_result.as_dict()
        with open(json_path_out, "w", encoding="utf-8") as handle_out_json:
            json.dump(as_dict_result, handle_out_json, indent=4, ensure_ascii=False)

        with open(text_path_out, "w", encoding="utf-8") as handle_out_text:
            for page in as_dict_result.get("pages", []):
                for line in page.get("lines", []):
                    content = line.get("content", "")
                    tokens = content.split()
                    filtered_tokens = [
                        token
                        for token in tokens
                        if token.lower() not in STOP_WORDS
                    ]
                    handle_out_text.write(" ".join(filtered_tokens) + "\n")

        return f"Processed: {file_path}\n"

    except Exception as exc:
        error_message = f"Failed to process {file_path}: {str(exc)}"
        print(error_message)
        return error_message + "\n"


# -----------------------------------------------------------------------------
# Filter Text from JSON
# -----------------------------------------------------------------------------
def filter_text_from_json(
        json_path: str,
        stop_words: Set[str],
        output_txt_path: str
) -> None:
    """
    Load OCR JSON data, filter out stop words, and write the cleaned
    text to a .txt file.

    :param json_path: Path to the JSON file
    :param stop_words: Set of stop words to filter out
    :param output_txt_path: the Path where the filtered text will be written
    """
    try:
        with open(json_path, "r", encoding="utf-8") as handle_in:
            data = json.load(handle_in)

        filtered_lines = []
        for page in data.get("pages", []):
            for line in page.get("lines", []):
                content = line.get("content", "")
                tokens = content.split()
                filtered_tokens = [
                    token
                    for token in tokens
                    if token.lower() not in stop_words
                ]
                filtered_lines.append(" ".join(filtered_tokens))

        with open(output_txt_path, "w", encoding="utf-8") as handle_out:
            handle_out.write("\n".join(filtered_lines))

    except Exception as exc:
        print(f"Error processing JSON file {json_path}: {exc}")


# -----------------------------------------------------------------------------
# Handle Folder Upload
# -----------------------------------------------------------------------------
def handle_folder_upload(
        input_folder: str,
        output_folder: str
) -> str:
    """
    Scan an input folder for PDF files, process them, and summarize the results.

    :param input_folder: Input folder path containing PDF files
    :param output_folder: Output folder path
    :return: A summary string of all processed files
    """
    client = DocumentIntelligenceClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_KEY)
    )

    summary = ""
    pdf_files_list = []
    for root, _, file_list in os.walk(input_folder):
        for filename in file_list:
            if filename.lower().endswith(".pdf"):
                pdf_files_list.append(os.path.join(root, filename))

    for pdf_path in pdf_files_list:
        summary += process_single_pdf(pdf_path, output_folder, client)

    return summary


# -----------------------------------------------------------------------------
# Main GUI
# -----------------------------------------------------------------------------
def start_gui() -> None:
    """
    Create and launch the GUI for selecting input/output folders and
    running the PDF processing operation.
    """
    from typing import Optional

    selected_input_folder: Optional[str] = None
    selected_output_folder: Optional[str] = None

    def select_input_folder() -> None:
        nonlocal selected_input_folder
        folder = filedialog.askdirectory(
            title="Choose a folder containing files to process"
        )
        if folder:
            selected_input_folder = folder
            input_folder_label.config(
                text=f"Input folder: {os.path.basename(selected_input_folder)}"
            )
        else:
            selected_input_folder = None
            input_folder_label.config(text="No input folder selected.")

    def select_output_folder() -> None:
        nonlocal selected_output_folder
        folder = filedialog.askdirectory(
            title="Choose a folder to save the output files"
        )
        if folder:
            selected_output_folder = folder
            output_folder_label.config(
                text=f"Output folder: {os.path.basename(selected_output_folder)}"
            )
        else:
            selected_output_folder = None
            output_folder_label.config(text="No output folder selected.")

    def run_processing() -> None:
        if not selected_input_folder or not selected_output_folder:
            messagebox.showwarning(
                "Folders missing",
                "Please select both input and output folders before running."
            )
            return

        status_label.config(text="Processing...")
        progress_bar.start()
        root_window.update_idletasks()

        result_text = handle_folder_upload(
            selected_input_folder,
            selected_output_folder
        )
        progress_bar.stop()
        output_text_box.delete("1.0", tk.END)
        output_text_box.insert(tk.END, result_text)
        status_label.config(text="Processing complete.")
        messagebox.showinfo(
            "Success",
            f"Files saved to {selected_output_folder}"
        )

    root_window = tk.Tk()
    root_window.title("OCR & Text Filter Tool")
    root_window.geometry("900x700")
    root_window.configure(bg="#f0f0f0")

    # Header Frame
    header_frame = tk.Frame(root_window, bg="#4a90e2", height=60)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    title_label = tk.Label(
        header_frame,
        text="OCR & Text Filter Tool",
        font=("Helvetica", 24, "bold"),
        fg="white",
        bg="#4a90e2"
    )
    title_label.grid(row=0, column=0, padx=10, pady=20)

    # Main Frame
    main_frame = tk.Frame(root_window, bg="#f0f0f0")
    main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    main_frame.grid_columnconfigure(0, weight=1)

    # Button Frame
    button_frame = tk.Frame(main_frame, bg="#f0f0f0")
    button_frame.grid(row=0, column=0, pady=10)

    # Folder Selection Buttons
    input_folder_btn = tk.Button(
        button_frame,
        text="Select Input Folder",
        command=select_input_folder,
        font=("Helvetica", 12),
        bg="#4a90e2",
        fg="white",
        padx=10,
        pady=5
    )
    input_folder_btn.grid(row=0, column=0, padx=10)

    output_folder_btn = tk.Button(
        button_frame,
        text="Select Output Folder",
        command=select_output_folder,
        font=("Helvetica", 12),
        bg="#4a90e2",
        fg="white",
        padx=10,
        pady=5
    )
    output_folder_btn.grid(row=0, column=1, padx=10)

    # Labels for Folder Paths
    input_folder_label = tk.Label(
        button_frame,
        text="No input folder selected",
        font=("Helvetica", 12),
        bg="#f0f0f0"
    )
    input_folder_label.grid(row=1, column=0, pady=5)

    output_folder_label = tk.Label(
        button_frame,
        text="No output folder selected",
        font=("Helvetica", 12),
        bg="#f0f0f0"
    )
    output_folder_label.grid(row=1, column=1, pady=5)

    # Run Button
    run_button = tk.Button(
        button_frame,
        text="Run",
        command=run_processing,
        font=("Helvetica", 12),
        bg="#4a90e2",
        fg="white",
        padx=10,
        pady=5
    )
    run_button.grid(row=0, column=2, pady=10)

    # Output Text Area
    output_text_box = scrolledtext.ScrolledText(
        main_frame,
        wrap=tk.WORD,
        width=100,
        height=25,
        font=("Courier", 10)
    )
    output_text_box.grid(row=4, column=0, pady=10)

    # Status Label
    status_label = tk.Label(
        main_frame,
        text="",
        font=("Helvetica", 10),
        bg="#f0f0f0",
        fg="#4a90e2"
    )
    status_label.grid(row=5, column=0, pady=5)

    # Footer with Progress Bar
    footer_frame = tk.Frame(main_frame, bg="#f0f0f0", height=40)
    footer_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
    footer_frame.grid_columnconfigure(0, weight=1)

    progress_bar = ttk.Progressbar(
        footer_frame,
        orient="horizontal",
        mode="indeterminate",
        length=400
    )
    progress_bar.grid(row=0, column=0, pady=10)

    root_window.mainloop()


# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    start_gui()
