# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

14 agent-based simulations of complexity economics concepts from Eric Beinhocker's *The Origin of Wealth* (2006). Each simulation is self-contained in a numbered directory. The project includes a launch dashboard, a unified research findings page, and analysis documents.

## Running simulations

Each simulation has a CLI. All run from their own directory with Python 3.14+:

```bash
cd 01-stock-market && python3 cli.py --ticks 200 --seed 42
cd 07-sugarscape && python3 cli.py --ticks 200 --seed 42
cd 13-sand-pile && python3 cli.py --ticks 10000 --seed 42
```

Some simulations require a mode flag (these also work without, defaulting to the first option):
- `01-stock-market`: `--learning` (default) or `--rational`
- `04-punctuated-equilibrium`: `--evolve` (default) or `--cascade-test`
- `06-prisoners-dilemma`: `--spatial` (default) or `--tournament`
- `12-predator-prey`: spatial (default) or `--ode`

Dependencies: Python stdlib + NumPy (used by 01, 04, 05, 06, 07, 09, 10). No other pip packages. Some simulations are pure stdlib.

## Architecture

### Per-simulation structure
Every `NN-name/` directory contains:
- `simulation.py` — Core model (dataclass configs, agent/environment classes, simulation loop)
- `cli.py` — CLI entry point with argparse, progress output, CSV/JSON export
- `index.html` — Self-contained interactive browser visualization (dark theme, Chart.js from CDN)
- `experiments.md` — Planned experiments and theoretical background
- `findings.md` — Actual results from CLI experiments with analysis

### Web pages (root level)
- `index.html` — Launch dashboard linking all 14 simulations (dark theme)
- `findings.html` — Unified research findings page (light cream theme, Anthropic Economic Index style)
- `synthesis.md` — Cross-model analysis mapping simulations to Beinhocker's thesis
- `empirical-validation.md` — 35 comparisons of simulation outputs to real-world data

### Deployment
Static site configured for Cloudflare Pages via `wrangler.toml`. All HTML files are self-contained — no build step.

## Key conventions

### HTML visualizations
- Dark theme: `#0a0e14` background, green/teal/amber accents
- Chart.js 4.x from CDN for all charts
- **Chart containers must use explicit `height` (280px regular, 340px wide) — not `min-height` with auto grid rows**
- **Never use `!important` on canvas width/height CSS** — it fights Chart.js responsive sizing
- **Add `min-height: 0; overflow: hidden;` to any flex/grid container holding a canvas** — prevents the classic CSS grid overflow bug where canvases grow unbounded
- Each simulation re-implements its model in JavaScript inside index.html (the Python simulation.py is for CLI experiments, the JS is for browser visualization)
- Preset experiments are embedded as dropdowns/buttons in each sim's sidebar

### Python simulations
- Use `@dataclass` for all configuration
- All simulations accept `--seed` for reproducibility
- Export via CSV (`--output`) and/or JSON (`--json`)
- No shared library between simulations — each is fully self-contained

### Findings page (findings.html)
- Light theme (`#faf9f5` background) — intentionally different from the dark simulation theme
- Each simulation section includes: key finding callout, book quote blockquote, metric cards, experiment table, emergent behaviors list, Beinhocker connection
- Book quotes use `.book-quote` class with teal left border

## The book
`beinhocker.pdf` (547 pages, gitignored) is the source material. Key chapter-to-simulation mapping:
- Ch 4 → 07-sugarscape
- Ch 6 → 01-stock-market, 06-prisoners-dilemma, 10-el-farol-bar
- Ch 7 → 03-boolean-network, 05-rigids-flexibles
- Ch 8 → 02-beer-game, 04-punctuated-equilibrium, 11-schelling, 12-predator-prey, 13-sand-pile
- Ch 9 → 08-technology-evolution
- Ch 14 → 14-business-plans
- Ch cross → 09-integrated-economy
