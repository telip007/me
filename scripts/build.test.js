import test from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { build } from './build.js';

async function fixture(t, basePath = '') {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'blog-build-'));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.mkdir(path.join(root, 'src/posts'), { recursive: true });
  const files = {
    'config.json': JSON.stringify({ siteUrl: 'https://example.test', basePath, siteTitle: 'Example', siteSubtitle: 'Deutsch', siteDescription: 'Beschreibung', author: 'Example', locales: { en: { siteSubtitle: 'English', siteDescription: 'Description' } } }),
    'about.md': '---\ntitle: Über diesen Blog\nslug: ueber-mich\n---\n# Deutsch',
    'about.en.md': '---\ntitle: About this blog\nslug: about\n---\n# English',
    'datenschutz.md': '# Datenschutz\n\nBestehender Rechtstext.',
    'styles.css': 'body { color: black; }',
    'favicon.svg': '<svg xmlns="http://www.w3.org/2000/svg"/>',
  };
  for (const [name, body] of Object.entries(files)) await fs.writeFile(path.join(root, 'src', name), body);
  const post = (name, meta = '', body = 'A useful article.') => fs.writeFile(path.join(root, 'src/posts', name), `---\ntitle: ${name}\ndate: '2026-01-01'\ntags: [LLM]\n${meta}\n---\n${body}`);
  const read = route => fs.readFile(path.join(root, 'dist', route), 'utf8');
  return { root, post, read };
}

