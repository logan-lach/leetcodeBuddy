// Check for stored accepted submission on popup load
chrome.storage.local.get([STORAGE_KEYS.LAST_ACCEPTED_SUBMISSION], (result) => {
  if (result[STORAGE_KEYS.LAST_ACCEPTED_SUBMISSION]) {
    const { code, metadata } = result[STORAGE_KEYS.LAST_ACCEPTED_SUBMISSION];

    // Show congratulations message
    document.getElementById("congratsMessage").style.display = "block";

    // Display metadata if available
    if (metadata) {
      let metadataHtml = "<div>";
      if (metadata.title) metadataHtml += `<p><strong>Problem:</strong> ${metadata.title}</p>`;
      if (metadata.problemSlug) metadataHtml += `<p><strong>Slug:</strong> ${metadata.problemSlug}</p>`;
      if (metadata.difficulty) metadataHtml += `<p><strong>Difficulty:</strong> ${metadata.difficulty}</p>`;
      metadataHtml += "</div>";
      document.getElementById("metadata").innerHTML = metadataHtml;
    }

    // Display the code
    document.getElementById("output").innerText = code;
  }
});

// Manual capture button
document.getElementById("capture").addEventListener("click", async () => {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(tab.id, { type: MESSAGE_TYPES.GET_SOLUTION }, (response) => {
    if (response && response.code) {
      document.getElementById("output").innerText = response.code;
    } else {
      document.getElementById("output").innerText = "No code found.";
    }
  });
});

