try {
  const theme = localStorage.getItem("goeksu-color-scheme");
  if (theme === "light" || theme === "dark") {
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="color-scheme"]').content = theme;
    const chrome = theme === "light" ? "#ffffff" : "#171717";
    for (const meta of document.querySelectorAll('meta[name="theme-color"]')) meta.content = chrome;
  }
} catch {}
