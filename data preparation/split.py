import os
import random
import shutil

# Function to split dataset into training, validation, and test sets
def split_dataset(input_folder, output_folder, train_size=0.7, val_size=0.15, test_size=0.15, random_state=42):
    # Create output folders if they don't exist
    train_folder = os.path.join(output_folder, "train")
    val_folder = os.path.join(output_folder, "val")
    test_folder = os.path.join(output_folder, "test")
    for folder in [train_folder, val_folder, test_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Iterate through each subfolder in the input folder
    for class_name in os.listdir(input_folder):
        class_folder = os.path.join(input_folder, class_name)
        train_class_folder = os.path.join(train_folder, class_name)
        val_class_folder = os.path.join(val_folder, class_name)
        test_class_folder = os.path.join(test_folder, class_name)

        # Create class folders in output folders if they don't exist
        for folder in [train_class_folder, val_class_folder, test_class_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)

        # Get list of images in class folder
        images = os.listdir(class_folder)
        
        # Shuffle the list of images
        random.seed(random_state)
        random.shuffle(images)
        
        # Calculate the number of images for each split
        num_images = len(images)
        num_train = int(train_size * num_images)
        num_val = int(val_size * num_images)
        num_test = num_images - num_train - num_val
        
        # Assign images to each split
        train_images = images[:num_train]
        val_images = images[num_train:num_train+num_val]
        test_images = images[num_train+num_val:]
        
        # Copy images to respective folders
        for img_name in train_images:
            shutil.copy(os.path.join(class_folder, img_name), os.path.join(train_class_folder, img_name))
        for img_name in val_images:
            shutil.copy(os.path.join(class_folder, img_name), os.path.join(val_class_folder, img_name))
        for img_name in test_images:
            shutil.copy(os.path.join(class_folder, img_name), os.path.join(test_class_folder, img_name))

# Main function
def main():
    input_folder = r"D:\\cat"  # Path to input folder containing augmented images
    output_folder = r"D:\dataset split7"  # Path to output folder to save split datasets

    # Split dataset into training, validation, and test sets
    split_dataset(input_folder, output_folder)

if __name__ == "__main__":
    main()
