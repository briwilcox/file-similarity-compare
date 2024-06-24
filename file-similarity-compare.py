import os
import argparse
from difflib import SequenceMatcher
from tabulate import tabulate

def read_file(file_path):
    with open(file_path, 'r', errors='ignore') as file:
        return file.read()

def calculate_similarity(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

def compare_files(target_file, directory):
    target_content = read_file(target_file)
    results = []
    target_file_name = os.path.basename(target_file)

    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.samefile(file_path, target_file):
                continue  # Skip the target file itself
            try:
                content = read_file(file_path)
                similarity = calculate_similarity(target_content, content)
                relative_path = os.path.relpath(file_path, directory)
                results.append((relative_path, similarity))
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

    return sorted(results, key=lambda x: x[1], reverse=True)

def display_results(results, threshold=None):
    if threshold:
        filtered_results = [(f, s) for f, s in results if s >= threshold]
        print(f"\nFiles with similarity ≥{threshold*100}%:")
    else:
        filtered_results = results
        print("\nAll comparisons:")

    if filtered_results:
        headers = ["Filename", "Similarity Score"]
        table = tabulate([(f, f"{s:.2%}") for f, s in filtered_results], headers=headers, tablefmt="grid")
        print(table)
    else:
        print("No files found matching the criteria.")

def main():
    parser = argparse.ArgumentParser(description="Compare file similarity in a directory.")
    parser.add_argument("target_file", help="Path to the target file for comparison")
    parser.add_argument("-d", "--directory", default=".", help="Directory to search for files (default: current directory)")
    args = parser.parse_args()

    target_file = os.path.abspath(args.target_file)
    directory = os.path.abspath(args.directory)

    if not os.path.isfile(target_file):
        print(f"Error: Target file '{target_file}' does not exist.")
        return

    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    print(f"Comparing '{target_file}' with files in '{directory}' (including subdirectories)...")
    results = compare_files(target_file, directory)
    
    display_results(results, threshold=0.95)  # Display high similarity results (≥95%)
    display_results(results)  # Display all results

if __name__ == "__main__":
    main()
