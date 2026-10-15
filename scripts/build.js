import fs from 'node:fs';
import { promises as fsp } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import matter from 'gray-matter';
import MarkdownIt from 'markdown-it';

function parseMatter(raw) {
  const source = raw.replace(/^\uFEFF/, '');
  const first = source.split(/\r?\n/, 1)[0];
  if (source.startsWith('---') && !['---', '---yaml', '---json'].includes(first)) {
    throw new Error('Only YAML or JSON front matter is allowed');
  }
  return matter(source);
}

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false,
});

function ensureAbs(base, rel) {
  const b = base.replace(/\/$/, '');
  return `${b}${rel.startsWith('/') ? rel : `/${rel}`}`;
}

function normalizeBasePath(value = '') {
  const trimmed = String(value).trim();
  if (!trimmed || trimmed === '/') return '';
  return `/${trimmed.replace(/^\/+|\/+$/g, '')}`;
}

function withBase(config, rel) {
  const pathName = rel.startsWith('/') ? rel : `/${rel}`;
  return `${config.assetsBase}${pathName}`;
}

function formatDate(value, language = 'de') {
  try {
    const date = new Date(value);
    return new Intl.DateTimeFormat(language === 'en' ? 'en-GB' : 'de-DE', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }).format(date);
  } catch {
    return language === 'en' ? 'Unknown date' : 'Unbekanntes Datum';
  }
}

