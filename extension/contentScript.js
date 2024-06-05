let model;
let sensitivityLevel = 5; // Default sensitivity level, least restrictive
let filterEnabled = true;

// Define the category levels and class names
const categoryLevels = {
  bottom: 2,
  men_full_dressed: 5,
  men_half_naked: 4,
  men_penis: 1,
  men_undies: 3,
  women_breasts: 2,
  women_full_dressed: 5,
  women_short_dressed: 4,
  women_undies: 3,
  women_vagina: 1,
};

const class_names = [
  "bottom",
  "men_full_dressed",
  "men_half_naked",
  "men_penis",
  "men_undies",
  "women_breasts",
  "women_full_dressed",
  "women_short_dressed",
  "women_undies",
  "women_vagina",
];

async function loadModel() {
  try {
    model = await tf.loadLayersModel(
      chrome.runtime.getURL("model2/model.json")
    );
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

// Throttle function to limit processImages invocations
function throttle(fn, wait) {
  let inThrottle, lastFn, lastTime;
  return function () {
    const context = this;
    const args = arguments;
    if (!inThrottle) {
      fn.apply(context, args);
      lastTime = Date.now();
      inThrottle = true;
    } else {
      clearTimeout(lastFn);
      lastFn = setTimeout(function () {
        if (Date.now() - lastTime >= wait) {
          fn.apply(context, args);
          lastTime = Date.now();
        }
      }, Math.max(wait - (Date.now() - lastTime), 0));
    }
  };
}

const throttleProcessImages = throttle(async () => {
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
}, 100);

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
      const results = predictions.arraySync()[0]; // Convert tensor data to regular array
      const highestPredictionIndex = predictions.argMax(1).dataSync()[0];
      const highestConfidence = results[highestPredictionIndex];
      console.log("Predictions received for image:", img.src, results);

      const shouldBlur = determineIfSensitive(
        highestPredictionIndex,
        highestConfidence
      );
      console.log(
        "The level of this image is:",
        categoryLevels[class_names[highestPredictionIndex]]
      );
      console.log("Should the image be blurred? ", shouldBlur);
      if (shouldBlur) {
        img.style.filter = "blur(20px)";
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

function determineIfSensitive(predictedIndex, highestConfidence) {
  const category = class_names[predictedIndex];
  const level = categoryLevels[category];
  return highestConfidence >= 0.3 && level <= sensitivityLevel;
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
      throttleProcessImages();
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
  throttleProcessImages();
});
