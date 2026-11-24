(() => {
  const isNative = CSS.supports("view-timeline-name: --article-reading") &&
    CSS.supports("view-timeline-inset: 0px") && CSS.supports("timeline-scope: --article-reading") &&
    CSS.supports("animation-timeline: --article-reading") &&
    CSS.supports("animation-range: contain 0% entry-crossing 100%");
  if (isNative) return;

  const progress = document.querySelector(".reading-progress");
  const article = document.querySelector(".article");
  const root = document.documentElement;
  let pending = false;

  function update() {
    pending = false;
    const { top, bottom } = article.getBoundingClientRect();
    const insets = getComputedStyle(progress);
    const safeTop = parseFloat(insets.borderTopWidth) || 0;
    const safeBottom = parseFloat(insets.paddingBottom) || 0;
    const start = Math.max(0, top + scrollY - safeTop);
    const end = bottom + scrollY - root.clientHeight + safeBottom;
    const fraction = end > start ? Math.max(0, Math.min(1, (scrollY - start) / (end - start))) : Number(bottom <= root.clientHeight - safeBottom);
    progress.style.setProperty("--reading-progress", fraction);
  }

  function schedule() {
    if (!pending) {
      pending = true;
      requestAnimationFrame(update);
    }
  }

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  window.visualViewport?.addEventListener("resize", schedule);
  window.addEventListener("pageshow", schedule);
  if ("ResizeObserver" in window) new ResizeObserver(schedule).observe(article);
  schedule();
})();
