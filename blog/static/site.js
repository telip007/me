/* Native navigation stays native. This script only adds request feedback and reading helpers. */
(() => {
  'use strict';
  const form = document.querySelector('.search-form');
  const status = document.querySelector('#search-status');
  const error = document.querySelector('#search-error');
  if (form) {
    document.body.addEventListener('htmx:beforeRequest', event => {
      if (!form.contains(event.detail.elt)) return;
      document.querySelector('#posts')?.setAttribute('aria-busy', 'true');
      if (error) error.hidden = true;
    });
    document.body.addEventListener('htmx:afterSwap', event => {
      if (event.detail.target.id !== 'posts') return;
      const results = document.querySelector('#posts');
      results?.removeAttribute('aria-busy');
      if (status) status.textContent = results?.dataset.resultLabel || '';
    });
    document.body.addEventListener('htmx:afterRequest', event => {
      if (!form.contains(event.detail.elt)) return;
      document.querySelector('#posts')?.removeAttribute('aria-busy');
      if (!event.detail.successful && !event.detail.xhr?.status) {
        if (error) error.hidden = false;
      }
    });
    for (const name of ['htmx:responseError', 'htmx:sendError', 'htmx:timeout']) {
      document.body.addEventListener(name, event => {
        if (!form.contains(event.detail.elt)) return;
        document.querySelector('#posts')?.removeAttribute('aria-busy');
        if (error) error.hidden = false;
      });
    }
  }
  // Make overflowing code and tables reachable with a keyboard only when they overflow.
  for (const table of document.querySelectorAll('.prose table')) {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll';
    table.before(wrapper);
    wrapper.append(table);
  }
  for (const element of document.querySelectorAll('.prose pre, .table-scroll')) {
    const update = () => {
      if (element.scrollWidth > element.clientWidth + 1) {
        element.tabIndex = 0;
        element.setAttribute('role', 'region');
        element.setAttribute('aria-label', document.documentElement.lang === 'de' ? 'Horizontal scrollbarer Code oder Tabelle' : 'Horizontally scrollable code or table');
      } else {
        element.removeAttribute('tabindex');
        element.removeAttribute('role');
        element.removeAttribute('aria-label');
      }
    };
    update();
    if ('ResizeObserver' in window) new ResizeObserver(update).observe(element);
  }
})();
