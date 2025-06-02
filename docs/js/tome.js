// style console blocks
document.addEventListener("DOMContentLoaded", () => {
  function escapeHTML(str) {
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;");
  }

  document.querySelectorAll("div.language-console.highlight pre code").forEach(codeElem => {
    const lines = codeElem.textContent.split("\n");
    const html = lines.map(line => {
      if (line.startsWith("# ")) {
        return `<span class="console-line comment-line">${escapeHTML(line)}</span>`;
      } else if (line.startsWith("$ ")) {
        const prefix = escapeHTML(line.charAt(0));
        const rest   = escapeHTML(line.slice(1));
        return `<span class="console-line command-line"><span class="prompt">${prefix}</span><span class="cmd-text">${rest}</span></span>`;
      } else if (line === "") {
        return `<span class="console-line empty-line"></span>`;
      } else {
        return `<span class="console-line output-line">${escapeHTML(line)}</span>`;
      }
    }).join("");
    codeElem.innerHTML = html;
  });
});
