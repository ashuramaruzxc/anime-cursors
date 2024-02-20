import argparse
import os
import json
from win2xcur import writer,parser

def list_files_with_format(directory, file_format, recursive=False):
    # Ensure the file_format starts with a dot for consistency
    file_format = '.' + file_format if not file_format.startswith('.') else file_format
    matched_files = []
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(file_format):
                    matched_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if file.endswith(file_format) and os.path.isfile(os.path.join(directory, file)):
                matched_files.append(os.path.join(directory, file))
    return matched_files

def load_help_menu():
    with open("menu.json", "r") as file:
        help_menu = json.load(file)
    return help_menu

def generate_help_message(help_menu):
    description = help_menu["description"]
    version = help_menu["version"]
    arguments = help_menu["arguments"]

    help_message = f"{description}\n\nArguments:\n"
    for arg in arguments:
        help_message += f"{arg['name']}: {arg['description']}\n"
    help_message += f"\nVersion: {version}"
    return help_message

def main():
    help_menu = load_help_menu()
    parser = argparse.ArgumentParser(description=help_menu["description"])
    parser.add_argument('-d', '--dir', '--directory', type=str, help='Directory to list')
    parser.add_argument('-r', '--recursive', action='store_true', help='Set to list directories recursively')
    parser.add_argument('--format', type=str, choices=['ani', 'cur'], help='File format to filter by (ani or cur)')
    parser.add_argument('-o', '--output', type=str, help='Output directory')
    parser.add_argument('--name',type=str,help='specifies the cursor theme name in index.theme')
    parser.add_argument('--comment',type=str, help='specifies the index.theme description')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print verbose output')
    parser.add_argument('--version', action='version', version=help_menu["version"])
    args = parser.parse_args()

    if args.dir:
        directory = args.dir
        if not os.path.isdir(directory):
            print(f"Error: '{directory}' is not a valid directory.")
            return
    else:
        print("Error: Please specify a directory using -d or --dir")
        return

    if args.format:
        # Adjust file extension based on the provided format argument
        file_extension = '.' + args.format
        files = list_files_with_format(directory, file_extension, args.recursive)
        for file in files:
            if args.verbose:
                print("File Path:", file)
            print("File Name:", os.path.basename(file))
    else:
        print("Error: Please specify a file format using --format as 'ani' or 'cur'")
        return

if __name__ == '__main__':
    main()
