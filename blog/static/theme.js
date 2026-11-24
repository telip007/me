(() => {
  const root = document.documentElement;
  const scheme = document.querySelector('meta[name="color-scheme"]');
  const chrome = [...document.querySelectorAll('meta[name="theme-color"]')];
  const button = document.querySelector("[data-theme-toggle]");
  const storageKey = "goeksu-color-scheme";
  const system = window.matchMedia("(prefers-color-scheme: dark)");

  function apply(theme) {
    if (theme) root.dataset.theme = theme;
    else delete root.dataset.theme;
    scheme.content = theme || "light dark";
    chrome[0].content = theme === "dark" ? "#171717" : "#ffffff";
    chrome[1].content = theme === "light" ? "#ffffff" : "#171717";

    const active = theme || (system.matches ? "dark" : "light");
    const target = active === "dark" ? "light" : "dark";
    button.textContent = target === "dark" ? "Dark mode" : "Light mode";
    button.setAttribute("aria-label", `Switch to ${target} mode`);
  }

  function sync() {
    try {
      const saved = localStorage.getItem(storageKey);
      apply(saved === "light" || saved === "dark" ? saved : undefined);
    } catch {
      apply(root.dataset.theme);
    }
  }

  apply(root.dataset.theme);
  button.hidden = false;
  button.addEventListener("click", () => {
    const active = root.dataset.theme || (system.matches ? "dark" : "light");
    const next = active === "dark" ? "light" : "dark";
    apply(next);
    try {
      localStorage.setItem(storageKey, next);
    } catch {}
  });
  system.addEventListener("change", () => apply(root.dataset.theme));
  window.addEventListener("storage", (event) => {
    if (event.key === storageKey || event.key === null) sync();
  });
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) sync();
  });
})();
