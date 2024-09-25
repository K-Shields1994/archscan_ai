import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os


def start_gui(handle_folder_upload):
    """
    Starts the Tkinter GUI and handles user interactions.
    """

    def upload_folder():
        folder_path = filedialog.askdirectory(
            title="Choose a folder containing PDF files"
        )
        if folder_path:
            folder_label.config(text=f"Selected folder: {os.path.basename(folder_path)}")

            # Show a progress message
            status_label.config(text="Processing...")

            # Call the provided callback function to process the folder
            result = handle_folder_upload(folder_path)

            # Clear the text area
            output_text.delete(1.0, tk.END)

            # Insert result into the output text area
            output_text.insert(tk.END, result)

            # Update status message
            status_label.config(text="Processing complete.")
        else:
            messagebox.showwarning("No folder selected", "Please select a folder containing PDF files.")
            status_label.config(text="No folder selected.")

    # Setup the GUI window
    root = tk.Tk()
    root.title("PDF Analyzer")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')  # Set background color

    # Header Frame with Title
    header_frame = tk.Frame(root, bg='#4a90e2', height=60)
    header_frame.pack(fill='x')
    title_label = tk.Label(header_frame, text="PDF Analyzer", font=("Helvetica", 24, "bold"), fg='white', bg='#4a90e2')
    title_label.pack(pady=10)

    # Main frame for the content
    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Folder upload button
    upload_button = tk.Button(main_frame, text="Upload Folder", command=upload_folder, font=("Helvetica", 12),
                              bg="#4a90e2", fg="white", padx=10, pady=5)
    upload_button.pack(pady=10)

    # Label to display selected folder
    folder_label = tk.Label(main_frame, text="No folder selected", font=("Helvetica", 12), bg="#f0f0f0")
    folder_label.pack(pady=5)

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