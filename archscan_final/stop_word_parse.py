import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import json


def load_stop_words(file_path):
    """
    Loads stop words from a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Stop words file not found: {file_path}")
        return set()


def filter_text_from_json(json_file_path, stop_words, output_txt_path):
    """
    Parses a JSON file, filters out stop words, and writes the cleaned text to a text file.
    """
    try:
        # Load JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_text = []

        # Process each page
        for page in data.get("pages", []):
            for line in page.get("lines", []):
                content = line.get("content", "")
                words = content.split()
                filtered_words = [word for word in words if word.lower() not in stop_words]
                filtered_text.append(" ".join(filtered_words))

        # Write the filtered text to a file
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(filtered_text))
    except Exception as e:
        print(f"Error processing JSON file {json_file_path}: {e}")


def process_folder(input_folder, output_folder, stop_words_file):
    """
    Processes all JSON files in a folder, filters out stop words, and saves the results.
    """
    stop_words = load_stop_words(stop_words_file)
    if not stop_words:
        return "No stop words loaded. Operation aborted.\n"

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    result_summary = ""

    # Process all JSON files in the input folder
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".json"):
                input_path = os.path.join(root, file)
                output_file_name = os.path.splitext(file)[0] + "_filtered.txt"
                output_path = os.path.join(output_folder, output_file_name)
                filter_text_from_json(input_path, stop_words, output_path)
                result_summary += f"Processed: {file}\n"

    return result_summary


def start_gui():
    selected_input_folder = None
    selected_output_folder = None
    stop_words_path = "text_files/stop_words.txt"  # Default path to stop words file

    def select_input_folder():
        nonlocal selected_input_folder
        selected_input_folder = filedialog.askdirectory(title="Select Input Folder")
        input_folder_label.config(
            text=f"Input folder: {os.path.basename(selected_input_folder)}" if selected_input_folder else "No folder selected."
        )

    def select_output_folder():
        nonlocal selected_output_folder
        selected_output_folder = filedialog.askdirectory(title="Select Output Folder")
        output_folder_label.config(
            text=f"Output folder: {os.path.basename(selected_output_folder)}" if selected_output_folder else "No folder selected."
        )

    def run_process():
        if not selected_input_folder or not selected_output_folder:
            messagebox.showwarning("Folders missing", "Please select both input and output folders.")
            return

        if not os.path.exists(stop_words_path):
            messagebox.showerror("Error", f"Stop words file not found at: {stop_words_path}")
            return

        status_label.config(text="Processing...")
        progress_bar.start()
        root.update_idletasks()

        result = process_folder(selected_input_folder, selected_output_folder, stop_words_path)
        progress_bar.stop()
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, result)
        status_label.config(text="Processing complete.")
        messagebox.showinfo("Success", f"Files saved to {selected_output_folder}")

    # GUI Initialization
    root = tk.Tk()
    root.title("JSON Text Filter")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')

    # Header Frame
    header_frame = tk.Frame(root, bg='#4a90e2', height=60)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    title_label = tk.Label(header_frame, text="JSON Text Filter", font=("Helvetica", 24, "bold"), fg='white', bg='#4a90e2')
    title_label.grid(row=0, column=0, padx=10, pady=20)

    # Main Frame
    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    main_frame.grid_columnconfigure(0, weight=1)

    # Button Frame
    button_frame = tk.Frame(main_frame, bg='#f0f0f0')
    button_frame.grid(row=0, column=0, pady=10)

    # Folder Selection Buttons
    input_button = tk.Button(button_frame, text="Select Input Folder", command=select_input_folder, font=("Helvetica", 12),
                              bg="#4a90e2", fg="white", padx=10, pady=5)
    input_button.grid(row=0, column=0, padx=10)

    output_button = tk.Button(button_frame, text="Select Output Folder", command=select_output_folder,
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
    footer_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
    footer_frame.grid_columnconfigure(0, weight=1)

    progress_bar = ttk.Progressbar(footer_frame, orient="horizontal", mode="indeterminate", length=400)
    progress_bar.grid(row=0, column=0, pady=10)

    root.mainloop()


# Start the GUI
start_gui()