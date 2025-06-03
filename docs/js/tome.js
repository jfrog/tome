// style console blocks
document.addEventListener("DOMContentLoaded", () => {
  function escapeHTML(str) {
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;");
  }

  document.querySelectorAll("div.language-console.highlight pre").forEach(preElem => {
    const copyButton = preElem.querySelector("button.md-clipboard");
    if (copyButton) {
      // Remove the default clipboard target, as we will set the text manually
      delete copyButton.dataset.clipboardTarget;
      preElem.dataset.clipboardText = "";
    }
    const copyCommands = []
    const codeElem = preElem.querySelector("code")
    const lines = codeElem.textContent.split("\n");
    const html = lines.map(line => {
      if (line.startsWith("# ")) {
        return `<span class="console-line comment-line">${escapeHTML(line)}</span>`;
      } else if (line.startsWith("$ ")) {
        const prefix = escapeHTML(line.charAt(0));
        const rest   = escapeHTML(line.slice(1));
        copyCommands.push(rest.trim());
        return `<span class="console-line command-line"><span class="prompt">${prefix}</span><span class="cmd-text" id="#${preElem.id}__cmd">${rest}</span></span>`;
      } else if (line === "") {
        return `<span class="console-line empty-line"></span>`;
      } else {
        return `<span class="console-line output-line">${escapeHTML(line)}</span>`;
      }
    }).join("");
    codeElem.innerHTML = html;
    preElem.dataset.clipboardText = copyCommands.join("\n");
  });
});
