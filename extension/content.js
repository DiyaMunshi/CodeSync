const button = document.createElement("button");

button.textContent = "Save to CodeSync";
button.id = "codesync-save-button";

Object.assign(button.style, {
  position: "fixed",
  bottom: "24px",
  right: "24px",
  zIndex: "999999",
  padding: "12px 18px",
  background: "#16a34a",
  color: "white",
  border: "none",
  borderRadius: "8px",
  fontSize: "14px",
  fontWeight: "600",
  cursor: "pointer",
  boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
});

// Extract the problem slug from the current LeetCode URL.
function getProblemSlug() {
  const match = location.pathname.match(/\/problems\/([^/]+)/);
  return match ? match[1].toLowerCase() : "";
}

// Extract the problem title and number from the page.

function getProblemDetails() {
  const selectors = [
    '[data-cy="question-title"]',
    '[data-testid="question-title"]',
    'div[class*="text-title-large"]'
  ];

  let visibleTitle = "";

  for (const selector of selectors) {
    const element = document.querySelector(selector);

    if (element?.textContent?.trim()) {
      visibleTitle = element.textContent.trim();
      break;
    }
  }

  // Extract a number when the title includes one, e.g. "1. Two Sum".
  const match = visibleTitle.match(/^(\d+)\.\s*(.+)$/);

  const title = match
    ? match[2].trim()
    : document.title.replace(/\s*-\s*LeetCode.*$/i, "").trim();

  return {
    problemNumber: match ? match[1] : "",
    title
  };
}


button.addEventListener("click", async () => {
  const accepted = confirm(
    "Have you received Accepted on LeetCode?"
  );

  if (!accepted) return;

  button.textContent = "Saving...";
  button.style.background = "#2563eb";
  button.disabled = true;

  try {
    const details = getProblemDetails();

    const response = await chrome.runtime.sendMessage({
      action: "saveSolution",
      url: location.href,
      title: details.title,
      problemNumber: details.problemNumber,
      problemSlug: getProblemSlug()
    });

    if (!response?.success) {
      throw new Error(
        response?.error || "Could not save solution"
      );
    }

    button.textContent = response.result?.filename
      ? `Saved: ${response.result.filename}`
      : "Saved locally!";

    button.style.background = "#15803d";
  } catch (error) {
    button.textContent = "Save failed";
    button.style.background = "#dc2626";
    alert(error.message);
  } finally {
    button.disabled = false;
  }
});

document.body.appendChild(button);