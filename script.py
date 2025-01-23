import os

def create_text_from_files(directory, output_file):
    """
    Reads all files in a directory (including subdirectories) and writes their content to a single .txt file.
    
    Args:
        directory (str): The root directory to start scanning.
        output_file (str): The output file where all the file contents will be saved.
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Read and write content from the file
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(f"Contents of file: {file_path}\n")
                        outfile.write(infile.read())
                        outfile.write("\n" + "="*50 + "\n")
                except Exception as e:
                    outfile.write(f"Error reading file {file_path}: {e}\n")
                    outfile.write("\n" + "="*50 + "\n")

# Customize the directory and output file name
directory_to_scan = r"I:\travelai-backend"  # Replace with the directory you want to scan
output_file_name = "output.txt"              # Replace with your desired output file name

create_text_from_files(directory_to_scan, output_file_name)

print(f"Contents of all files in '{directory_to_scan}' have been saved to '{output_file_name}'.")
