import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib
import os
import mysql.connector

mydb = mysql.connector.connect(
	host = "localhost",
	user = "root",
	password = "",
    database="hash"
)

def calculate_md5_for_file(file_path):
    md5_hash = hashlib.md5()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()

def calculate_md5_for_all_files(directory_path):
    md5_checksums = {}

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_md5 = calculate_md5_for_file(file_path)
            md5_checksums[file_path] = file_md5

    return md5_checksums

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            print(f"New directory created: {event.src_path}")
            file_md5_checksums = calculate_md5_for_all_files(event.src_path)

            for file_path, md5_checksum in file_md5_checksums.items():
                print(f"MD5 Checksum of {file_path}: {md5_checksum}")
        else:
            print(f"New file detected: {event.src_path}! Scanning...")
            calculate_md5_for_file(event.src_path)
            cursor = mydb.cursor()
            name= str(calculate_md5_for_file(event.src_path))
            cursor.execute("SELECT * from data WHERE hash = %s", (name,))

            rows = cursor.fetchone()
            if rows is None:
                print(event.src_path, "is safe!")
            else:
                print(event.src_path, "is virus!")
            

def monitor_folder(folder_path):
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    folder_to_monitor = "/Users/xy0ke/Downloads/"
    monitor_folder(folder_to_monitor)
