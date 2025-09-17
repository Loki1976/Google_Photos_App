import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import os
import json
from PIL import Image
import piexif
import datetime

class GooglePhotosMetadataApp:
    """
    A GUI application to transfer photo metadata from Google Takeout JSON files
    to their corresponding image files' EXIF data, including all subdirectories.
    """

    def __init__(self, master):
        """
        Initializes the application and its GUI components.

        Args:
            master (tk.Tk): The root Tkinter window.
        """
        self.master = master
        self.master.title("Google Photos Metadata Transfer (Recursive)")
        self.master.geometry("500x350")
        
        self.folder_path = None
        
        self._create_widgets()

    def _create_widgets(self):
        """Creates and places all the GUI widgets."""
        control_frame = tk.Frame(self.master, padx=10, pady=10)
        control_frame.pack(fill="x")
        
        self.path_label = tk.Label(control_frame, text="No folder selected", wraplength=450)
        self.path_label.pack(side="left", fill="x", expand=True)
        
        browse_button = tk.Button(control_frame, text="Browse", command=self._browse_folder)
        browse_button.pack(side="right")
        
        self.progress_bar = Progressbar(self.master, orient="horizontal", length=480, mode="determinate")
        self.progress_bar.pack(pady=10, padx=10, fill="x")
        
        self.process_button = tk.Button(self.master, text="Process Files", command=self._process_files, state=tk.DISABLED)
        self.process_button.pack(pady=5)
        
        self.log_text = tk.Text(self.master, wrap="word", width=60, height=10, state=tk.DISABLED)
        self.log_text.pack(pady=10, padx=10)

    def _log_message(self, message):
        """
        Appends a message to the log display and updates the GUI.

        Args:
            message (str): The message to log.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.master.update_idletasks()

    def _browse_folder(self):
        """Opens a dialog for the user to select a folder."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path = folder_path
            self.path_label.config(text=folder_path)
            self.process_button.config(state=tk.NORMAL)
            self._log_message(f"Selected folder: {folder_path}")
            
    def _process_files(self):
        """
        Initiates the metadata transfer process for all files in the selected folder and its subdirectories.
        """
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder.")
            return

        self.process_button.config(state=tk.DISABLED)
        self._log_message("Starting recursive file processing...")

        # Find all JSON files in the directory and its subdirectories
        json_files = []
        for dirpath, _, filenames in os.walk(self.folder_path):
            for filename in filenames:
                if filename.endswith('.json'):
                    json_files.append(os.path.join(dirpath, filename))
        
        if not json_files:
            self._log_message("No JSON files found in the selected folder or its subdirectories.")
            messagebox.showinfo("Done", "No JSON files to process.")
            self.process_button.config(state=tk.NORMAL)
            return

        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(json_files)

        for i, json_path in enumerate(json_files):
            self._update_exif_from_json(json_path)
            self.progress_bar['value'] += 1
            self.master.update_idletasks()
            
        self._log_message("All files processed. Task completed.")
        self.process_button.config(state=tk.NORMAL)
        messagebox.showinfo("Done", "Processing complete!")

    def _update_exif_from_json(self, json_path):
        """
        Finds the corresponding image for a given JSON file and updates its EXIF data.
        
        Args:
            json_path (str): The full path to the JSON metadata file.
        """
        dir_path, json_filename = os.path.split(json_path)
        base_name = os.path.splitext(json_filename)[0]
        
        image_filename = None
        # Check for common image extensions
        for ext in ['', '.jpg', '.jpeg', '.png', '.gif', '.webp']:
            potential_image = base_name + ext
            image_path = os.path.join(dir_path, potential_image)
            if os.path.exists(image_path):
                image_filename = potential_image
                break
        
        if not image_filename:
            self._log_message(f"  - No matching image found for {json_filename}. Skipping.")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            timestamp_unix = data.get('photoTakenTime', {}).get('timestamp')
            
            if not timestamp_unix:
                self._log_message(f"  - No timestamp found in {json_filename}. Skipping.")
                return

            original_dt = datetime.datetime.fromtimestamp(int(timestamp_unix))
            exif_date_str = original_dt.strftime('%Y:%m:%d %H:%M:%S')

            image_path_full = os.path.join(dir_path, image_filename)
            img = Image.open(image_path_full)
            exif_dict = piexif.load(img.info.get("exif", b""))
            
            exif_dict["0th"][piexif.ImageIFD.DateTime] = exif_date_str.encode('utf-8')
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_date_str.encode('utf-8')
            exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = exif_date_str.encode('utf-8')
            
            exif_bytes = piexif.dump(exif_dict)
            
            img.save(image_path_full, exif=exif_bytes)
            self._log_message(f"  - Successfully updated {image_filename}.")

        except Exception as e:
            self._log_message(f"  - ERROR: Could not process {json_filename}. Reason: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GooglePhotosMetadataApp(root)
    root.mainloop()