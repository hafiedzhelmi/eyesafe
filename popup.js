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

  document.getElementById("save").addEventListener("click", function () {
    const sensitivity = sensitivitySelect.value;
    const filterEnabled = filterToggle.checked;
    chrome.storage.local.set({ sensitivity, filterEnabled }, function () {
      console.log(
        "Settings updated - Sensitivity:",
        sensitivity,
        "Filter Enabled:",
        filterEnabled
      );
      alert("Settings updated");
    });
  });
});
