document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("summarizeBtn");
  const statusDiv = document.getElementById("status");
  const summaryDiv = document.getElementById("summary");

  if (!btn || !statusDiv || !summaryDiv) {
    console.error("Popup elements not found. Check popup.html IDs.");
    return;
  }

  btn.addEventListener("click", async () => {
    statusDiv.textContent = "Checking YouTube video...";
    summaryDiv.textContent = "";

    try {
      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });

      if (!tab?.url || !tab.url.includes("youtube.com/watch")) {
        statusDiv.textContent = "Please open a YouTube video.";
        return;
      }

      const videoId = new URL(tab.url).searchParams.get("v");

      if (!videoId) {
        statusDiv.textContent = "Invalid YouTube URL.";
        return;
      }

      statusDiv.textContent = "Generating summary (this may take time)...";

      const response = await fetch(
        "https://ysummariser.onrender.com/api/summarize",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ videoId }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        statusDiv.textContent = data.error || "Failed to summarize.";
        return;
      }

      statusDiv.textContent = "Summary ready:";
      summaryDiv.textContent = data.summary;
    } catch (err) {
      console.error(err);
      statusDiv.textContent = "Error connecting to backend.";
    }
  });
});
