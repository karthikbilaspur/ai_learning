import os
from googletrans import Translator
import shutil
from datetime import datetime

def rename_files(directory: str, old_name: str, new_name: str, languages: list[str]):
    translator = Translator()
    for filename in os.listdir(directory):
        if old_name in filename:
            file_extension = os.path.splitext(filename)[1]
            for language in languages:
                translation = translator.translate(new_name, dest=language)
                new_filename = filename.replace(old_name, translation.text)
                shutil.copy(os.path.join(directory, filename), os.path.join(directory, new_filename))
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Renamed {filename} to {new_filename} at {current_time}")

def rename_files_without_translation(directory: str, old_name: str, new_name: str):
    for filename in os.listdir(directory):
        if old_name in filename:
            new_filename = filename.replace(old_name, new_name)
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Renamed {filename} to {new_filename} at {current_time}")

def main():
    print("File Renamer")
    print("1. Rename files with translation")
    print("2. Rename files without translation")
    choice = input("Enter your choice: ")

    directory = input("Enter the directory path: ")
    old_name = input("Enter the old name: ")

    if choice == "1":
        new_name = input("Enter the new name: ")
        languages = input("Enter the languages (comma-separated, e.g. en, es, fr): ").split(',')
        languages = [lang.strip() for lang in languages]
        rename_files(directory, old_name, new_name, languages)
    elif choice == "2":
        new_name = input("Enter the new name: ")
        rename_files_without_translation(directory, old_name, new_name)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()