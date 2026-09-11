# Design.md — ECDAT Visual Design

## Theme
Security / cybersecurity-tech aesthetic — dark-mode-friendly, precise, trustworthy. Avoid generic "startup blue" — this is a quantum-security audit tool, it should feel serious and technical, not playful.

## Color Palette — "Midnight Executive" (security-appropriate)

| Role | Color | Hex |
|---|---|---|
| Primary (dominant, ~60%) | Deep Navy | `#1E2761` |
| Background (dark mode) | Near-black slate | `#0F1420` |
| Background (light mode, if used) | Off-white | `#F4F7FB` |
| Secondary | Ice Blue | `#CADCFC` |
| Accent (sparingly — CTAs, highlights) | Teal | `#0FA3B1` |

## Risk-Level Color Coding (functional, not decorative — must be consistent everywhere)

| Risk Level | Color | Hex |
|---|---|---|
| SAFE | Green | `#02C39A` |
| PARTIAL | Amber/Yellow | `#F4A300` |
| VULNERABLE | Orange-Red | `#E85D2C` |
| CRITICAL | Deep Red | `#C1121F` |

**Rule: these four colors are reserved exclusively for risk-level indicators** (badges, chart segments, table row accents). Never reuse them decoratively elsewhere on the dashboard — consistency here is what makes the risk visualization scannable at a glance.

## Typography

| Element | Font | Size |
|---|---|---|
| Dashboard title / headers | Inter or system sans-serif, bold | 28-32px |
| Section headers | Same family, semi-bold | 18-20px |
| Body text / table content | Same family, regular | 14px |
| Code context snippets | Monospace (e.g., "Fira Code", "Consolas", or fallback `monospace`) | 13px |
| Big stat callout (Migration Readiness Score) | Bold, large | 48-60px |

## Layout Principles
- **Summary-first:** the Migration Readiness Score and risk breakdown chart should be the first thing visible — don't bury it below the findings table
- **Findings table:** use the risk-level colors as small left-border accents or badge chips per row, not full-row background fills (full-color rows get visually noisy at scale)
- **Drill-down view:** show code context in a monospace block styled like a code editor (dark background, light text) — reinforces the "security tool" feel
- **Charts:** use a donut or horizontal bar chart for the Safe/Partial/Vulnerable/Critical breakdown — horizontal bars read better than pie charts for 4+ categories

## Things to Avoid
- No decorative gradient backgrounds or "AI-generated" looking accent stripes across headers
- No default Streamlit/Bootstrap look-and-feel left unstyled — at minimum override the default theme colors to match the palette above
- Don't use red/green as the *only* differentiator for risk levels (colorblind accessibility) — pair color with a text label or icon (⚠, ✕, ✓) on every badge

## Reference Inspiration
Security dashboards like GitHub's Security tab (Dependabot alerts) or Snyk's vulnerability dashboard are good visual references for how to present a long list of severity-tagged findings cleanly.
