import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { renderMermaidASCII } from '@zombie-mermaid/ascii-renderer';

const [directory, flag] = process.argv.slice(2);
if (!directory || (flag !== undefined && flag !== '--check') || process.argv.length > 4) {
  console.error('Usage: node render.mjs <diagram-directory> [--check]');
  process.exit(2);
}

const layouts = {
  'task-graph': { paddingX: 1, paddingY: 3 },
  'repair-loop': { paddingX: 1, paddingY: 5 },
};

for (const [name, spacing] of Object.entries(layouts)) {
  const source = readFileSync(new URL(`./${name}.mmd`, import.meta.url), 'utf8');
  const output = join(directory, `${name}.txt`);
  const art = renderMermaidASCII(source, {
    useAscii: false,
    boxBorderPadding: 1,
    colorMode: 'none',
    ...spacing,
  });
  // Preserve the layout while removing the renderer's right-hand canvas padding.
  const text = `${art.replace(/ +$/gm, '').trimEnd()}\n`;

  if (flag !== '--check') {
    writeFileSync(output, text);
  } else if (readFileSync(output, 'utf8') !== text) {
    console.error(`${output} differs from a fresh render`);
    process.exitCode = 1;
  }
}
