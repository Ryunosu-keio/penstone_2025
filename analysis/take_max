import os
import pandas as pd

def count_lines_in_directory(directory_path):
    """
    Count lines in all txt files within a directory.

    Parameters:
    - directory_path: The path to the directory.

    Returns:
    - Dictionary with file names as keys and their respective line counts as values.
    """
    line_counts = {}

    for file in os.listdir(directory_path):
        if file.endswith(".txt"):
            file_path = os.path.join(directory_path, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                line_counts[file] = len(f.readlines()) - 1

    return line_counts

if __name__ == "__main__":
    base_directory = "log"
    all_counts = {}

    for i in range(2, 11):
        sub_directory = os.path.join(base_directory, str(i))
        all_counts[str(i)] = count_lines_in_directory(sub_directory)

    df = pd.DataFrame(all_counts).fillna(0).astype(int)
    print(df)
