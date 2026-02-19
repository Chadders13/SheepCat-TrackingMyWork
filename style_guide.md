# SheepCat Brand & Style Guide

> **Audience:** Designers, developers, and contributors working on the SheepCat website and product.  
> **Last updated:** 2026

---

## Table of Contents

1. [Brand Identity](#1-brand-identity)
2. [Colour Palette](#2-colour-palette)
3. [Typography](#3-typography)
4. [Logo Usage](#4-logo-usage)
5. [Glass-Effect Design System](#5-glass-effect-design-system)
6. [Components](#6-components)
7. [Accessibility Standards](#7-accessibility-standards)
8. [Writing Style](#8-writing-style)
9. [Spacing & Layout](#9-spacing--layout)
10. [Icons & Emoji](#10-icons--emoji)

---

## 1. Brand Identity

**SheepCat** is a gentle, neurodivergent-friendly productivity tool. Our brand voice combines:

| Trait | What it means in practice |
|-------|---------------------------|
| **Calm** | Soft tones, no harsh alerts, gentle language |
| **Professional** | Clean layouts, consistent spacing, clear hierarchy |
| **Inclusive** | Accessible colours, screen-reader support, plain English |
| **Sophisticated** | Glass-effect UI, subtle gradients, refined typography |

### Brand values

- **Privacy first** — data stays local, always.
- **Neurodivergent by design** — not an afterthought.
- **Open source with commercial freedom** — AGPLv3 + optional commercial licence.

---

## 2. Colour Palette

All colour values are CSS custom properties defined in `docs/styles.css`.

### Background gradient

The page background uses a fixed three-stop gradient that gives depth to glass cards.

| Stop | Hex | Name |
|------|-----|------|
| 0 % | `#1e1b4b` | Deep Indigo Night |
| 50 % | `#312e81` | Indigo |
| 100 % | `#0f172a` | Slate Dark |

### Brand & UI colours

| Token | Hex | Usage |
|-------|-----|-------|
| `--primary` | `#818cf8` | Buttons, links, step numbers, accents |
| `--primary-d` | `#6366f1` | Hover state for primary elements |
| `--primary-glow` | `rgba(99,102,241,0.45)` | Drop-shadow / glow on interactive elements |
| `--accent` | `#fb923c` | Warm accent (use sparingly) |
| `--green` | `#4ade80` | Success states, tick icons |
| `--green-bg` | `rgba(74,222,128,0.12)` | Success card backgrounds |
| `--green-bd` | `rgba(74,222,128,0.30)` | Success card borders |

### Text colours

| Token | Hex | Contrast on dark bg | Usage |
|-------|-----|---------------------|-------|
| `--text` | `#f1f5f9` | ≈ 15 : 1 (AAA) | Primary body copy, headings |
| `--muted` | `#94a3b8` | ≈ 5 : 1 (AA) | Secondary / descriptive copy |

### Glass surface colours

| Token | Value | Usage |
|-------|-------|-------|
| `--glass-bg` | `rgba(255,255,255,0.08)` | Card resting state |
| `--glass-bg-hov` | `rgba(255,255,255,0.13)` | Card hover state |
| `--glass-bd` | `rgba(255,255,255,0.18)` | Card borders |
| `--glass-shadow` | `0 8px 32px rgba(0,0,0,0.35)` | Card box-shadows |

> ⚠️ **Never** place `--muted` text on a light background — it only meets contrast requirements against the dark gradient.

---

## 3. Typography

| Role | Font stack | Weight | Size |
|------|-----------|--------|------|
| Body | `'Segoe UI', system-ui, -apple-system, sans-serif` | 400 | `1rem` / `16px` |
| Headings | Same as body | 800 | `clamp(2rem, 5vw, 3.4rem)` (h1) · `1.9rem` (h2) |
| Sub-headings | Same as body | 700 | `1.05rem` |
| Muted / labels | Same as body | 400 | `0.85–0.95rem` |
| Code | `'Consolas', 'Fira Code', 'Courier New', monospace` | 400 | `0.9em` |

### Line height

- **Body text:** `1.65` — generous leading helps readers with dyslexia and ADHD.
- **Headings:** `1.15` — tighter for visual impact.

### Do's and don'ts

✅ Use `clamp()` for fluid heading sizes.  
✅ Keep paragraph widths ≤ 680 px (optimal reading measure).  
✅ Use `font-weight: 700` or `800` for headings — never `600` or less.  
❌ Don't use italics for long passages — reserve for short emphasis only.  
❌ Don't set body copy smaller than `0.875rem` (14 px).

---

## 4. Logo Usage

The SheepCat logo is stored at `docs/logo.png` — the official circular badge artwork:

- **Shape:** Circular badge with a solid white background enclosed by a thick bold blue border (1:1 aspect ratio).
- **Central mascot:** Cartoon-style tabby cat with brown, black, and ginger stripes, yellow-green eyes, and a confident mischievous smirk.
- **Wool hood:** Thick fluffy cream-coloured sheep's wool hood framing the face, with two large curled light-brown ram's horns emerging from the sides.
- **Clothing:** Bright blue high-visibility hoodie with bright yellow reflective safety stripes on the shoulders and arms.
- **Props:** The cat sits behind a minimalist desk line with paws on a dark grey laptop (white circular logo on the lid).
- **Typography:** "SheepCat" in large bold rounded blue sans-serif below the desk; "Tracking My Work" tagline in smaller matching blue beneath.
- **Colour palette:** Primary Blue (outer ring, hoodie, text) · Accent Yellow (hi-vis stripes, eyes) · Earth tones (tabby fur, cream wool, light-brown horns) · White background.

**Suggested alt text:**
```
alt="SheepCat logo: A tabby cat wearing a sheep's wool hood with ram horns and a blue high-vis hoodie, working on a laptop, with the text 'SheepCat - Tracking My Work'"
```

### Sizes

| Context | Recommended size |
|---------|-----------------|
| Navigation bar | 36 × 36 px |
| Hero / page header | 100 × 100 px |
| Favicon (future) | 32 × 32 px |
| Social / OG image (future) | 512 × 512 px |

### Clear space

Maintain a minimum clear space of **0.5× the logo height** on all sides.

### Do's and don'ts

✅ Always include `alt=""` when the logo is decorative (nav) with a visible text label nearby.  
✅ Include `alt="SheepCat logo"` when the logo stands alone (hero).  
✅ Apply `filter: drop-shadow(...)` for the characteristic indigo glow effect.  
❌ Don't stretch or skew the SVG — set only `width` or `height`, not both.  
❌ Don't recolour the logo without checking contrast on the destination background.  
❌ Don't display the logo smaller than 24 × 24 px.

---

## 5. Glass-Effect Design System

### What is glassmorphism?

Glassmorphism gives UI elements the appearance of frosted glass floating over a colourful background. Key CSS properties:

```css
/* Glass card */
background: rgba(255, 255, 255, 0.08);
backdrop-filter: blur(20px) saturate(180%);
-webkit-backdrop-filter: blur(20px) saturate(180%);
border: 1px solid rgba(255, 255, 255, 0.18);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
border-radius: 16px;
```

### The three glass levels

| Level | Background opacity | Blur | Usage |
|-------|--------------------|------|-------|
| **Subtle** | `rgba(255,255,255,0.04)` | `blur(12px)` | Section dividers, alt-bg |
| **Standard** | `rgba(255,255,255,0.08)` | `blur(16–20px)` | Feature cards, who-cards |
| **Strong** | `rgba(255,255,255,0.13)` | `blur(24px)` | Pricing plans, success card |

### Hover states

On hover, increase `background` opacity by one level and add a subtle `transform: translateY(-3px)`. Never remove the border.

### Reduced-motion support

The `@media (prefers-reduced-motion: reduce)` block in `styles.css` disables all transitions and the logo float animation. **Always** respect this preference — it is critical for users with vestibular disorders.

---

## 6. Components

### Buttons

| Class | Style | Use for |
|-------|-------|---------|
| `.btn-primary` | Solid indigo fill | Primary CTAs |
| `.btn-outline` | Semi-transparent glass + white border | Secondary actions |
| `.btn-white` | White fill, indigo text | CTAs on the indigo CTA band |
| `.btn-pay` | Same as `.btn-primary` | Payment page buy buttons |
| `.btn-pay.outline` | Glass + indigo border | Secondary payment option |

**Minimum touch target:** 44 × 44 px (WCAG 2.5.5 AAA guideline).

### Cards (`.feature-card`, `.who-card`, `.plan-card`)

- **Resting:** `--glass-bg`, `--glass-bd` border, no shadow.
- **Hover:** `--glass-bg-hov`, drop-shadow, `translateY(-3px)`.
- **Focus-visible:** 3 px indigo outline via the global `*:focus-visible` rule.

### Step numbers (`.step-num`)

Circular badges with `--primary` background and an indigo glow (`box-shadow: 0 0 18px var(--primary-glow)`). Minimum size 2.4 rem to maintain legibility.

### Navigation

The nav is `position: sticky` with a heavily blurred background (`blur(20px)`) so page content reads through it as the user scrolls.

---

## 7. Accessibility Standards

SheepCat targets **WCAG 2.1 Level AA** compliance. The following rules are non-negotiable.

### Colour contrast

| Pair | Ratio | Level |
|------|-------|-------|
| `#f1f5f9` on dark gradient | ≈ 15 : 1 | AAA |
| `#94a3b8` on dark gradient | ≈ 5 : 1 | AA |
| `#818cf8` on dark gradient (large text) | ≈ 4.6 : 1 | AA |
| White `#fff` on `#4f46e5` (btn-white text) | ≈ 7 : 1 | AAA |

### Keyboard navigation

- All interactive elements must be reachable and operable by keyboard alone.
- The global `*:focus-visible` rule provides a **3 px indigo outline** on focus — never suppress this with `outline: none` without providing a custom equivalent.

### Screen readers

- Decorative logo instances use `aria-hidden="true"` and an empty `alt=""`.
- Informational logo instances use `alt="SheepCat logo"`.
- The confetti wrapper has `aria-hidden="true"` — it conveys no information.
- The SVG root element includes `role="img"` and `aria-label="SheepCat"` with an inner `<title>` element.

### Motion sensitivity

All animations are disabled via `@media (prefers-reduced-motion: reduce)`. This includes:
- The hero logo float animation.
- Button hover `transform` transitions.
- Card lift transitions.
- Confetti fall animation.

### Semantic HTML

- Use `<section>` with a heading for page regions.
- Use `<nav>` for the navigation bar.
- Use `<main>` for the primary content area.
- Use `<footer>` for footer content.
- Use `<table>` with `<thead>`, `<tbody>`, and `<th scope>` for data tables.

### Language

- The `<html>` element must always include `lang="en"`.
- Plain English: short sentences, active voice, no jargon.

---

## 8. Writing Style

### Voice & tone

| Situation | Tone |
|-----------|------|
| Feature descriptions | Warm, reassuring, direct |
| Legal/licence copy | Clear, precise, no jargon |
| Error messages | Calm, constructive, solution-focused |
| CTAs | Confident, specific (e.g. "Subscribe for £8.99/yr" not just "Buy") |

### Grammar rules

- **UK English** throughout (`colour`, `licence`, `customisable`).
- Use em dashes (—) for parenthetical asides, not hyphens.
- Use an en dash (–) for ranges (e.g. `£8.99–£15.99`).
- Capitalise proper nouns: *SheepCat*, *AGPLv3*, *Ollama*, *GitHub*.
- Spell out numbers one through nine; use numerals for 10 and above.
- Don't use exclamation marks excessively — reserve for genuine celebration moments (e.g. the success page).

### Headings

- Page `<h1>`: unique, descriptive, ≤ 60 characters.
- Section `<h2>`: clear topic, title case.
- Card/step `<h3>` / `<h4>`: sentence case, concise.

---

## 9. Spacing & Layout

### Base unit

All spacing is based on a **0.25 rem (4 px)** grid.

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | `0.25rem` | Tight inline gaps |
| `sm` | `0.5rem` | Padding on small elements |
| `md` | `1rem` | Standard padding / gap |
| `lg` | `1.5rem` | Card padding, section gaps |
| `xl` | `2.5rem` | Section vertical padding |
| `2xl` | `4.5rem` | Hero/section padding |

### Max widths

| Context | Max width |
|---------|-----------|
| Section inner content | `1080px` |
| Licence / pricing section | `860px` |
| Reading-optimised text (steps, FAQs) | `680–720px` |
| Success card | `560px` |
| Readable paragraph | `600px` |

### Responsive breakpoints

| Breakpoint | Width | Change |
|-----------|-------|--------|
| Mobile | < 640 px | Single-column licence grid |
| Tablet | 640–1080 px | Auto-fit grid columns |
| Desktop | > 1080 px | Full grid, max-width containers |

---

## 10. Icons & Emoji

SheepCat uses Unicode emoji for icons throughout the site. This avoids external icon-library dependencies and works across all platforms.

### Approved icon set

| Emoji | Meaning |
|-------|---------|
| 🧠 | ADHD / brain / AI |
| 🌈 | Autism / diversity |
| 📖 | Dyslexia / reading |
| 💡 | Dyspraxia / ideas |
| ⚡ | Anxiety / speed |
| 🔄 | Working memory / cycles |
| ⏰ | Interval check-ins / time |
| 🤖 | AI summaries |
| 📋 | Work log |
| 🔒 | Privacy / security |
| 🗂️ | Session management |
| 🧩 | Modular architecture |
| 🔑 | Licence / key |
| ✓ (text) | Feature list tick |
| ✗ (text) | Feature list cross |
| 💙 | Brand heart (footer only) |

### Usage rules

- Emoji in headings: place **before** the heading text for visual anchoring (e.g. `🔑 What does the licence cover?`).
- Emoji in copy: use sparingly — no more than one per sentence.
- Always provide textual equivalents — never rely on emoji alone to convey meaning.
- Don't use emoji for decorative flair in places where they may distract readers with sensory sensitivities.

---

*This style guide is a living document. Submit suggestions via the [GitHub repository](https://github.com/Chadders13/SheepCat-TrackingMyWork-Website).*