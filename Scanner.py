from pathlib import Path
import os

#user's Downloads folder
downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
p = Path(downloads_path)

def download_dir_scan():
    for subdir in p.iterdir():
        if subdir.is_dir():
            print(subdir.name)

def download_file_scan():
    for file in p.iterdir():
        if file.is_file():
            print(file.name)

def pdf_scan():
    for file in p.iterdir():
        if file.is_file() and file.suffix.lower() == ".pdf":
            print(file.name)

def image_scan():
    for file in p.iterdir():
        if file.is_file() and file.suffix.lower() == ".jpeg" or file.suffix.lower() == ".png" or file.suffix.lower() == ".jpg":
            print(file.name)

def user_search():
    search_term = input("\nEnter the keyword to search for: ").lower()
    print(f"\nSearching for '{search_term}'...\n")
    
    found_items = False
    for item in p.iterdir():
        if search_term in item.name.lower():
            item_type = "DIR " if item.is_dir() else "FILE"
            print(f"[{item_type}] {item.name}")
            found_items = True
            
    if not found_items:
        print("No matching files or directories found.")


print("====== Downloads ======\n")


prompt_text = """Type "dir" to scan the Downloads folder
Type "files" to scan all the files in the Downloads folder
Type "pdf" to scan for pdf files
Type "image" to scan for images
Type "search" to search subdirs, files or pdfs in the download folder
> """

scan = input(prompt_text).strip().lower() #Strip whitespace, convert to lowercase

if scan == "dir":
    print("\nScanning the Downloads folder for directories...\n")
    download_dir_scan()

elif scan in ["files", "file"]:
    print("\nScanning the Downloads folder for files...\n")
    download_file_scan()


elif scan == "pdf":
    print("\nScanning the Downloads folder for PDFs...\n")
    pdf_scan()

elif scan == "image" or scan == "images" or scan == "photos" :
    print("\nScanning the Downloads folder for Images...\n")
    image_scan()

elif scan == "search":
    user_search()

else:
    print("\nInvalid input. Please run the script again and choose a valid option.\n")