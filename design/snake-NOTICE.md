# Contribution snake generation

The animated contribution SVGs are generated using [Platane/snk](https://github.com/Platane/snk), the same generator that the reference profile publicly uses. The official README explicitly provides [SVG-only Action usage](https://github.com/Platane/snk#svg), color customization and instructions for placing generated images in a GitHub Profile README. This profile follows that published use of the generator and retains its generated attribution.

At the checked version, the official repository and npm package metadata did not provide a general source license. We do not describe them as MIT or grant a new license to them. No official generator source is copied into this profile repository. `snake.mjs` is original local invocation and data-conversion glue; the official source remains in a separate local checkout, and only the generated artwork is published.

For the checked generation, use official v3 commit `d8f6715049803e982ee5ff501b6b9b7d5deeb09b` (version 3.5.0) with Node 24 or newer and an existing esbuild installation (checked with esbuild 0.25.12):

```sh
git clone https://github.com/Platane/snk /path/to/snk
git -C /path/to/snk checkout d8f6715049803e982ee5ff501b6b9b7d5deeb09b
node design/snake.mjs --source=/path/to/snk --esbuild=/path/to/esbuild
```

The script calls the official `getBestRoute`, `getPathToPose`, `cellsToGrid`, `parseEntry` and `createSvg` functions. It uses the reference workflow's light/dark palettes, four-part snake, 16-pixel cells, 12-pixel dots and 100-ms step duration. Loop length varies with the actual contribution route. There is no added GitHub Action, scheduler, credential or external image service.

The input is Bluuok's public contribution-calendar snapshot, captured on 2026-10-05, in `contributions.json`. The graph is not copied from the reference author's activity. Reduced-motion variants preserve the initial contribution grid and snake without CSS animation.
