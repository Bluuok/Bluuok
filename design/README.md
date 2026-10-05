# Rebuilding the profile artwork

The checked-in SVGs work without any runtime service, GitHub secret or scheduled workflow. The generator is based on the authorized reference described in [NOTICE.md](../NOTICE.md).

Use Python 3.12 or newer and install `fonttools` and `uharfbuzz` in an isolated environment. Download these fonts from the `google/fonts` repository into `design/fonts/`:

| Local name | Official source |
| --- | --- |
| `Archivo.ttf` | `ofl/archivo/Archivo[wdth,wght].ttf` |
| `Plex.ttf` | `ofl/ibmplexsans/IBMPlexSans[wdth,wght].ttf` |
| `NotoSC.ttf` | `ofl/notosanssc/NotoSansSC[wght].ttf` |

Their SIL OFL notices are retained in `licenses/`. Font files are excluded from Git. Run from the repository root:

```sh
python design/build.py
python design/readme.py
```

The hero uses the reference's 15-second crystal dislocation loop. The original project illustrations loop in 12 seconds (ThreadCove) and 9 seconds (Clawtide). Each has desktop, mobile, light, dark and static variants. `<picture>` selects static artwork when the viewer prefers reduced motion. All lettering is outlined; SVGs need no external fonts or scripts.

`contributions.json` is a public GitHub contribution-calendar snapshot for Bluuok captured on 2026-10-05. The snake is an original decorative traversal of those cells. It does not claim that a scheduled refresh exists. To update the calendar, replace the public snapshot and regenerate the SVGs. Folio merge counts and links are manually verified in the README.
