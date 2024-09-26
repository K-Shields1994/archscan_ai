import tkinter as tk
from tkinter import filedialog, scrolledtext


def run_gui(handle_process_function):
    root = tk.Tk()
    root.title("Document OCR Tool")

    input_folder = None
    output_folder = None

    def upload_folder():
        nonlocal input_folder
        input_folder = filedialog.askdirectory()
        folder_label.config(text=f"Input: {input_folder}")

    def choose_output_folder():
        nonlocal output_folder
        output_folder = filedialog.askdirectory()
        destination_label.config(text=f"Output: {output_folder}")

    def run_process():
        if input_folder and output_folder:
            handle_process_function(input_folder, output_folder)
            status_label.config(text="Processing complete!")
        else:
            status_label.config(text="Please select both input and output folders.")

    # Create GUI components (buttons, labels, etc.)
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # Button to upload folder
    upload_button = tk.Button(button_frame, text="Select Input Folder", command=upload_folder)
    upload_button.grid(row=0, column=0, padx=10)

    # Button to choose output folder
    output_button = tk.Button(button_frame, text="Select Output Folder", command=choose_output_folder)
    output_button.grid(row=0, column=1, padx=10)

    # Label to display selected input folder
    folder_label = tk.Label(button_frame, text="No input folder selected")
    folder_label.grid(row=1, column=0, pady=5)

    # Label to display selected output folder
    destination_label = tk.Label(button_frame, text="No output folder selected")
    destination_label.grid(row=1, column=1, pady=5)

    # Button to run the process
    run_button = tk.Button(button_frame, text="Run", command=run_process)
    run_button.grid(row=0, column=2, pady=10)

    # Output status label
    status_label = tk.Label(root, text="")
    status_label.pack(pady=10)

    root.mainloop()