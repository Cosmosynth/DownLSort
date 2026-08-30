from scanner import (
    download_dir_scan,
    download_file_scan,
    image_scan,
    pdf_scan,
    user_search, docs_scan
)

PROMPT = """Type "dir" to scan the Downloads folder
Type "files" to scan all the files in the Downloads folder
Type "pdf" to scan for pdf files
Type "image" to scan for images
Type "docs" to scan for documents file
Type "search" to search subdirs, files or pdfs in the download folder
Type "quit" to exit
>> """

while True:
    print("====== Downloads ======\n")
    choice = input(PROMPT).strip().lower()

    if choice == "dir":
        print("\nScanning the Downloads folder for directories...\n")
        download_dir_scan()


    elif choice in ["files", "file"]:
        print("\nScanning the Downloads folder for files...\n")
        download_file_scan()

    elif choice == "pdf":
        print("\nScanning the Downloads folder for PDFs...\n")
        pdf_scan()

    elif choice in ["doc", "docs", "documents", "document"]:
        print("\nScanning the Downloads folder for Documents...\n")
        docs_scan()


    elif choice in ["image", "images", "photos"]:
        print("\nScanning the Downloads folder for Images...\n")
        image_scan()


    elif choice == "search":
        user_search()

        
    elif choice in ["quit", "exit", "q"]:
        print("\nGoodbye.")
        break
    else:
        print("\nInvalid input. Please choose a valid option.\n")
