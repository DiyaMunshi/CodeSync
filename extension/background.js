const LANGUAGE_MAP = {
  "python": "python",
  "python3": "python3",
  "c": "c",
  "c++": "cpp",
  "cpp": "cpp",
  "java": "java",
  "javascript": "javascript",
  "typescript": "typescript",
  "c#": "csharp",
  "csharp": "csharp",
  "go": "go",
  "rust": "rust",
  "kotlin": "kotlin",
  "swift": "swift",
  "ruby": "ruby",
  "php": "php",
  "sql": "sql"
};

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action !== "saveSolution" || !sender.tab?.id) {
    return;
  }

  (async () => {
    const results = await chrome.scripting.executeScript({
      target: { tabId: sender.tab.id },
      world: "MAIN",
      func: () => {
        let code = null;

        // Attempt to read the Monaco editor.
        if (window.monaco?.editor?.getModels) {
          const models = window.monaco.editor.getModels();
          if (models.length) {
            code = models[0].getValue();
          }
        }

        // Attempt to detect the language from visible page elements.
        const languageElements = [
          ...document.querySelectorAll(
            '[data-mode-id], [class*="language"], button, [role="combobox"]'
          )
        ];

        const candidates = languageElements
          .map(element => {
            const text = [
              element.getAttribute("data-mode-id"),
              element.getAttribute("aria-label"),
              element.innerText,
              element.textContent
            ].filter(Boolean).join(" ").trim();

            return text.toLowerCase();
          });

        const knownLanguages = [
          "python3", "python", "javascript", "typescript",
          "c++", "cpp", "c#", "csharp", "java", "kotlin",
          "swift", "rust", "ruby", "php", "golang", "go", "sql", "c"
        ];

        let detectedLanguage = null;

        // Prefer explicit editor language identifiers.
        if (window.monaco?.editor?.getModels) {
          const models = window.monaco.editor.getModels();
          for (const model of models) {
            const id = model.getLanguageId?.()?.toLowerCase();
            if (id && knownLanguages.includes(id)) {
              detectedLanguage = id;
              break;
            }
          }
        }

        // Fall back to visible language selectors.
        if (!detectedLanguage) {
          for (const candidate of candidates) {
            for (const language of knownLanguages) {
              if (
                candidate === language ||
                candidate.includes(` ${language} `) ||
                candidate.startsWith(`${language} `)
              ) {
                detectedLanguage = language;
                break;
              }
            }
            if (detectedLanguage) break;
          }
        }

        return { code, detectedLanguage };
      }
    });

    const result = results?.[0]?.result;
    const code = result?.code;
    const detectedLanguage = result?.detectedLanguage;

    if (!code) {
      throw new Error(
        "Could not read the editor source. The LeetCode editor may need a different capture method."
      );
    }

    if (!detectedLanguage || !LANGUAGE_MAP[detectedLanguage]) {
      throw new Error(
        "Could not reliably detect the programming language. Please check the language selected on LeetCode."
      );
    }

    const response = await fetch("http://127.0.0.1:5050/solution", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: message.title,
       code,
       language: LANGUAGE_MAP[detectedLanguage],
        url: message.url,
        problemNumber: message.problemNumber || "",
        problemSlug: message.problemSlug || "",
        status: "accepted"
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "CodeSync could not save the solution.");
    }

    sendResponse({
      success: true,
      result: data,
      language: LANGUAGE_MAP[detectedLanguage]
    });
  })().catch(error => {
    sendResponse({
      success: false,
      error: error.message
    });
  });

  return true;
});