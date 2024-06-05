# Sexual Content Filtering Browser Extension Utilizing Web Scraping and Convolutional Neural Network

This project is implemented to fulfill the requirements of my final year project development with the title "Sexual Content Filtering Browser Extension Utilizing Web Scraping and Convolutional Neural Network."

## Project Structure

The project consists of three main parts: data preparation, model training, and app development.

### Data Preparation

The `data preparation` folder contains the scraping code used on two platforms: Google and Reddit. The proprietary APIs of these platforms are utilized to collect images. Reddit provides images that are sexual in nature, while Google provides less explicit images. The folder also contains code for renaming, resizing, and splitting the images to complete the dataset.

### Model Training

The `model training` folder contains the code to train a modified MobileNetv2 model, which achieved good accuracy results. The model is designed to categorize images into 10 categories:

```python
class_names = [
    'bottom',  # level 2
    'men_full_dressed',  # level 5
    'men_half_naked',  # level 4
    'men_penis',  # level 1
    'men_undies',  # level 3
    'women_breasts',  # level 2
    'women_full_dressed',  # level 5
    'women_short_dressed',  # level 4
    'women_undies',  # level 3
    'women_vagina'  # level 1
]
```

### Extension Development

The `extension` folder contains the browser extension app and the exported model. The extension works effectively on various images, filtering them based on user-defined sensitivity levels. Users can customize the sensitivity level to filter out different degrees of explicit content, ranging from explicit nudity to minimal nudity.

#### Features of the Extension

- **User-Friendly Interface:** The extension provides an intuitive interface for users to set their preferred sensitivity level.
- **Real-Time Filtering:** The extension uses the trained MobileNetv2 model to analyze and blur images in real-time based on the sensitivity settings.
- **Customizable Settings:** Users can enable or disable the filter and adjust the sensitivity level through the extension's settings.
- **Detailed Guide:** A guide is included to help users understand how to use the filter and the criteria for each sensitivity level.

#### How to Use

1. **Set Sensitivity Level:** Select the desired sensitivity level from the dropdown menu.
2. **Enable Filter:** Toggle the switch to enable or disable the content filter.
3. **Save Settings:** Click the "Save Settings" button to apply the changes.
4. **View Guide:** Click on the "How to use this filter" link to view a detailed guide on the filter criteria.

This project demonstrates the integration of web scraping, machine learning, and browser extension development to provide a practical solution for filtering explicit content.
