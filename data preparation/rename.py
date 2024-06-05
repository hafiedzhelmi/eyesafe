import os

# Function to ensure consistent labeling for images based on subfolder and index number
def ensure_consistent_labeling(folder_path):
    for root, dirs, files in os.walk(folder_path):
        # Get the label from the subfolder name
        label = os.path.basename(root)
        index = 0
        for file in files:
            # Construct the new filename using the subfolder name and index number
            new_filename = f"{label}_{index:04}.png"  # Format: subfolder_indexnumber.png
            old_filepath = os.path.join(root, file)
            new_filepath = os.path.join(root, new_filename)
            # Rename the file if it's not already named correctly
            if file != new_filename:
                os.rename(old_filepath, new_filepath)
                print(f"Renamed {file} to {new_filename}")
            index += 1

# Main function to traverse through main folder and ensure consistent labeling
def main():
    main_folder = r"D:\cat"
    ensure_consistent_labeling(main_folder)

if __name__ == "__main__":
    main()
