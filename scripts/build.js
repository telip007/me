import fs from 'node:fs';
import { promises as fsp } from 'node:fs';
import path from 'node:path';
import matter from 'gray-matter';
import MarkdownIt from 'markdown-it';

const CONFIG_PATH = path.join(process.cwd(), 'src', 'config.json');
const SRC_POST_DIR = path.join(process.cwd(), 'src', 'posts');
const SRC_STYLE = path.join(process.cwd(), 'src', 'styles.css');
const SRC_FAVICON = path.join(process.cwd(), 'src', 'favicon.svg');
const SRC_ABOUT = path.join(process.cwd(), 'src', 'about.md');
const DIST_DIR = path.join(process.cwd(), 'dist');

const WATCH = process.argv.includes('--watch');
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false,
});

function ensureAbs(base, rel) {
  const b = base.replace(/\/$/, '');
  return `${b}${rel.startsWith('/') ? rel : `/${rel}`}`;
}

function siteRoot(config) {
  return config.siteUrl.replace(/\/$/, '');
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

function formatDate(value) {
  try {
    const date = new Date(value);
    return new Intl.DateTimeFormat('en-US', {
      dateStyle: 'medium',
    }).format(date);
  } catch {
    return 'Unknown date';
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
  return `<link rel="canonical" href="${url}">`;
}

function renderMetaTags({ title, description, canonicalUrl, image, type = 'website', siteName, twitterHandle, publishedTime, modifiedTime }) {
  return `
    <meta property="og:site_name" content="${escapeHtml(siteName)}">
    <meta property="og:title" content="${escapeHtml(title)}">
    <meta property="og:description" content="${escapeHtml(description)}">
    <meta property="og:type" content="${type}">
    <meta property="og:url" content="${canonicalUrl}">
    ${publishedTime ? `<meta property="article:published_time" content="${publishedTime}">` : ''}
    ${modifiedTime ? `<meta property="article:modified_time" content="${modifiedTime}">` : ''}
    ${image ? `<meta property="og:image" content="${image}">` : ''}
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="${escapeHtml(title)}">
    <meta name="twitter:description" content="${escapeHtml(description)}">
    ${twitterHandle ? `<meta name="twitter:creator" content="${twitterHandle}">` : ''}
    ${twitterHandle ? `<meta name="twitter:site" content="${twitterHandle}">` : ''}
    ${image ? `<meta name="twitter:image" content="${image}">` : ''}
  `;
}

function renderJsonLdWebsite({ siteUrl, siteName, description }) {
  return `
    <script type="application/ld+json">
      ${JSON.stringify(
        {
          '@context': 'https://schema.org',
          '@type': 'WebSite',
          name: siteName,
          description,
          url: siteUrl,
          inLanguage: 'en',
        },
        null,
        2,
      )}
    </script>
  `;
}

function renderJsonLdPost({ post, siteUrl, siteName, author, canonicalUrl }) {
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
      )}
    </script>
  `;
}

function postListMarkup(posts, sectionTitle, config) {
  if (!posts.length) {
    return `<p>No posts yet.</p>`;
  }

  const items = posts
    .map(
      (post) => `
      <article class="post-item">
        <h3><a href="${withBase(config, post.url)}">${escapeHtml(post.title)}</a></h3>
        <p class="meta">${formatDate(post.date)} • ${post.readTime} min read • ${post.tags.map((tag) => `<a class="tag-link" href="${withBase(config, `/tags/${post.tagIndex.get(tag)}/`)}">#${escapeHtml(tag)}</a>`).join(' ')}</p>
        <p class="intro">${escapeHtml(post.excerpt)}</p>
      </article>
    `,
    )
    .join('\n');

  return `
    <section class="listing">
      <h2>${escapeHtml(sectionTitle)}</h2>
      <div class="divider"></div>
      ${items}
    </section>
  `;
}

function renderShell({ title, description, canonicalUrl, bodyClass = '', main, config, extraHead = '' }) {
  const siteName = config.siteTitle;
  const pageTitle = title === siteName ? title : `${title} | ${siteName}`;
  const metaDesc = description || config.siteDescription;
  const jsonLdWebsite = renderJsonLdWebsite({
    siteUrl: config.siteUrl,
    siteName,
    description: config.siteDescription,
  });

  return `<!doctype html>
<html lang="${config.language || 'en'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(pageTitle)}</title>
  <meta name="description" content="${escapeHtml(metaDesc)}">
  <meta name="robots" content="index,follow">
  <meta name="theme-color" content="#ffffff">
  <link rel="icon" href="${withBase(config, '/favicon.svg')}" type="image/svg+xml">
  ${buildCanonical(canonicalUrl)}
  ${renderMetaTags({
    title: pageTitle,
    description: metaDesc,
    canonicalUrl,
    siteName,
    twitterHandle: config.twitterHandle,
    type: bodyClass === 'post-page' ? 'article' : 'website',
    publishedTime: bodyClass === 'post-page' ? extraHead.publishedTime : undefined,
    modifiedTime: bodyClass === 'post-page' ? extraHead.modifiedTime : undefined,
  })}
  <link rel="stylesheet" href="${withBase(config, '/styles.css')}">
  <link rel="alternate" type="application/rss+xml" title="RSS" href="${withBase(config, '/rss.xml')}">
  ${typeof extraHead === 'string' ? extraHead : extraHead.html || ''}
  ${jsonLdWebsite}
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <div class="frame">
    <header class="site-header">
      <a href="${withBase(config, '/')}" class="site-title">${escapeHtml(siteName)}</a>
      <nav aria-label="Primary" class="site-nav">
        <a href="${withBase(config, '/')}">Home</a>
        <a href="${withBase(config, '/about/')}">About</a>
      </nav>
    </header>

    <main id="content" class="${bodyClass}">${main}</main>

    <footer class="site-footer">
      <p>© ${new Date().getFullYear()} ${escapeHtml(config.author)} · A minimal space on the web.</p>
      <p><a href="${withBase(config, '/sitemap.xml')}">Sitemap</a> · <a href="${withBase(config, '/rss.xml')}">RSS</a></p>
    </footer>
  </div>
</body>
</html>`;
}

function renderPostPage(post, { config, previousPost, nextPost }) {
  const canonical = ensureAbs(config.siteUrl, post.url);
  const jsonLdPost = renderJsonLdPost({
    post: {
      ...post,
      image: post.image,
    },
    siteUrl: config.siteUrl,
    siteName: config.siteTitle,
    author: config.author,
    canonicalUrl: canonical,
  });

  const nav = `
    <nav class="post-nav" aria-label="Post navigation">
      ${previousPost ? `<a class="button" href="${withBase(config, previousPost.url)}">← ${escapeHtml(previousPost.title)}</a>` : '<span></span>'}
      ${nextPost ? `<a class="button" href="${withBase(config, nextPost.url)}">${escapeHtml(nextPost.title)} →</a>` : '<span></span>'}
    </nav>
  `;

  const main = `
    <article class="post-page">
      <p class="kicker">${formatDate(post.date)} · ${post.readTime} min read</p>
      <h1>${escapeHtml(post.title)}</h1>
      <p class="meta">${post.tags.map((tag) => `<a class="tag-link" href="${withBase(config, `/tags/${post.tagIndex.get(tag)}/`)}">#${escapeHtml(tag)}</a>`).join(' ')}</p>
      <div class="divider"></div>
      <div class="post-content">${post.html}</div>
      ${nav}
      ${jsonLdPost}
    </article>
  `;

  return renderShell({
    title: post.title,
    description: post.excerpt,
    canonicalUrl: canonical,
    bodyClass: 'post-page',
    main,
    config,
    extraHead: {
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

async function build() {
  const [configRaw, styleText, faviconSvg, aboutRaw] = await Promise.all([
    fsp.readFile(CONFIG_PATH, 'utf8'),
    fsp.readFile(SRC_STYLE, 'utf8'),
    fsp.readFile(SRC_FAVICON, 'utf8'),
    fsp.readFile(SRC_ABOUT, 'utf8').catch(() => '# About\n\nThis page is intentionally minimal and can be edited in `src/about.md`.')
  ]);

  const config = JSON.parse(configRaw);
  config.siteUrl = ensureAbs(config.siteUrl, '');
  config.assetsBase = normalizeBasePath(config.basePath);

  const postFiles = await fsp.readdir(SRC_POST_DIR);
  const allPosts = await Promise.all(
    postFiles
      .filter((name) => name.endsWith('.md'))
      .map(async (fileName) => {
        const filePath = path.join(SRC_POST_DIR, fileName);
        const raw = await fsp.readFile(filePath, 'utf8');
        const parsed = matter(raw);
        const slug = parsed.data.slug || path.basename(fileName, '.md');
        const title = parsed.data.title || slug;
        const date = parsed.data.date || new Date().toISOString();
        const tags = (parsed.data.tags || [])
          .map((tag) => String(tag).trim())
          .filter(Boolean);
        const excerpt = parsed.data.excerpt || parsed.data.description || parsed.content.slice(0, 140).replace(/\n/g, ' ').trim();
        const html = md.render(parsed.content);

        return {
          slug,
          title,
          date,
          tags,
          excerpt,
          html,
          source: filePath,
          readTime: estimateReadTime(parsed.content),
          featured: Boolean(parsed.data.featured),
          image: parsed.data.image,
          updated: parsed.data.updated || date,
        };
      }),
  );

  const sortedPosts = [...allPosts].sort((a, b) => new Date(b.date) - new Date(a.date));
  const tagSet = new Map();
  sortedPosts.forEach((post) => {
    post.url = `/posts/${post.slug}/`;
    (post.tags || []).forEach((tag) => {
      const key = slugifyTag(tag);
      tagSet.set(tag, key);
    });
  });

  sortedPosts.forEach((post) => {
    post.tagIndex = tagSet;
  });

  await fsp.rm(DIST_DIR, { recursive: true, force: true });
  await fsp.mkdir(DIST_DIR, { recursive: true });

  await writeFileSafe(path.join(DIST_DIR, 'styles.css'), styleText);
  await writeFileSafe(path.join(DIST_DIR, 'favicon.svg'), faviconSvg);

  // Homepage
  const featuredPosts = sortedPosts.filter((post) => post.featured);
  const featuredSection = featuredPosts.length
    ? `
      <section class="featured">` +
      featuredPosts
        .map(
          (post) => `
            <article>
              <p class="kicker">Featured</p>
              <h2><a href="${withBase(config, post.url)}">${escapeHtml(post.title)}</a></h2>
              <p class="meta">${formatDate(post.date)} • ${post.readTime} min read</p>
              <p>${escapeHtml(post.excerpt)}</p>
            </article>
          `,
        )
        .join('') +
      `</section>`
    : '';

  const indexMain = `
    <section class="intro-block">
      <h1>${escapeHtml(config.siteSubtitle)}</h1>
      <p class="lead">${escapeHtml(config.siteDescription)}</p>
    </section>
    ${featuredSection}
    ${postListMarkup(sortedPosts, 'Latest Posts', config)}
  `;

  await writeFileSafe(
    path.join(DIST_DIR, 'index.html'),
    renderShell({
      title: config.siteTitle,
      description: config.siteDescription,
      canonicalUrl: ensureAbs(config.siteUrl, '/'),
      bodyClass: 'home',
      main: indexMain,
      config,
    }),
  );

  // Individual posts
  await Promise.all(
    sortedPosts.map(async (post, index) => {
      const previousPost = sortedPosts[index - 1] || null;
      const nextPost = sortedPosts[index + 1] || null;
      const page = renderPostPage(post, { config, previousPost, nextPost });
      await writeFileSafe(path.join(DIST_DIR, post.url, 'index.html'), page);
    }),
  );

  // About page
  const aboutParsed = matter(aboutRaw);
  const aboutTitle = aboutParsed.data.title || 'About';
  const aboutDescription = aboutParsed.data.excerpt || aboutParsed.data.description || 'About this static blog.';
  const aboutHtml = md.render(aboutParsed.content);
  const aboutMain = `<article class="about">${aboutHtml.includes('<h1') ? '' : `<h1>${escapeHtml(aboutTitle)}</h1>`}${aboutHtml}</article>`;
  await writeFileSafe(
    path.join(DIST_DIR, 'about', 'index.html'),
    renderShell({
      title: aboutTitle,
      description: aboutDescription,
      canonicalUrl: ensureAbs(config.siteUrl, '/about/'),
      bodyClass: 'about-page',
      main: aboutMain,
      config,
    }),
  );

  // Tag pages
  const tags = [...tagSet.entries()];
  for (const [rawTag, slug] of tags) {
    const postsForTag = sortedPosts.filter((post) => post.tags.includes(rawTag));
    const tagMain = `
      <h1>Tag: ${escapeHtml(rawTag)}</h1>
      ${postListMarkup(postsForTag, `Posts tagged ${rawTag}`, config)}
    `;
    await writeFileSafe(
      path.join(DIST_DIR, 'tags', slug, 'index.html'),
      renderShell({
        title: `Tag: ${rawTag}`,
        description: `Posts tagged with ${rawTag}.`,
        canonicalUrl: ensureAbs(config.siteUrl, `/tags/${slug}/`),
        bodyClass: 'tag-page',
        main: tagMain,
        config,
      }),
    );
  }

  // RSS feed
  const rssItems = sortedPosts
    .map((post) => {
      const link = ensureAbs(config.siteUrl, post.url);
      return `
      <item>
        <title><![CDATA[${post.title}]]></title>
        <link>${link}</link>
        <guid>${link}</guid>
        <pubDate>${new Date(post.updated).toUTCString()}</pubDate>
        <description><![CDATA[${post.excerpt}]]></description>
      </item>`;
    })
    .join('\n');

  const rss = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title><![CDATA[${config.siteTitle}]]></title>
    <link>${siteRoot(config)}/</link>
    <description><![CDATA[${config.siteDescription}]]></description>
    <language>${config.language || 'en'}</language>
    ${rssItems}
  </channel>
</rss>`;

  await writeFileSafe(path.join(DIST_DIR, 'rss.xml'), rss);

  // robots and sitemap
  await writeFileSafe(
    path.join(DIST_DIR, 'robots.txt'),
    `User-agent: *\nAllow: /\nSitemap: ${siteRoot(config)}/sitemap.xml\n`,
  );

  const urls = [
    '/',
    '/about/',
    '/rss.xml',
    '/sitemap.xml',
    '/robots.txt',
    ...sortedPosts.map((post) => post.url),
    ...tags.map(([, slug]) => `/tags/${slug}/`),
  ].map((u) => `<url><loc>${ensureAbs(config.siteUrl, u)}</loc></url>`);

  const sitemap = `<?xml version="1.0" encoding="UTF-8" ?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${urls.join('\n  ')}
</urlset>`;

  await writeFileSafe(path.join(DIST_DIR, 'sitemap.xml'), sitemap);
}

function slugifyTag(value) {
  return String(value)
    .toLowerCase()
    .trim()
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

await build();
if (WATCH) {
  watchMode();
}
