// Package existing public files for Cloudflare Pages. No external dependencies.
import { readdir, readFile, writeFile, mkdir, cp, rm, lstat } from 'node:fs/promises';
import { dirname, resolve, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(root, 'dist');
assert.equal(dirname(output), root, 'Build output must stay inside this repository');
assert.equal(relative(root, output), 'dist', 'Unexpected build output path');
const config = JSON.parse(await readFile(join(root, 'site.config.json'), 'utf8'));
const manifest = JSON.parse(await readFile(join(root, 'data/publication-manifest.json'), 'utf8'));
assert.equal(config.origin, 'https://jcvpn.blog');
assert.match(config.indexnow_key, /^[a-f0-9]{32}$/);
assert.equal(manifest.origin, config.origin);

// Fail before publishing if a page was edited without refreshing SEO metadata.
for (const [url, page] of Object.entries(manifest.pages)) {
  const path = resolve(root, page.file);
  assert.equal(dirname(path), root, 'Page must be in the site root');
  const html = await readFile(path, 'utf8');
  const hash = createHash('sha256').update(html.replaceAll('\r\n', '\n')).digest('hex');
  assert.equal(hash, page.sha256, `${page.file} changed: run tools/prepare_site.py before publishing`);
  assert.ok(html.includes(`rel="canonical" href="${url}"`), `Missing canonical: ${page.file}`);
  assert.ok(html.includes('name="robots" content="index,follow"'), `Indexing is disabled: ${page.file}`);
}
assert.equal((await readFile(join(root, config.indexnow_key + '.txt'), 'utf8')).trim(), config.indexnow_key);
const files = (await readdir(root, { withFileTypes: true }))
  .filter(entry => entry.isFile() && entry.name.endsWith('.html'))
  .map(entry => entry.name);
assert.ok(files.includes('404.html'), 'A top-level 404.html is required for this static multi-page site');
assert.equal(files.length, Object.keys(manifest.pages).length + 2, 'Refresh publication metadata for new or removed pages');
files.push('03-可信内容与SEO规范.md', '04-首批品牌档案.md', 'robots.txt', 'sitemap.xml', '.nojekyll', config.indexnow_key + '.txt');
async function collect(directory) {
  for (const entry of await readdir(join(root, directory), { withFileTypes: true })) {
    assert.ok(!entry.isSymbolicLink(), `Symlink is not a publication asset: ${entry.name}`);
    const name = join(directory, entry.name);
    if (entry.isDirectory()) await collect(name);
    else if (entry.isFile()) files.push(name);
  }
}
await collect('assets');
await collect('data');

// Only the verified repository-local dist directory is replaced.
try {
  const existing = await lstat(output);
  assert.ok(existing.isDirectory() && !existing.isSymbolicLink(), 'dist must be a regular directory');
  await rm(output, { recursive: true });
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
}
await mkdir(output);
for (const name of files.sort()) {
  const target = resolve(output, name);
  assert.ok(target.startsWith(output + sep), 'Asset path escaped dist');
  await mkdir(dirname(target), { recursive: true });
  await cp(join(root, name), target);
}
await writeFile(join(root, '.release', 'cloudflare-build.json'), JSON.stringify({ directory: 'dist', files: files.length, pages: Object.keys(manifest.pages).length }, null, 2)).catch(async error => {
  if (error.code !== 'ENOENT') throw error;
  await mkdir(join(root, '.release'), { recursive: true });
  await writeFile(join(root, '.release', 'cloudflare-build.json'), JSON.stringify({ directory: 'dist', files: files.length, pages: Object.keys(manifest.pages).length }, null, 2));
});
console.log(`Cloudflare Pages build ready: dist/ (${files.length} files, ${Object.keys(manifest.pages).length} canonical pages).`);
