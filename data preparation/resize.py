import os
from PIL import Image

# Function to convert images to PNG and resize them
def convert_and_resize_image(image_path):
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if not already in RGB mode
            img = img.convert("RGB")
            # Resize the image to 255x255
            img_resized = img.resize((255, 255))
            # Get the file name without extension
            file_name = os.path.splitext(image_path)[0]
            # Save the image as PNG format
            img_resized.save(file_name + '.png', format='PNG')
            print(f"Converted and resized: {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

# Function to process all images in a folder recursively
def process_images_in_folder(folder_path):
    # Iterate through all files and folders within the current folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file is an image
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.heic')):
                image_path = os.path.join(root, file)
                # Convert and resize the image
                convert_and_resize_image(image_path)

# Main function to start the processing
def main():
    main_folder_path = r'D:\cat'
    process_images_in_folder(main_folder_path)

if __name__ == "__main__":
    main()