test('preserves German URLs and builds paired localized routes, feeds and metadata', async t => {
  const { root, post, read } = await fixture(t, '/me');
  await post('de.md', 'slug: modelle\ntranslationKey: models');
  await post('en.md', 'lang: en\nslug: models\ntranslationKey: models');
  await build(root);
  const german = await read('texte/modelle/index.html');
  const english = await read('en/articles/models/index.html');
  assert.match(german, /<html lang="de"/);
  assert.match(english, /<html lang="en"/);
  assert.match(english, /href="\/me\/en\/about\/"/);
  assert.match(english, /href="\/me\/en\/rss.xml"/);
  assert.match(english, /hreflang="de" href="https:\/\/example.test\/me\/texte\/modelle\/"/);
  assert.match(german, /hreflang="en" href="https:\/\/example.test\/me\/en\/articles\/models\/"/);
  assert.match(english, /rel="canonical" href="https:\/\/example.test\/me\/en\/articles\/models\/"/);
  assert.match(english, /"inLanguage": "en"/);
  assert.match(english, /min read/);
  assert.doesNotMatch(english, /Min\. Lesezeit|Zum Inhalt|Über mich/);
  assert.match(await read('en/tags/llm/index.html'), /Topic: LLM/);
  assert.match(await read('en/rss.xml'), /<language>en<\/language>/);
  assert.doesNotMatch(await read('en/rss.xml'), /\/texte\/modelle\//);
  assert.doesNotMatch(await read('rss.xml'), /\/en\/articles\//);
  assert.match(await read('sitemap.xml'), /xhtml:link rel="alternate" hreflang="en"/);
  assert.match(await read('about/index.html'), /url=\/me\/ueber-mich\//);
});

test('drafts never leak through pages, feed, sitemap or translation links', async t => {
  const { root, post, read } = await fixture(t);
  await post('de.md', 'slug: public\ntranslationKey: pair');
  await post('en.md', 'lang: en\nslug: hidden\ntranslationKey: pair\ndraft: true', 'PRIVATE_DRAFT_MARKER');
  await fs.mkdir(path.join(root, 'drafts'));
  await fs.writeFile(path.join(root, 'drafts/unpublished.md'), 'PRIVATE_DRAFT_MARKER');
  await build(root);
  assert.match(await read('en/index.html'), /No articles published yet/);
  await assert.rejects(read('en/articles/hidden/index.html'), /ENOENT/);
  for (const file of ['index.html', 'en/index.html', 'rss.xml', 'en/rss.xml', 'sitemap.xml', 'texte/public/index.html']) {
    const html = await read(file);
    assert.doesNotMatch(html, /\/hidden\/|PRIVATE_DRAFT_MARKER/);
  }
  const unpaired = await read('texte/public/index.html');
  assert.match(unpaired, /href="\/en\/" hreflang="en"/);
  assert.doesNotMatch(unpaired, /rel="alternate" hreflang="en"/);
});

test('rejects unsafe slugs and duplicate language pairs before replacing output', async t => {
  const { root, post, read } = await fixture(t);
  await post('first.md', 'slug: good\ntranslationKey: same');
  await build(root);
  const before = await read('index.html');
  await post('second.md', 'slug: another\ntranslationKey: same');
  await assert.rejects(build(root), /Duplicate translationKey/);
  assert.equal(await read('index.html'), before);
  await post('second.md', 'slug: ../../escape');
  await assert.rejects(build(root), /Invalid post slug/);
  assert.equal(await read('index.html'), before);
});

test('escapes feed text and script-sensitive JSON-LD without corrupting XML', async t => {
  const { root, post, read } = await fixture(t);
  await post('special.md', 'slug: special\nexcerpt: "A & B ]]> </script>"');
  await build(root);
  assert.match(await read('rss.xml'), /A &amp; B \]\]&gt; &lt;\/script&gt;/);
  assert.match(await read('texte/special/index.html'), /\\u003c\/script>/);
});

test('rejects executable front matter without running it and accepts plain JSON', async t => {
  const { root, read } = await fixture(t);
  const file = path.join(root, 'src/posts/unsafe.md');
  await fs.writeFile(file, '---javascript\n({title: (globalThis.__blogExecuted = true), date: "2026-01-01"})\n---\nUnsafe');
  await assert.rejects(build(root), /Only YAML or JSON front matter/);
  assert.equal(globalThis.__blogExecuted, undefined);
  await fs.writeFile(file, '---json\n{"title":"Safe JSON","date":"2026-01-01","slug":"safe"}\n---\nSafe');
  await build(root);
  assert.match(await read('texte/safe/index.html'), /Safe JSON/);
});

test('keeps the current privacy notice and labels the German fallback in English', async t => {
  const { root, read } = await fixture(t);
  await build(root);
  assert.match(await read('datenschutz/index.html'), /Bestehender Rechtstext/);
  assert.match(await read('sitemap.xml'), /https:\/\/example.test\/datenschutz\//);
  assert.match(await read('en/index.html'), /href="\/datenschutz\/" lang="de">Privacy \(German\)/);
  assert.match(await read('en/index.html'), /href="https:\/\/github.com\/telip007" rel="me"/);
});

test('invalid draft flags, unsupported languages and duplicate URLs fail closed', async t => {
  const { root, post } = await fixture(t);
  await post('one.md', 'slug: first\ndraft: "yes"');
  await assert.rejects(build(root), /draft must be true or false/);
  await post('one.md', 'slug: first\nlang: fr');
  await assert.rejects(build(root), /Unsupported lang/);
  await post('one.md', 'slug: same');
  await post('two.md', 'slug: same');
  await assert.rejects(build(root), /Duplicate output route/);
});

test('escapes quotes in image and social metadata instead of creating attributes', async t => {
  const { root, post, read } = await fixture(t);
  const image = 'https://example.test/photo.jpg" onload="alert(1)';
  const configPath = path.join(root, 'src/config.json');
  const config = JSON.parse(await fs.readFile(configPath, 'utf8'));
  config.twitterHandle = '@example" onmouseover="alert(2)';
  await fs.writeFile(configPath, JSON.stringify(config));
  await post('quoted.md', `slug: quoted\nimage: ${JSON.stringify(image)}`);
  await build(root);
  const page = await read('texte/quoted/index.html');
  assert.match(page, /property="og:image" content="https:\/\/example.test\/photo.jpg&quot; onload=&quot;alert\(1\)"/);
  assert.match(page, /name="twitter:creator" content="@example&quot; onmouseover=&quot;alert\(2\)"/);
  assert.doesNotMatch(page, /content="[^"]*" on(?:load|mouseover)=/);
});
