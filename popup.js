document.getElementById("capture").addEventListener("click", async () => {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(tab.id, { type: "GET_SOLUTION" }, (response) => {
    if (response && response.code) {
      document.getElementById("output").innerText = response.code;
    } else {
      document.getElementById("output").innerText = "No code found.";
    }
  });
});

