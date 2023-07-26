from pathlib import Path


# Argument: filename in script directory
# Returns: fully qualified file path
def __find_file_in_directory(filename: str):
    script_dir = Path(__file__).resolve().parent
    file_path = script_dir / filename
    return file_path


# Argument: filename of .txt file in script directory
# Returns: raw text from file
def get_text(filename: str):
    # build fully qualified file path
    file_path = __find_file_in_directory(filename)

    # Create Path objects from the filepaths
    file = Path(file_path)

    # Check if the filepaths exist
    if not file.exists():
        raise FileNotFoundError("filepath does not exist.")

    # Read the text content from the files
    try:
        text = file.read_text()
    except Exception as e:
        raise Exception("Error occurred while reading the file:", e)

    return text
