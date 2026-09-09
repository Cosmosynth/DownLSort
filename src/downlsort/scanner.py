from pathlib import Path



downloads = Path.home() / "Downloads"
IMAGE_TYPES = {".jpg", ".jpeg", ".png"}
DOC_TYPES = {".pdf", ".docx", ".doc", ".odt", ".rtf", ".pages", ".txt", ".epub"}

def file_type_scan():
    for file in downloads.iterdir():
        if file.is_file():
            print(file.suffix)

def download_dir_scan():
    for item in downloads.iterdir():
        if item.is_dir():
            print(item.name)


def download_file_scan():
    for item in downloads.iterdir():
        if item.is_file():
            print(item.name)


def pdf_scan():
    for item in downloads.iterdir():
        if item.is_file() and item.suffix.lower() == ".pdf":
            print(item.name)

def image_scan():
    for item in downloads.iterdir():
        if item.is_file() and item.suffix.lower() in IMAGE_TYPES:
            print(item.name)


def docs_scan():
    for item in downloads.iterdir():
        if item.is_file() and item.suffix.lower() in DOC_TYPES:
            print(item.name)



def user_search():
    search_term = input("\nEnter the keyword to search for: ").lower()
    print(f"\nSearching for '{search_term}'...\n")

    found = False
    for item in downloads.iterdir():
        if search_term in item.name.lower():
            kind = "DIR " if item.is_dir() else "FILE"
            print(f"[{kind}] {item.name}")
            found = True

    if not found:
        print("No matching files or directories found.")

file_type_scan()