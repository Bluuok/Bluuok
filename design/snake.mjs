/**
 * Original offline glue for Platane/snk's publicly documented SVG generator.
 * Node 24+ and esbuild. Clone the pinned official v3 commit outside this repo,
 * then run `node design/snake.mjs --source=/path/to/snk --esbuild=/path/to/esbuild`.
 * No upstream source, credentials, network requests or scheduled jobs are used
 * by this script. See snake-NOTICE.md for public usage and provenance.
 */
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { createRequire, registerHooks } from 'node:module';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const designDir = path.dirname(fileURLToPath(import.meta.url));
const sourceArg = process.argv.find(a => a.startsWith('--source='));
const sourceDir = path.resolve(sourceArg?.slice(9) || path.join(designDir, '../../reference/snk'));
const sourceUrl = pathToFileURL(sourceDir + path.sep).href;
const esbuildArg = process.argv.find(a => a.startsWith('--esbuild='));
const esbuild = createRequire(import.meta.url)(esbuildArg?.slice(10) || 'esbuild');

function sourceFile(candidate) {
  for (const file of [candidate + '.ts', path.join(candidate, 'index.ts'), candidate]) {
    if (existsSync(file) && path.extname(file)) return file;
  }
  throw new Error(`Cannot resolve official snk module: ${candidate}`);
}

// Resolve official workspace aliases and transpile its TS in memory without
// copying its source into the profile or installing its packages.
registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier.startsWith('@snk/')) {
      return nextResolve(pathToFileURL(sourceFile(path.join(sourceDir, 'packages', specifier.slice(5)))).href, context);
    }
    if (specifier.startsWith('.') && context.parentURL?.startsWith(sourceUrl)) {
      const candidate = fileURLToPath(new URL(specifier, context.parentURL));
      return nextResolve(pathToFileURL(sourceFile(candidate)).href, context);
    }
    return nextResolve(specifier, context);
  },
  load(url, context, nextLoad) {
    if (url.startsWith(sourceUrl) && url.endsWith('.ts')) {
      return { format: 'module', shortCircuit: true,
        source: esbuild.transformSync(readFileSync(fileURLToPath(url), 'utf8'), { loader: 'ts', format: 'esm' }).code };
    }
    return nextLoad(url, context);
  },
});

const [solver, pose, fixtures, svg, converter, options, snakeTools] = await Promise.all([
  import('@snk/solver/getBestRoute'),
  import('@snk/solver/getPathToPose'),
  import('@snk/types/__fixtures__/snake'),
  import('@snk/svg-creator'),
  import(pathToFileURL(path.join(sourceDir, 'packages/generate-snake-animation/cellsToGrid.ts')).href),
  import(pathToFileURL(path.join(sourceDir, 'packages/generate-snake-animation/outputsOptions.ts')).href),
  import('@snk/types/snake'),
]);

const snapshot = JSON.parse(readFileSync(path.join(designDir, 'contributions.json'), 'utf8'));
const levels = ['NONE', 'FIRST_QUARTILE', 'SECOND_QUARTILE', 'THIRD_QUARTILE', 'FOURTH_QUARTILE'];
const cells = snapshot.weeks.flatMap((week, x) => week.contributionDays.map(day => ({
  x,
  y: new Date(day.date + 'T00:00:00Z').getUTCDay(),
  date: day.date,
  count: day.contributionCount,
  level: levels.indexOf(day.contributionLevel),
})));
if (cells.some(cell => cell.level < 0)) throw new Error('Unknown contribution level');
const grid = converter.cellsToGrid(cells);
const chain = solver.getBestRoute(grid, fixtures.snake4);
if (!chain?.length) throw new Error('The official solver did not produce a route');
const returnPath = pose.getPathToPose(chain.at(-1), fixtures.snake4);
if (!returnPath) throw new Error('The official solver could not close the loop');
chain.push(...returnPath);

// Validate the actual route, rather than trusting decorative movement.
const occupied = new Set(cells.filter(c => c.level > 0).map(c => `${c.x},${c.y}`));
for (const position of chain) {
  occupied.delete(`${snakeTools.getHeadX(position)},${snakeTools.getHeadY(position)}`);
}
if (occupied.size) throw new Error(`${occupied.size} active contribution cells remain uneaten`);

const palettes = {
  light: { snake: '#A45220', dots: '#DDE3EA,#B4C8EA,#83A6E0,#4F7FCF,#2D5FB8' },
  dark: { snake: '#E3B75E', dots: '#1E2B3A,#2B4466,#3A64A0,#5A8BE0,#A8C4F2' },
};
const captured = cells.at(-1).date;
const metrics = { source: sourceDir, days: cells.length, activeDays: cells.filter(c => c.level > 0).length,
  totalContributions: snapshot.totalContributions, steps: chain.length, stepMs: 100, loopMs: chain.length * 100, assets: [] };
for (const [theme, palette] of Object.entries(palettes)) {
  // Workflow options, parsed by the official generator.
  const settings = options.parseEntry(`snake.svg?palette=github-${theme}&color_snake=${palette.snake}&color_dots=${palette.dots}`);
  let artwork = svg.createSvg(grid, cells, chain, settings.drawOptions, settings.animationOptions);
  artwork = artwork.replace('<desc>', `<title>Bluuok contribution graph, eaten by a snake</title><desc>`)
    .replace('</desc>', `; Bluuok public calendar snapshot through ${captured}; ${snapshot.totalContributions} contributions.</desc>`);
  const animatedName = `contributions-${theme}.svg`;
  writeFileSync(path.join(designDir, '../assets', animatedName), artwork + '\n');
  // The first-frame layout is retained as the reduced-motion alternative.
  const still = artwork
    .replace(/@keyframes\s+[\w-]+\{(?:[^{}]*\{[^{}]*\})+\}/g, '')
    .replace(/animation(?:-name)?:[^;}]+;?/g, '');
  if (/@keyframes|animation:|animation-name:|<animate/.test(still)) throw new Error('Static artwork still animates');
  const stillName = `contributions-${theme}-still.svg`;
  writeFileSync(path.join(designDir, '../assets', stillName), still + '\n');
  metrics.assets.push({ name: animatedName, bytes: Buffer.byteLength(artwork + '\n') },
    { name: stillName, bytes: Buffer.byteLength(still + '\n') });
}
console.log(JSON.stringify(metrics, null, 2));
