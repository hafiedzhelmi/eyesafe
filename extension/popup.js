document.addEventListener("DOMContentLoaded", function () {
  const sensitivitySelect = document.getElementById("sensitivity");
  const filterToggle = document.getElementById("filter-toggle");

  // Load stored settings and apply them to the popup elements
  chrome.storage.local.get(["sensitivity", "filterEnabled"], function (data) {
    if (data.sensitivity) {
      sensitivitySelect.value = data.sensitivity;
    }
    filterToggle.checked = data.filterEnabled !== false;
  });

  // Save settings when the "Save Settings" button is clicked
  document.getElementById("save").addEventListener("click", function () {
    const sensitivity = sensitivitySelect.value;
    const filterEnabled = filterToggle.checked;

    chrome.storage.local.set(
      { sensitivity: sensitivity, filterEnabled: filterEnabled },
      function () {
        console.log("Settings saved:", {
          sensitivity: sensitivity,
          filterEnabled: filterEnabled,
        });
      }
    );
  });

  // Open the guide page within the popup
  document.getElementById("open-guide").addEventListener("click", function () {
    document.getElementById("settings-container").classList.add("hidden");
    document.getElementById("guide-container").classList.remove("hidden");
  });

  // Go back to the settings page
  document.getElementById("go-back").addEventListener("click", function () {
    document.getElementById("guide-container").classList.add("hidden");
    document.getElementById("settings-container").classList.remove("hidden");
  });
});
