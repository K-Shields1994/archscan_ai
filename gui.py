import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os


def start_gui(handle_folder_upload, handle_save_output):
    """
    Starts the Tkinter GUI and handles user interactions.
    """

    # Initialize variables to hold selected folders
    selected_input_folder = None
    selected_output_folder = None

    def upload_folder():
        nonlocal selected_input_folder
        selected_input_folder = filedialog.askdirectory(
            title="Choose a folder containing files to process"
        )
        if selected_input_folder:
            folder_label.config(text=f"Input folder: {os.path.basename(selected_input_folder)}")
            status_label.config(text="Input folder selected.")
        else:
            messagebox.showwarning("No folder selected", "Please select an input folder.")
            status_label.config(text="No input folder selected.")

    def choose_output_folder():
        nonlocal selected_output_folder
        selected_output_folder = filedialog.askdirectory(
            title="Choose a folder to save the output files"
        )
        if selected_output_folder:
            destination_label.config(text=f"Output folder: {os.path.basename(selected_output_folder)}")
            status_label.config(text="Output folder selected.")
        else:
            messagebox.showwarning("No destination folder selected", "Please select an output folder.")
            status_label.config(text="No output folder selected.")

    def run_process():
        if not selected_input_folder or not selected_output_folder:
            messagebox.showwarning("Folders missing", "Please select both input and output folders before running.")
            return

        # Show a progress message
        status_label.config(text="Processing...")

        # Call the provided callback function to process the input folder and save the output
        result = handle_folder_upload(selected_input_folder, selected_output_folder)

        # Display the result in the text area
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, result)

        # Update status message
        status_label.config(text="Processing complete.")
        messagebox.showinfo("Success", f"Files saved to {selected_output_folder}")

    # Setup the GUI window
    root = tk.Tk()
    root.title("File Processor")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')  # Set background color

    # Header Frame with Title
    header_frame = tk.Frame(root, bg='#4a90e2', height=60)
    header_frame.pack(fill='x')
    title_label = tk.Label(header_frame, text="File Processor", font=("Helvetica", 24, "bold"), fg='white',
                           bg='#4a90e2')
    title_label.pack(pady=10)

    # Main frame for the content
    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Folder upload button
    upload_button = tk.Button(main_frame, text="Select Input Folder", command=upload_folder, font=("Helvetica", 12),
                              bg="#4a90e2", fg="white", padx=10, pady=5)
    upload_button.pack(pady=10)

    # Label to display selected input folder
    folder_label = tk.Label(main_frame, text="No input folder selected", font=("Helvetica", 12), bg="#f0f0f0")
    folder_label.pack(pady=5)

    # Button to choose output folder
    output_button = tk.Button(main_frame, text="Select Output Folder", command=choose_output_folder,
                              font=("Helvetica", 12),
                              bg="#4a90e2", fg="white", padx=10, pady=5)
    output_button.pack(pady=10)

    # Label to display selected output folder
    destination_label = tk.Label(main_frame, text="No output folder selected", font=("Helvetica", 12), bg="#f0f0f0")
    destination_label.pack(pady=5)

    # Button to run the process
    run_button = tk.Button(main_frame, text="Run", command=run_process, font=("Helvetica", 12),
                           bg="#4a90e2", fg="white", padx=10, pady=5)
    run_button.pack(pady=10)

    # Output area to display the results
    output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=100, height=25, font=("Courier", 10))
    output_text.pack(pady=10)

    # Status label for status updates
    status_label = tk.Label(main_frame, text="", font=("Helvetica", 10), bg="#f0f0f0", fg="#4a90e2")
    status_label.pack(pady=5)

    # Footer with progress bar
    footer_frame = tk.Frame(root, bg='#f0f0f0')
    footer_frame.pack(fill='x', pady=10)

    progress_bar = ttk.Progressbar(footer_frame, orient="horizontal", mode="indeterminate", length=400)
    progress_bar.pack(pady=10)

    root.mainloop()