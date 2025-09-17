This Python program is a graphical user interface (GUI) application designed to transfer metadata from Google Takeout JSON files to their corresponding photo files. It is built using the tkinter library for the user interface and several other libraries for file handling and EXIF data manipulation, including Pillow and piexif.

The program simplifies the process of restoring important metadata, such as the original creation date, to your images after a Google Takeout export. It's a common issue that the original photo date isn't preserved in the downloaded files, but this information is stored in a separate JSON sidecar file. This application automates the task of reading that JSON data and embedding it into the photo's EXIF (Exchangeable Image File Format) data.

Key Features and Workflow
Folder Selection: Users can select a root directory containing their Google Photos export. The program then recursively searches all subdirectories for matching photo and JSON files.

Automated Matching: For each JSON file (.json), the program attempts to find a corresponding image file with the same base name but with a standard photo extension (e.g., .jpg, .jpeg, .png).

Metadata Extraction & Transfer:

It reads the photoTakenTime Unix timestamp from the JSON file.

It converts this timestamp into a standard date and time format (YYYY:MM:DD HH:MM:SS).

Using the piexif library, it updates the photo's EXIF data, specifically the DateTimeOriginal, DateTimeDigitized, and DateTime tags, ensuring the correct date is written to the image file.

Progress and Logging:

A progress bar provides a visual representation of the processing status.

A real-time log window shows a detailed report of which files were processed, which were skipped due to missing counterparts, and any errors that occurred.

Robust Error Handling: The program is designed to handle potential issues gracefully, such as missing timestamps in the JSON file or corrupted image files, logging the error without halting the entire process.

This program is a practical tool for anyone who has used Google Takeout and needs to properly organize their digital photo collection by restoring the correct date and time metadata to their files.
