import fs from 'node:fs';
import path from 'node:path';

// Canonical URLs always describe production, including during a preview build.
// VERCEL_URL is a deployment URL and must never become the SEO origin.
const sourceOrigin = 'https://dr17.vercel.app';
const candidate = process.env.SITE_URL ||
  (process.env.VERCEL_PROJECT_PRODUCTION_URL && `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`) ||
  sourceOrigin;
let parsed;
try { parsed = new URL(candidate); } catch { throw new Error('SITE_URL must be an absolute HTTPS origin'); }
if (parsed.protocol !== 'https:' || parsed.username || parsed.password ||
    parsed.pathname !== '/' || parsed.search || parsed.hash || /\s/.test(candidate)) {
  throw new Error('SITE_URL must be an HTTPS origin without credentials, a path, query or fragment');
}
const origin = parsed.origin;
const preview = Boolean(process.env.VERCEL_ENV && process.env.VERCEL_ENV !== 'production');
const verification = process.env.GOOGLE_SITE_VERIFICATION || '';
if (verification && !/^[A-Za-z0-9_-]{1,300}$/.test(verification)) {
  throw new Error('GOOGLE_SITE_VERIFICATION must contain only the supplied verification token');
}

fs.rmSync('dist', { recursive: true, force: true });
fs.mkdirSync('dist', { recursive: true });
for (const file of ['style.css', 'nojs.css', 'app.js', 'favicon.svg', 'site.webmanifest',
                    'robots.txt', 'sitemap.xml', '404.html', 'index.html']) {
  if (!fs.existsSync(file)) throw new Error(`Required source file is missing: ${file}`);
  fs.copyFileSync(file, path.join('dist', file));
}
for (const dir of ['fa', 'en', 'ar', 'assets']) fs.cpSync(dir, path.join('dist', dir), { recursive: true });

function rewrite(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) { rewrite(file); continue; }
    if (!/\.(?:html|xml|txt|md|webmanifest)$/.test(file)) continue;
    let source = fs.readFileSync(file, 'utf8').replaceAll(sourceOrigin, origin);
    if (file.endsWith('.html')) {
      if (preview) {
        source = source.replace(/<meta name="robots" content="[^"]*">/,
                                '<meta name="robots" content="noindex, follow">');
      }
      if (verification && !file.endsWith('404.html')) {
        source = source.replace('</head>', `<meta name="google-site-verification" content="${verification}"></head>`);
      }
    }
    fs.writeFileSync(file, source);
  }
}
rewrite('dist');
// Let crawlers fetch preview HTML and see noindex. Disallow:/ would hide it.
if (preview) fs.writeFileSync('dist/robots.txt', 'User-agent: *\nDisallow: /api/\n');
console.log(`Built ${JSON.parse(fs.readFileSync('content/routes.json','utf8')).length} canonical pages for ${origin}${preview ? ' (preview: noindex)' : ''}`);
