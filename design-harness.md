# Design Harness — Simulation Redesign Spec

This document defines the design language for reworking all 16 simulation
index.html files to match the walkthrough page aesthetic.

## Reference
- Live walkthrough: https://beinhocker-mkirsanov.pages.dev/walkthrough.html
- Mini-sim examples: /mini/*.html (16 files showing the interactive component pattern)

## Design Tokens (CSS Variables)

```css
:root {
  --bg: #faf9f5;
  --bg-card: #ffffff;
  --bg-hover: #f5f3ee;
  --bg-metric: #f0eeea;
  --text-primary: #1a1a2e;
  --text-secondary: #4a4a5a;
  --text-tertiary: #7a7a8a;
  --accent-teal: #2a7f7f;
  --accent-teal-light: #e8f4f4;
  --accent-coral: #c96b5a;
  --accent-green: #4a8a5a;
  --accent-amber: #b08a3a;
  --border: #e2e0da;
  --border-light: #edecea;
  --shadow-sm: 0 1px 3px rgba(26,26,46,0.06);
  --shadow-md: 0 4px 12px rgba(26,26,46,0.08);
  --radius: 8px;
  --radius-lg: 12px;
  --font-sans: 'Inter', -apple-system, sans-serif;
  --font-serif: Georgia, 'Times New Roman', serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

## Typography
- Body: Inter 400, 0.9rem, line-height 1.7, color var(--text-primary)
- Headings: Inter 700 or Georgia serif for emphasis
- Data values: JetBrains Mono 500, var(--accent-teal)
- Labels: Inter 600, 0.75rem, uppercase, letter-spacing 0.06em, var(--accent-teal)
- Descriptions: 0.85rem, var(--text-secondary)

## Layout Pattern (for full simulations)
Each simulation page should use this structure:

```
┌─────────────────────────────────────────────┐
│ Nav bar (sticky, frosted glass)             │
├─────────────────────────────────────────────┤
│ Hero section (title, description, insight)  │
├──────────┬──────────────────┬───────────────┤
│ Controls │  Main canvas /   │  Stats panel  │
│ sidebar  │  visualization   │  (metrics,    │
│ (params, │  area             │  narrative)   │
│  presets)│                  │               │
├──────────┴──────────────────┴───────────────┤
│ Charts (2-column grid, explicit heights)    │
├─────────────────────────────────────────────┤
│ Footer (back to dashboard link)             │
└─────────────────────────────────────────────┘
```

3-column grid: 260px | 1fr | 280px
On mobile: stack vertically

## Component Styles

### Nav bar
- Sticky top, height 48px
- Background: rgba(250,249,245,0.92) with backdrop-filter: blur(12px)
- Border-bottom: 1px solid var(--border-light)
- Title left, "← Dashboard" link right

### Hero section
- Max-width: 900px centered, padding 2rem
- Title: 1.8rem Georgia serif, var(--text-primary)
- Subtitle: 0.9rem, var(--text-secondary)
- Key insight callout: teal left border, light teal background

### Controls sidebar
- Background: var(--bg-card), border: 1px solid var(--border), border-radius: var(--radius-lg)
- Section headers: 0.7rem uppercase, var(--accent-teal), letter-spacing 0.08em
- Inputs: clean borders, var(--bg), small rounded
- Buttons: background var(--bg-metric), border 1px solid var(--border), rounded
- Start/Pause primary button: background var(--accent-teal), color white
- Preset dropdown/buttons: subtle, var(--bg-metric) background

### Main visualization area
- Background: var(--bg-card), border, border-radius: var(--radius-lg)
- Canvas: border-radius 8px, background #f0eeea for empty state
- Adequate padding (1rem)

### Stats/metrics panel
- Background: var(--bg-card), border, border-radius
- Metric rows: label (var(--text-tertiary), 0.75rem) | value (var(--font-mono), var(--accent-teal))
- Narrative "What's Happening" box: italic, var(--text-secondary), border-left teal

### Charts
- 2-column grid, gap 16px
- Each chart: background var(--bg-card), border, border-radius, padding 1rem
- Chart title: 0.7rem uppercase, var(--accent-teal)
- EXPLICIT height: 280px (regular), 340px (wide spanning 2 cols)
- Canvas: width 100%, height calc(100% - 36px)
- min-height: 0; overflow: hidden on chart container
- Chart.js with light theme colors:
  - Grid lines: var(--border-light) or #eee
  - Tick labels: var(--text-tertiary), JetBrains Mono, 10px
  - Dataset colors: use accent palette (teal, coral, green, amber, blue)

### Footer
- Centered, padding 2rem
- "← Back to Dashboard" link in var(--accent-teal)
- Light border-top

## Canvas/Visualization Colors (light theme)
- Grid backgrounds: #f0eeea (warm gray)
- Agent/node colors: use the accent palette, NOT neon dark-theme colors
- Positive: var(--accent-green) #4a8a5a
- Negative/danger: var(--accent-coral) #c96b5a
- Neutral: var(--accent-teal) #2a7f7f
- Highlight: var(--accent-amber) #b08a3a
- Empty/background: #f0eeea or #e8e6e0

## Anti-patterns (DO NOT)
- No dark backgrounds (#0a0e14, #111820, etc.)
- No neon accent colors (#00cc66, #ff4488, #00ff88)
- No !important on canvas width/height
- No min-height instead of explicit height on chart containers
- No missing min-height:0/overflow:hidden on flex/grid chart parents
- No heavy shadows or glow effects
- No emoji in UI elements

## Quality Criteria (for evaluator)
1. Visual coherence: does it feel like it belongs on the same site as the walkthrough?
2. Typography: consistent use of Inter/Georgia/JetBrains Mono
3. Color palette: warm cream/teal/coral, no remnants of dark theme
4. Chart sizing: all charts render correctly at viewport size
5. Responsiveness: works at 1200px and 768px widths
6. Functionality: simulation actually runs, controls work
7. Navigation: can get back to dashboard
