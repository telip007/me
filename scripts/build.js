/** Compatibility entry point. Python is the single renderer for HTTP and export. */
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export function build(root = projectRoot) {
  return new Promise((resolve, reject) => {
    const child = spawn('uv', [
      'run', '--locked', '--project', projectRoot, 'python',
      path.join(projectRoot, 'scripts/export.py'), '--root', path.resolve(root),
    ], { cwd: projectRoot, stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '';
    child.stdout.on('data', data => { output += data; });
    child.stderr.on('data', data => { output += data; });
    child.on('error', error => reject(new Error(`Python build could not start. Install uv and run uv sync --locked. ${error.message}`)));
    child.on('close', code => code === 0 ? resolve() : reject(new Error(output.trim() || `Python export exited ${code}`)));
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  build().catch(error => { console.error(error.message); process.exitCode = 1; });
}