function estimateReadTime(markdown) {
  const stripped = markdown
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/\[[^\]]+\]\([^\)]+\)/g, ' ')
    .replace(/[#>*_`~\[\]()]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  const words = stripped.split(' ').filter(Boolean).length;
  return Math.max(1, Math.round(words / 220));
}

function escapeHtml(text = '') {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildCanonical(url) {
  return `<link rel="canonical" href="${escapeHtml(url)}">`;
}

function renderMetaTags({ title, description, canonicalUrl, image, type = 'website', siteName, twitterHandle, publishedTime, modifiedTime }) {
  return `
    <meta property="og:site_name" content="${escapeHtml(siteName)}">
    <meta property="og:title" content="${escapeHtml(title)}">
    <meta property="og:description" content="${escapeHtml(description)}">
    <meta property="og:type" content="${escapeHtml(type)}">
    <meta property="og:url" content="${escapeHtml(canonicalUrl)}">
    ${publishedTime ? `<meta property="article:published_time" content="${escapeHtml(publishedTime)}">` : ''}
    ${modifiedTime ? `<meta property="article:modified_time" content="${escapeHtml(modifiedTime)}">` : ''}
    ${image ? `<meta property="og:image" content="${escapeHtml(image)}">` : ''}
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="${escapeHtml(title)}">
    <meta name="twitter:description" content="${escapeHtml(description)}">
    ${twitterHandle ? `<meta name="twitter:creator" content="${escapeHtml(twitterHandle)}">` : ''}
    ${twitterHandle ? `<meta name="twitter:site" content="${escapeHtml(twitterHandle)}">` : ''}
    ${image ? `<meta name="twitter:image" content="${escapeHtml(image)}">` : ''}
  `;
}

function renderJsonLdWebsite({ siteUrl, siteName, description, language }) {
  return `
    <script type="application/ld+json">
      ${JSON.stringify(
        {
          '@context': 'https://schema.org',
          '@type': 'WebSite',
          name: siteName,
          description,
          url: siteUrl,
          inLanguage: language,
        },
        null,
        2,
      ).replace(/</g, '\\u003c')}
    </script>
  `;
}

function renderJsonLdPost({ post, siteUrl, siteName, author, canonicalUrl, language }) {
  return `
    <script type="application/ld+json">
      ${JSON.stringify(
        {
          '@context': 'https://schema.org',
          '@type': 'BlogPosting',
          mainEntityOfPage: {
            '@type': 'WebPage',
            '@id': canonicalUrl,
          },
          headline: post.title,
          description: post.excerpt,
          inLanguage: language,
          image: post.image || undefined,
          datePublished: post.date,
          dateModified: post.updated || post.date,
          author: {
            '@type': 'Person',
            name: author,
          },
          publisher: {
            '@type': 'Person',
            name: author,
          },
          isPartOf: {
            '@type': 'Blog',
            name: siteName,
            url: siteUrl,
          },
        },
        null,
        2,
      ).replace(/</g, '\\u003c')}
    </script>
  `;
}

function postListMarkup(posts, sectionTitle, config) {
  const t = config.labels;
  const sectionHeader = `
    <header class="section-heading">
      <div>
        <h2 id="journal-title">${escapeHtml(sectionTitle)}</h2>
      </div>
      <p class="section-count"><span>${String(posts.length).padStart(2, '0')}</span> ${posts.length === 1 ? t.article : t.articles}</p>
    </header>
  `;

  if (!posts.length) {
    return `
      <section class="journal" aria-labelledby="journal-title">
        ${sectionHeader}
        <div class="empty-index">
          <div class="material-grid" aria-hidden="true">
            <span></span><span></span><span></span><span></span>
          </div>
          <div class="empty-copy">
            <p class="eyebrow">Index / 000</p>
            <h3>${t.empty}</h3>
            <p>${t.emptyDetail}</p>
          </div>
        </div>
      </section>
    `;
  }

  const items = posts
    .map(
      (post, index) => `
      <article class="post-item">
        <a class="post-link" href="${withBase(config, post.url)}">
          <span class="post-number">${String(index + 1).padStart(3, '0')}</span>
          <span class="post-copy">
            <span class="post-meta">${formatDate(post.date, config.language)} · ${post.readTime} ${config.labels.readTime}</span>
            <span class="post-title">${escapeHtml(post.title)}</span>
            <span class="post-excerpt">${escapeHtml(post.excerpt)}</span>
          </span>
          <span class="post-arrow" aria-hidden="true">↗</span>
        </a>
      </article>
    `,
    )
    .join('\n');

  return `
    <section class="journal" aria-labelledby="journal-title">
      ${sectionHeader}
      <div class="post-list">${items}</div>
    </section>
  `;
}

function renderShell({ title, description, canonicalUrl, bodyClass = '', main, config, extraHead = '', alternates = {} }) {
  const t = config.labels;
  const other = config.language === 'de' ? 'en' : 'de';
  const switchPath = alternates[other] || (other === 'en' ? '/en/' : '/');
  const siteName = config.siteTitle;
  const pageTitle = title === siteName ? title : `${title} | ${siteName}`;
  const metaDesc = description || config.siteDescription;
  const jsonLdWebsite = renderJsonLdWebsite({
    siteUrl: absolute(config, config.homePath),
    siteName,
    description: config.siteDescription,
    language: config.language || 'de',
  });

  return `<!doctype html>
<html lang="${config.language || 'de'}" id="top">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(pageTitle)}</title>
  <meta name="description" content="${escapeHtml(metaDesc)}">
  <meta name="robots" content="index,follow">
  <meta name="theme-color" content="#050505">
  <meta name="color-scheme" content="dark">
  <link rel="icon" href="${withBase(config, '/favicon.svg')}" type="image/svg+xml">
  ${buildCanonical(canonicalUrl)}
  ${Object.entries(alternates).map(([lang, url]) => `<link rel="alternate" hreflang="${lang}" href="${escapeHtml(absolute(config, url))}">`).join('\n  ')}
  ${renderMetaTags({
    title: pageTitle,
    description: metaDesc,
    canonicalUrl,
    siteName,
    twitterHandle: config.twitterHandle,
    type: bodyClass === 'post-page' ? 'article' : 'website',
    image: bodyClass === 'post-page' ? extraHead.image : undefined,
    publishedTime: bodyClass === 'post-page' ? extraHead.publishedTime : undefined,
    modifiedTime: bodyClass === 'post-page' ? extraHead.modifiedTime : undefined,
  })}
  <link rel="stylesheet" href="${withBase(config, '/styles.css')}">
  <link rel="alternate" type="application/rss+xml" title="RSS" href="${withBase(config, config.feedPath)}">
  ${typeof extraHead === 'string' ? extraHead : extraHead.html || ''}
  ${jsonLdWebsite}
</head>
<body>
  <a class="skip-link" href="#content">${t.skip}</a>
  <div class="frame">
    <header class="site-header">
      <a href="${withBase(config, config.homePath)}" class="site-title">${escapeHtml(siteName)}</a>
      <nav aria-label="${t.navigation}" class="site-nav">
        <a href="${withBase(config, config.homePath)}"${bodyClass === 'home' ? ' aria-current="page"' : ''}>Index</a>
        <a href="${withBase(config, config.aboutPath)}"${bodyClass === 'about-page' ? ' aria-current="page"' : ''}>${t.about}</a>
        <a href="${withBase(config, config.feedPath)}">RSS</a>
        <a href="${withBase(config, switchPath)}" hreflang="${other}" lang="${other}" aria-label="${other === 'en' ? 'Read in English' : 'Auf Deutsch lesen'}">${other.toUpperCase()}</a>
      </nav>
    </header>

    <main id="content" class="${bodyClass}">${main}</main>

    <footer class="site-footer">
      <p>© ${new Date().getFullYear()} ${escapeHtml(config.author)}</p>
      <nav aria-label="${t.footer}">
        <a href="${withBase(config, config.feedPath)}">RSS</a>
        <a href="${withBase(config, '/sitemap.xml')}">Sitemap</a>
        <a href="https://github.com/telip007" rel="me">GitHub</a>
        <a href="${withBase(config, '/datenschutz/')}" lang="de">${config.language === 'en' ? 'Privacy (German)' : 'Datenschutz'}</a>
        <a href="#top">${t.top}</a>
      </nav>
    </footer>
  </div>
</body>
</html>`;
}

function renderPostPage(post, { config, previousPost, nextPost }) {
  const canonical = absolute(config, post.url);
  const jsonLdPost = renderJsonLdPost({
    post: {
      ...post,
      image: post.image,
    },
    siteUrl: absolute(config, config.homePath),
    siteName: config.siteTitle,
    author: config.author,
    canonicalUrl: canonical,
    language: config.language || 'de',
  });

  const nav = `
    <nav class="post-nav" aria-label="${config.labels.articleNavigation}">
      ${previousPost ? `<a class="button" href="${withBase(config, previousPost.url)}">← ${escapeHtml(previousPost.title)}</a>` : '<span></span>'}
      ${nextPost ? `<a class="button" href="${withBase(config, nextPost.url)}">${escapeHtml(nextPost.title)} →</a>` : '<span></span>'}
    </nav>
  `;

  const main = `
    <article class="post-article">
      <header class="post-header">
        <p class="eyebrow">${config.labels.article} / ${formatDate(post.date, config.language)}</p>
        <h1>${escapeHtml(post.title)}</h1>
        <p class="post-deck">${escapeHtml(post.excerpt)}</p>
        <div class="post-byline">
          <p>${post.readTime} ${config.labels.readTime}</p>
          <p>${post.tags.map((tag) => `<a class="tag-link" href="${withBase(config, `${config.tagPath}${post.tagIndex.get(tag)}/`)}">${escapeHtml(tag)}</a>`).join(' · ')}</p>
        </div>
      </header>
      <div class="post-content">${post.html}</div>
      ${nav}
      ${jsonLdPost}
    </article>
  `;

  return renderShell({
    title: post.title,
    alternates: post.alternates,
    description: post.excerpt,
    canonicalUrl: canonical,
    bodyClass: 'post-page',
    main,
    config,
    extraHead: {
      image: post.image,
      publishedTime: new Date(post.date).toISOString(),
      modifiedTime: new Date(post.updated || post.date).toISOString(),
      html: '',
    },
  });
}

async function writeFileSafe(filePath, content) {
  await fsp.mkdir(path.dirname(filePath), { recursive: true });
  await fsp.writeFile(filePath, content, 'utf8');
}

const LABELS = {
  de: { notes: 'Notizen', article: 'Text', articles: 'Texte', empty: 'Noch keine Texte veröffentlicht.', emptyDetail: 'Der erste Text erscheint hier, wenn er bereit ist.', readTime: 'Min. Lesezeit', skip: 'Zum Inhalt springen', navigation: 'Hauptnavigation', footer: 'Fußzeile', top: 'Nach oben ↑', about: 'Über diesen Blog', articleNavigation: 'Artikelnavigation', intro: 'KI, LLMs & Agentic Engineering', edition: 'Beobachtungen aus der Praxis', more: 'Über diesen Blog', topic: 'Thema', topicPosts: 'Texte zum Thema' },
  en: { notes: 'Notes', article: 'Article', articles: 'Articles', empty: 'No articles published yet.', emptyDetail: 'The first article will appear here when it is ready.', readTime: 'min read', skip: 'Skip to content', navigation: 'Main navigation', footer: 'Footer', top: 'Back to top ↑', about: 'About this blog', articleNavigation: 'Article navigation', intro: 'AI, LLMs & Agentic Engineering', edition: 'Observations from practice', more: 'About this blog', topic: 'Topic', topicPosts: 'Articles about' },
};
function absolute(config, route) { return ensureAbs(config.siteUrl, withBase(config, route)); }
function validSlug(value, label) {
  if (typeof value !== 'string' || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)) throw new Error(`Invalid ${label}: ${value}`);
  return value;
}
function xml(value) { return escapeHtml(value); }

export async function build(root = process.cwd()) {
  const src = path.join(root, 'src');
  const dist = path.join(root, 'dist');
  const base = JSON.parse(await fsp.readFile(path.join(src, 'config.json'), 'utf8'));
  base.assetsBase = normalizeBasePath(base.basePath);
  base.siteUrl = base.siteUrl.replace(/\/$/, '');
  const locales = {};
  for (const lang of ['de', 'en']) {
    const about = parseMatter(await fsp.readFile(path.join(src, lang === 'de' ? 'about.md' : 'about.en.md'), 'utf8'));
    const aboutSlug = validSlug(about.data.slug || (lang === 'de' ? 'ueber-mich' : 'about'), 'about slug');
    locales[lang] = { ...base, ...base.locales?.[lang], language: lang, labels: LABELS[lang], homePath: lang === 'de' ? '/' : '/en/', aboutPath: `${lang === 'de' ? '/' : '/en/'}${aboutSlug}/`, tagPath: lang === 'de' ? '/themen/' : '/en/tags/', feedPath: lang === 'de' ? '/rss.xml' : '/en/rss.xml', about };
  }
  const names = await fsp.readdir(path.join(src, 'posts')).catch(e => { if (e.code === 'ENOENT') return []; throw e; });
  const posts = [];
  const pairs = new Map();
  for (const name of names.filter(n => n.endsWith('.md')).sort()) {
    const parsed = parseMatter(await fsp.readFile(path.join(src, 'posts', name), 'utf8'));
    if (parsed.data.draft !== undefined && typeof parsed.data.draft !== 'boolean') throw new Error(`draft must be true or false: ${name}`);
    if (parsed.data.draft === true) continue;
    const lang = parsed.data.lang || 'de';
    if (!locales[lang]) throw new Error(`Unsupported lang in ${name}: ${lang}`);
    const slug = validSlug(parsed.data.slug || path.basename(name, '.md'), 'post slug');
    const date = parsed.data.date || (await fsp.stat(path.join(src, 'posts', name))).mtime.toISOString();
    if (!date || !Number.isFinite(new Date(date).getTime())) throw new Error(`Valid date required: ${name}`);
    const updated = parsed.data.updated || date;
    if (!Number.isFinite(new Date(updated).getTime())) throw new Error(`Invalid updated date: ${name}`);
    if (parsed.data.tags !== undefined && !Array.isArray(parsed.data.tags)) throw new Error(`tags must be an array: ${name}`);
    const post = { slug, lang, title: String(parsed.data.title || slug), date, updated, tags: [...new Set((parsed.data.tags || []).map(String).map(t => t.trim()).filter(Boolean))], excerpt: String(parsed.data.excerpt || parsed.data.description || parsed.content.slice(0, 140).replace(/\n/g, ' ').trim()), html: md.render(parsed.content), readTime: estimateReadTime(parsed.content), image: parsed.data.image, url: `${lang === 'de' ? '/texte/' : '/en/articles/'}${slug}/`, alternates: {} };
    if (parsed.data.translationKey !== undefined) {
      const key = validSlug(parsed.data.translationKey, 'translationKey');
      const group = pairs.get(key) || {};
      if (group[lang]) throw new Error(`Duplicate translationKey ${key} for ${lang}`);
      group[lang] = post;
      pairs.set(key, group);
    }
    posts.push(post);
  }
  for (const group of pairs.values()) {
    const alternates = Object.fromEntries(Object.entries(group).map(([lang, post]) => [lang, post.url]));
    for (const post of Object.values(group)) post.alternates = alternates;
  }
  const routes = new Map();
  const add = (route, content, alternates = null) => {
    if (routes.has(route)) throw new Error(`Duplicate output route: ${route}`);
    routes.set(route, { content, alternates });
  };
  const homeAlternates = { de: '/', en: '/en/' };
  const aboutAlternates = Object.fromEntries(Object.entries(locales).map(([lang, c]) => [lang, c.aboutPath]));
  const languageTags = {};
  for (const lang of ['de', 'en']) {
    const tags = new Map();
    for (const post of posts.filter(p => p.lang === lang)) for (const tag of post.tags) {
      const slug = validSlug(slugifyTag(tag), 'tag slug');
      if ([...tags].some(([other, value]) => value === slug && other !== tag)) throw new Error(`Tag slug collision: ${tag}`);
      tags.set(tag, slug);
    }
    languageTags[lang] = tags;
  }
  for (const lang of ['de', 'en']) {
    const config = locales[lang];
    const t = config.labels;
    const sorted = posts.filter(p => p.lang === lang).sort((a, b) => new Date(b.date) - new Date(a.date) || a.slug.localeCompare(b.slug));
    const tags = languageTags[lang];
    for (const post of sorted) post.tagIndex = tags;
    const indexMain = `<section class="intro-block" aria-labelledby="intro-title"><h1 id="intro-title">${escapeHtml(config.siteSubtitle)}</h1><div class="intro-bottom"><p class="lead">${escapeHtml(config.siteDescription)}</p><a class="text-link" href="${withBase(config, config.aboutPath)}">${t.more} <span aria-hidden="true">↗</span></a></div></section>${postListMarkup(sorted, t.articles, config)}`;
    add(config.homePath, renderShell({ title: config.siteTitle, canonicalUrl: absolute(config, config.homePath), bodyClass: 'home', main: indexMain, config, alternates: homeAlternates }), homeAlternates);
    sorted.forEach((post, i) => add(post.url, renderPostPage(post, { config, previousPost: sorted[i - 1], nextPost: sorted[i + 1] }), post.alternates));
    const aboutHtml = md.render(config.about.content);
    const aboutTitle = config.about.data.title || t.about;
    add(config.aboutPath, renderShell({ title: aboutTitle, description: config.about.data.description, canonicalUrl: absolute(config, config.aboutPath), bodyClass: 'about-page', main: `<article class="about"><aside class="page-marker" aria-hidden="true"><span>${t.about}</span><span>TG / 01</span></aside><div class="about-content">${aboutHtml.includes('<h1') ? '' : `<h1>${escapeHtml(aboutTitle)}</h1>`}${aboutHtml}</div></article>`, config, alternates: aboutAlternates }), aboutAlternates);
    for (const [tag, slug] of tags) {
      const route = `${config.tagPath}${slug}/`;
      // Only identical tag labels are counterparts; translated tags are not guessed.
      const alternates = Object.fromEntries(Object.entries(locales).filter(([l]) => languageTags[l].has(tag)).map(([l, c]) => [l, `${c.tagPath}${languageTags[l].get(tag)}/`]));
      const title = `${t.topic}: ${tag}`;
      add(route, renderShell({ title, description: `${t.topicPosts} ${tag}.`, canonicalUrl: absolute(config, route), bodyClass: 'tag-page', main: `<h1>${escapeHtml(title)}</h1>${postListMarkup(sorted.filter(p => p.tags.includes(tag)), `${t.topicPosts} ${tag}`, config)}`, config, alternates }), alternates);
    }
    const items = sorted.map(post => `<item><title>${xml(post.title)}</title><link>${xml(absolute(config, post.url))}</link><guid>${xml(absolute(config, post.url))}</guid><pubDate>${new Date(post.date).toUTCString()}</pubDate><description>${xml(post.excerpt)}</description></item>`).join('\n');
    add(config.feedPath, `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>${xml(config.siteTitle)}</title><link>${xml(absolute(config, config.homePath))}</link><description>${xml(config.siteDescription)}</description><language>${lang}</language>${items}</channel></rss>`);
  }
  // Preserve the existing German legal text; English pages label its language explicitly.
  const privacy = parseMatter(await fsp.readFile(path.join(src, 'datenschutz.md'), 'utf8'));
  const privacyTitle = privacy.data.title || 'Datenschutz';
  const privacyHtml = md.render(privacy.content);
  add('/datenschutz/', renderShell({ title: privacyTitle, description: privacy.data.description, canonicalUrl: absolute(base, '/datenschutz/'), bodyClass: 'privacy-page', main: `<article class="about"><aside class="page-marker" aria-hidden="true"><span>Datenschutz</span><span>TG / 02</span></aside><div class="about-content">${privacyHtml.includes('<h1') ? '' : `<h1>${escapeHtml(privacyTitle)}</h1>`}${privacyHtml}</div></article>`, config: locales.de }), {});
  // Keep the existing German /about/ redirect.
  if (locales.de.aboutPath !== '/about/') add('/about/', `<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=${withBase(base, locales.de.aboutPath)}">${buildCanonical(absolute(base, locales.de.aboutPath))}<title>Weiterleitung</title></head><body><a href="${withBase(base, locales.de.aboutPath)}">Über diesen Blog</a></body></html>`);
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">${[...routes].filter(([, p]) => p.alternates !== null).map(([route, page]) => `<url><loc>${xml(absolute(base, route))}</loc>${Object.entries(page.alternates).map(([lang, url]) => `<xhtml:link rel="alternate" hreflang="${lang}" href="${xml(absolute(base, url))}"/>`).join('')}</url>`).join('\n')}</urlset>`;
  // Validate every route before replacing output; malformed content leaves last build intact.
  await fsp.rm(dist, { recursive: true, force: true });
  await fsp.mkdir(dist, { recursive: true });
  for (const [route, page] of routes) await writeFileSafe(path.join(dist, route.endsWith('/') ? `${route}index.html` : route), page.content);
  await fsp.copyFile(path.join(src, 'styles.css'), path.join(dist, 'styles.css'));
  await fsp.copyFile(path.join(src, 'favicon.svg'), path.join(dist, 'favicon.svg'));
  await writeFileSafe(path.join(dist, 'sitemap.xml'), sitemap);
  await writeFileSafe(path.join(dist, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${absolute(base, '/sitemap.xml')}\n`);
}

function slugifyTag(value) {
  return String(value)
    .toLowerCase()
    .trim()
    .replace(/ä/g, 'ae')
    .replace(/ö/g, 'oe')
    .replace(/ü/g, 'ue')
    .replace(/ß/g, 'ss')
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');
}

function watchMode() {
  const watcher = fs.watch(process.cwd(), { recursive: true }, async (eventType, filename) => {
    if (!filename) return;
    if (String(filename).startsWith('src') || filename === 'package.json') {
      try {
        await build();
        console.log(`[watch] Rebuilt (${eventType}: ${filename})`);
      } catch (error) {
        console.error('[watch] Build failed:', error.message);
      }
    }
  });
  return watcher;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  await build();
  if (process.argv.includes('--watch')) watchMode();
}
