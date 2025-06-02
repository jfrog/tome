// termynal-init.js

document.addEventListener("DOMContentLoaded", () => {
  // 1) Convert any <div class="termy">…<pre><code>…</code></pre> into a <div data-termynal>
  document.querySelectorAll(".termy:not([data-termynal])").forEach(container => {
    const codeNode = container.querySelector("pre code");
    if (!codeNode) return;
    const lines = codeNode.textContent.split("\n");
    const inner = lines.map(line => {
      const t = line.trim();
      if (t.startsWith("$")) {
        return `<span data-ty="input">${t.slice(1).trim()}</span>`;
      }
      return `<span data-ty>${line}</span>`;
    }).join("");
    container.innerHTML = `<div data-termynal>${inner}</div>`;
  });

  // 2) Mount Termynal on every [data-termynal] block
  document.querySelectorAll("[data-termynal]").forEach(mount);

  function mount(div) {
    new Termynal(div, { lineDelay: 400, startDelay: 600, typeDelay: 35 });
    if (div.parentNode.classList.contains("termy-wrapper")) return;
    const wrapper = document.createElement("div");
    wrapper.className = "termy-wrapper";
    div.parentNode.insertBefore(wrapper, div);
    wrapper.appendChild(div);
  }
});
