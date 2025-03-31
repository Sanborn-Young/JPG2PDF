import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import img2pdf
from PIL import Image
import tempfile
import threading

class ImageToPdfConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("JPEG to PDF with OCR Text Layer")
        self.root.geometry("800x600")
        
        self.selected_directory = tk.StringVar()
        self.selected_files = []
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Directory selection
        frame1 = ttk.Frame(self.root, padding=10)
        frame1.pack(fill=tk.X)
        
        ttk.Label(frame1, text="Directory:").pack(side=tk.LEFT)
        ttk.Entry(frame1, textvariable=self.selected_directory, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame1, text="Browse", command=self.browse_directory).pack(side=tk.LEFT)
        
        # File list
        frame2 = ttk.Frame(self.root, padding=10)
        frame2.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame2, text="Files:").pack(anchor=tk.W)
        
        # Create Treeview for file list
        self.tree_view = ttk.Treeview(frame2, columns=("Filename", "Status"), show="headings")
        self.tree_view.heading("Filename", text="Filename")
        self.tree_view.heading("Status", text="Status")
        self.tree_view.column("Filename", width=400)
        self.tree_view.column("Status", width=100)
        self.tree_view.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        frame3 = ttk.Frame(self.root, padding=10)
        frame3.pack(fill=tk.X)
        
        ttk.Label(frame3, text="Progress:").pack(side=tk.LEFT)
        ttk.Progressbar(frame3, variable=self.progress_var, length=500, mode="determinate").pack(side=tk.LEFT, padx=5)
        
        # Status label
        ttk.Label(frame3, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        frame4 = ttk.Frame(self.root, padding=10)
        frame4.pack(fill=tk.X)
        
        ttk.Button(frame4, text="Select All", command=self.select_all_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame4, text="Convert Selected", command=self.convert_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame4, text="Convert All", command=self.convert_all).pack(side=tk.LEFT, padx=5)
    
    def browse_directory(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_directory.set(folder_path)
            self.list_files(folder_path)
    
    def list_files(self, folder_path):
        # Clear existing items
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
        
        # List image files
        self.selected_files = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg')):
                self.tree_view.insert("", "end", values=(filename, "Pending"))
                self.selected_files.append(os.path.join(folder_path, filename))
    
    def select_all_files(self):
        for item in self.tree_view.get_children():
            self.tree_view.selection_add(item)
    
    def convert_selected(self):
        selected_items = self.tree_view.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one file")
            return
        
        # Get the selected file paths
        files_to_convert = []
        for item in selected_items:
            file_name = self.tree_view.item(item, "values")[0]
            file_path = os.path.join(self.selected_directory.get(), file_name)
            files_to_convert.append((item, file_path))
        
        # Start conversion in a separate thread
        threading.Thread(target=self.process_files, args=(files_to_convert,), daemon=True).start()
    
    def convert_all(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "No files found in the selected directory")
            return
        
        # Get all file paths
        files_to_convert = []
        for item in self.tree_view.get_children():
            file_name = self.tree_view.item(item, "values")[0]
            file_path = os.path.join(self.selected_directory.get(), file_name)
            files_to_convert.append((item, file_path))
        
        # Start conversion in a separate thread
        threading.Thread(target=self.process_files, args=(files_to_convert,), daemon=True).start()
    
    def process_files(self, files_to_convert):
        total_files = len(files_to_convert)
        processed_files = 0
        
        self.progress_var.set(0)
        self.status_var.set(f"Processing 0/{total_files}")
        
        for item, file_path in files_to_convert:
            file_name = os.path.basename(file_path)
            
            try:
                # Update status in the UI
                self.update_tree_item(item, "Converting")
                
                # Create output filename
                base_name = os.path.splitext(file_name)[0]
                temp_pdf = os.path.join(tempfile.gettempdir(), f"{base_name}_temp.pdf")
                output_pdf = os.path.join(self.selected_directory.get(), f"{base_name}_ocr_txt.pdf")
                
                # Convert JPEG to PDF
                self.jpeg_to_pdf(file_path, temp_pdf)
                
                # Update status
                self.update_tree_item(item, "Adding OCR")
                
                # Add OCR text layer
                self.add_ocr_layer(temp_pdf, output_pdf)
                
                # Clean up temp file
                if os.path.exists(temp_pdf):
                    os.remove(temp_pdf)
                
                # Update status
                self.update_tree_item(item, "Completed")
                
            except Exception as e:
                self.update_tree_item(item, "Failed")
                print(f"Error processing {file_name}: {str(e)}")
            
            # Update progress
            processed_files += 1
            progress_percentage = (processed_files / total_files) * 100
            self.progress_var.set(progress_percentage)
            self.status_var.set(f"Processing {processed_files}/{total_files}")
        
        self.status_var.set(f"Completed {processed_files}/{total_files}")
    
    def update_tree_item(self, item, status):
        # Update the status column in the treeview
        # This needs to be run in the main thread
        self.root.after(0, lambda: self.tree_view.item(item, values=(self.tree_view.item(item, "values")[0], status)))
    
    def jpeg_to_pdf(self, image_path, output_path):
        # Convert JPEG to PDF using img2pdf
        with open(output_path, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(image_path))
    
    def add_ocr_layer(self, input_pdf, output_pdf):
        # Use ocrmypdf to add a text layer
        cmd = [
            "ocrmypdf",
            "--skip-text",  # Skip if text layer exists
            "--deskew",     # Straighten pages
            "--clean",      # Clean before OCR
            "--language", "eng",  # English language
            input_pdf,      # Input PDF
            output_pdf      # Output PDF
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"OCR failed: {result.stderr}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToPdfConverter(root)
    root.mainloop()
