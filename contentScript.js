let model;
let sensitivityLevel = 5; // Default sensitivity level, least restrictive
let filterEnabled = true;

async function loadModel() {
  try {
    model = await tf.loadLayersModel(chrome.runtime.getURL("model/model.json"));
    console.log("Model loaded successfully");
    if (model) {
      processImages(); // Ensure model is loaded before processing images
    }
  } catch (error) {
    console.error("Failed to load model:", error);
  }
}

async function fetchSettings() {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get(["sensitivity", "filterEnabled"], function (data) {
      if (data.sensitivity) {
        sensitivityLevel = parseInt(data.sensitivity);
        console.log("Sensitivity level set to:", sensitivityLevel);
      }
      filterEnabled = data.filterEnabled !== false;
      console.log("Filter enabled:", filterEnabled);
      resolve();
    });
  });
}

// Debounce function to limit processImages invocations
function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

const debounceProcessImages = debounce(async () => {
  await fetchSettings();
  if (!filterEnabled) {
    console.log("Content filter is disabled.");
    return;
  }

  const images = document.getElementsByTagName("img");
  console.log(`Found ${images.length} images on the page.`);
  Array.from(images).forEach((img) => {
    if (!img.classList.contains("processed")) {
      markAndProcessImage(img);
    }
  });
}, 300);

function markAndProcessImage(img) {
  img.classList.add("processed");
  img.crossOrigin = "anonymous";
  if (img.complete && img.naturalHeight !== 0) {
    console.log(
      "Processing an image with valid dimensions and complete loading.",
      img.src
    );
    analyzeAndBlur(img);
  } else {
    img.onload = () => {
      console.log("Onload triggered for image.", img.src);
      analyzeAndBlur(img);
    };
  }
}

async function analyzeAndBlur(img) {
  if (img.width > 0 && img.height > 0 && model) {
    const tensor = tf.browser.fromPixels(img);
    const resized = tensor
      .resizeBilinear([224, 224])
      .div(tf.scalar(255.0))
      .expandDims(0);
    let predictions;
    try {
      predictions = await model.predict(resized);
      const results = predictions.arraySync(); // Convert tensor data to regular array
      const highestPredictionIndex = predictions.argMax(1).dataSync()[0];
      console.log("Predictions received for image:", img.src, results);

      const shouldBlur = determineIfSensitive(highestPredictionIndex);
      console.log("The level of this image is:", highestPredictionIndex + 1);
      console.log("Should the image be blurred? ", shouldBlur);
      if (shouldBlur) {
        img.style.filter = "blur(8px)";
        console.log("Applied blur to image:", img.src);
      }
    } catch (error) {
      console.error("Failed to process image:", img.src, error);
    } finally {
      // Dispose of all tensors
      tensor.dispose();
      resized.dispose();
      predictions && predictions.dispose();
    }
  } else {
    console.log(
      "Skipping image with invalid dimensions or model not loaded:",
      img.src
    );
  }
}

function determineIfSensitive(predictedIndex) {
  return predictedIndex + 1 <= sensitivityLevel;
}

// Load the model after defining necessary functions
loadModel();

// Mutation observer to handle dynamic content loading
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (
      (mutation.type === "childList" && mutation.addedNodes.length) ||
      mutation.type === "attributes"
    ) {
      debounceProcessImages();
    }
  });
});

const config = {
  childList: true,
  subtree: true,
  attributes: true,
  attributeFilter: ["style", "src"],
};
observer.observe(document.body, config);

// Listen for changes in the settings to update sensitivity and filtering status
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (changes.sensitivity) {
    sensitivityLevel = parseInt(changes.sensitivity.newValue);
    console.log("Updated sensitivity level:", sensitivityLevel);
  }

  if (changes.filterEnabled) {
    filterEnabled = changes.filterEnabled.newValue !== false;
    console.log("Updated filter enabled status:", filterEnabled);
  }

  // Re-process images if filtering is enabled
  debounceProcessImages();
});
