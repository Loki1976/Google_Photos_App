import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import os
import json
from PIL import Image
import piexif

class GooglePhotosMetadataApp:
    def __init__(self, master):
        self.master = master
        master.title("Google Photos Metadata Transfer")
        master.geometry("500x350")
        
        self.create_widgets()

    def create_widgets(self):
        # Frame for controls
        control_frame = tk.Frame(self.master, padx=10, pady=10)
        control_frame.pack(fill="x")
        
        # Folder selection
        self.path_label = tk.Label(control_frame, text="No folder selected", wraplength=450)
        self.path_label.pack(side="left", fill="x", expand=True)
        
        self.browse_button = tk.Button(control_frame, text="Browse", command=self.browse_folder)
        self.browse_button.pack(side="right")
        
        # Progress bar
        self.progress_bar = Progressbar(self.master, orient="horizontal", length=480, mode="determinate")
        self.progress_bar.pack(pady=10)
        
        # Process button
        self.process_button = tk.Button(self.master, text="Process Files", command=self.process_files, state=tk.DISABLED)
        self.process_button.pack(pady=5)
        
        # Log display
        self.log_text = tk.Text(self.master, wrap="word", width=60, height=10, state=tk.DISABLED)
        self.log_text.pack(pady=10)

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.master.update_idletasks() # Refresh the UI

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path = folder_path
            self.path_label.config(text=folder_path)
            self.process_button.config(state=tk.NORMAL)
            self.log_message(f"Selected folder: {folder_path}")
            
    def process_files(self):
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder.")
            return

        self.process_button.config(state=tk.DISABLED)
        self.log_message("Starting file processing...")

        # Find all JSON and image files
        all_files = os.listdir(self.folder_path)
        json_files = [f for f in all_files if f.endswith('.json')]
        
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(json_files)

        for i, json_filename in enumerate(json_files):
            base_name = os.path.splitext(json_filename)[0]
            
            # Find the corresponding image file
            image_filename = None
            if os.path.exists(os.path.join(self.folder_path, base_name)): # Handles .jpg.json
                image_filename = base_name
            elif os.path.exists(os.path.join(self.folder_path, base_name + '.jpg')):
                image_filename = base_name + '.jpg'
            elif os.path.exists(os.path.join(self.folder_path, base_name + '.jpeg')):
                image_filename = base_name + '.jpeg'
            
            if not image_filename:
                self.log_message(f"  - No matching image found for {json_filename}. Skipping.")
                self.progress_bar['value'] += 1
                continue

            # Load and process the JSON and image
            try:
                json_path = os.path.join(self.folder_path, json_filename)
                image_path = os.path.join(self.folder_path, image_filename)

                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract the timestamp from Google Takeout JSON
                # The timestamp is typically a Unix timestamp (seconds since epoch)
                photo_taken_time_unix = data.get('photoTakenTime', {}).get('timestamp')
                
                if photo_taken_time_unix:
                    # Convert Unix timestamp to a Python datetime object
                    import datetime
                    original_dt = datetime.datetime.fromtimestamp(int(photo_taken_time_unix))
                    
                    # Format the date string for EXIF (YYYY:MM:DD HH:MM:SS)
                    exif_date_str = original_dt.strftime('%Y:%m:%d %H:%M:%S')

                    # Open the image with Pillow
                    img = Image.open(image_path)
                    
                    # Get existing EXIF data or create a new one
                    exif_dict = piexif.load(img.info.get("exif", b""))
                    
                    # Update DateTimeOriginal, DateTime, and DateTimeDigitized tags
                    # The tags are numeric keys. Piexif provides constants for them.
                    exif_dict["0th"][piexif.ImageIFD.DateTime] = exif_date_str
                    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_date_str
                    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = exif_date_str
                    
                    # Dump the dictionary to bytes
                    exif_bytes = piexif.dump(exif_dict)
                    
                    # Save the image with the new EXIF data
                    img.save(image_path, exif=exif_bytes)
                    self.log_message(f"  - Successfully updated {image_filename}.")

            except Exception as e:
                self.log_message(f"  - ERROR: Could not process {json_filename}. Reason: {e}")
            finally:
                self.progress_bar['value'] += 1
                self.master.update_idletasks() # Ensure the UI updates

        self.log_message("All files processed. Task completed.")
        self.process_button.config(state=tk.NORMAL)
        messagebox.showinfo("Done", "Processing complete!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GooglePhotosMetadataApp(root)
    root.mainloop()