import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

// Exercise the production listeners without starting a browser or adding a DOM dependency.
function searchUI() {
  const listeners = new Map();
  const input = {};
  const form = { contains: element => element === input };
  const results = {
    dataset: { resultLabel: '1 article' },
    busy: false,
    setAttribute() { this.busy = true; },
    removeAttribute() { this.busy = false; },
  };
  const status = { textContent: '' };
  const error = { hidden: true };
  const elements = { '.search-form': form, '#search-status': status, '#search-error': error, '#posts': results };
  runInNewContext(readFileSync(new URL('../blog/static/site.js', import.meta.url), 'utf8'), {
    document: {
      querySelector: selector => elements[selector],
      querySelectorAll: () => [],
      body: { addEventListener(name, handler) { listeners.set(name, handler); } },
    },
  });
  return { results, status, error, emit(name, extra = {}) { listeners.get(name)?.({ detail: { elt: input, ...extra } }); } };
}

test('replacing an in-flight search does not announce a network failure', () => {
  const ui = searchUI();
  ui.emit('htmx:beforeRequest');
  ui.emit('htmx:afterRequest', { xhr: { status: 0 } });
  assert.equal(ui.error.hidden, true);
  ui.emit('htmx:beforeRequest');
  assert.equal(ui.results.busy, true);
});

for (const name of ['htmx:sendError', 'htmx:responseError', 'htmx:timeout']) {
  test(`${name} preserves results and offers recovery`, () => {
    const ui = searchUI();
    ui.emit('htmx:beforeRequest');
    ui.emit(name);
    assert.equal(ui.error.hidden, false);
    assert.equal(ui.results.busy, false);
    assert.equal(ui.results.dataset.resultLabel, '1 article');
    ui.emit('htmx:beforeRequest');
    assert.equal(ui.error.hidden, true);
    ui.emit('htmx:afterSwap', { target: { id: 'posts' } });
    assert.equal(ui.status.textContent, '1 article');
    assert.equal(ui.results.busy, false);
  });
}
