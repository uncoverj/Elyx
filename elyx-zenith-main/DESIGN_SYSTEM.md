# ELYX Design System v1.0

## 🎨 Brand Identity
**Name:** ELYX — Premium Esports Stats Tracker  
**Tone:** Dark, premium, esports-focused, high-contrast  
**Font stack:** Space Grotesk (display) + Inter (body) + JetBrains Mono (data)  

---

## 🎨 Color Palette

### Core Colors (HSL)
| Token | HSL | Usage |
|-------|-----|-------|
| `--background` | `228 28% 6%` | Main background |
| `--foreground` | `210 40% 96%` | Primary text |
| `--card` | `228 26% 9%` | Card surfaces |
| `--card-hover` | `228 26% 12%` | Card hover state |
| `--primary` | `0 80% 55%` | Valorant red — main accent |
| `--primary-glow` | `0 80% 62%` | Hover/glow state |
| `--accent` | `265 70% 58%` | Purple accent |
| `--secondary` | `228 24% 14%` | Muted surfaces |
| `--muted` | `228 20% 16%` | Muted backgrounds |
| `--muted-foreground` | `220 15% 50%` | Secondary text |
| `--border` | `228 18% 14%` | Borders |

### Semantic Colors
| Token | HSL | Usage |
|-------|-----|-------|
| `--success` | `155 72% 45%` | Wins, positive stats |
| `--destructive` | `0 84% 60%` | Losses, negative |
| `--warning` | `42 95% 55%` | Warnings, gold ranks |
| `--info` | `210 100% 62%` | Telegram, info badges |

### Neon Palette (for agents/roles)
| Token | HSL | Usage |
|-------|-----|-------|
| `--neon-blue` | `210 100% 62%` | Jett, Platinum |
| `--neon-cyan` | `185 100% 55%` | Special effects |
| `--neon-purple` | `265 85% 62%` | Omen, Diamond |
| `--neon-pink` | `330 85% 60%` | Accent gradients |

---

## 📐 Spacing & Grid

**Base unit:** 4px  
**Grid:** 8pt grid system  
**Container:** max-width 1400px, 1rem padding  
**Card padding:** 16px (default), 20-24px (large)  
**Gap between cards:** 12px (tight), 16px (default), 24px (sections)

---

## 🔤 Typography

| Level | Font | Weight | Size | Tracking |
|-------|------|--------|------|----------|
| H1 | Space Grotesk | 700 | 24-28px | -0.02em |
| H2 | Space Grotesk | 700 | 18-20px | -0.02em |
| H3 | Space Grotesk | 700 | 14-16px | -0.01em |
| Body | Inter | 400-500 | 14px | 0 |
| Small | Inter | 500-600 | 11-12px | 0 |
| Micro | Inter | 600-700 | 10px | 0.1-0.15em |
| Data | JetBrains Mono | 400-500 | 12-14px | 0 |
| Label | Inter | 700 | 10px | 0.15em, uppercase |

---

## 🧱 Components

### Glass Card
```css
background: linear-gradient(145deg, hsl(228 26% 11%), hsl(228 26% 8%));
border: 1px solid hsl(228 18% 14% / 0.7);
box-shadow: 0 4px 24px -4px hsl(0 0% 0% / 0.5), inset 0 1px 0 hsl(0 0% 100% / 0.03);
border-radius: 0.875rem;
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

### Pill Button (active)
```css
background: hsl(0 80% 55%);
color: white;
box-shadow: 0 0 12px hsl(0 80% 55% / 0.3);
border-radius: 0.75rem;
font-weight: 700;
font-size: 12px;
```

### Pill Button (inactive)
```css
background: hsl(228 24% 14%);
color: hsl(220 15% 50%);
border-radius: 0.75rem;
```

### Gradient Border
```css
position: relative;
&::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, hsl(0 80% 55%), hsl(330 85% 60%), hsl(265 85% 62%));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  opacity: 0.6;
}
```

### Stat Bar
```css
height: 3px (thin) / 5px (thick);
border-radius: 50%;
background: hsl(228 20% 16% / 0.6);
fill animation: 1.2s cubic-bezier(0.4, 0, 0.2, 1);
```

### Win/Loss Card
```css
/* Win */
border-left: 3px solid hsl(155 72% 45%);
background: linear-gradient(135deg, hsl(155 72% 45% / 0.15), hsl(155 72% 45% / 0.05));

/* Loss */
border-left: 3px solid hsl(0 80% 55%);
background: linear-gradient(135deg, hsl(0 80% 55% / 0.15), hsl(0 80% 55% / 0.05));
```

---

## 🎬 Animations

| Animation | Duration | Easing | Usage |
|-----------|----------|--------|-------|
| fade-in | 0.4s | ease-out | Page elements |
| slide-up | 0.5s | ease-out | Cards entering |
| scale-in | 0.3s | spring(300) | Avatar, badges |
| pulse-glow | 3s infinite | ease-in-out | Active elements |
| stat-bar-fill | 1.2s | cubic-bezier(0.4, 0, 0.2, 1) | Progress bars |
| nav-indicator | spring(400, 28) | - | Navigation |

### Motion principles:
- **Entry:** opacity 0 → 1, translateY(10-20px) → 0
- **Stagger:** 30-80ms between items
- **Hover:** translateY(-1px), shadow increase
- **Spring for layout:** stiffness 300-500, damping 25-30

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | 320-430px | Bottom nav, 2-col stat grid |
| Tablet | 768px+ | 2-col, larger cards |
| Desktop | 1024px+ | Top nav, 4-col stat grid, full-width |

### Mobile specifics:
- Bottom nav with glass blur
- safe-area padding (iOS)
- 44px minimum tap targets
- Horizontal scroll for pills

---

## 🏗 Page Architecture

```
/ (ProfilePage)
├── HeroHeader (banner + avatar + badges)
├── Game pills + Refresh button
├── Rank cards (Current + Peak)
├── Overview stats (4-col grid)
├── Secondary stats (4-col grid)
└── Elyx Score + Trust card

/stats (StatsPage)
├── Header
├── Rank distribution chart
├── Role bars (with progress)
└── Top agents list

/leaderboard (LeaderboardPage)
├── Header + sort toggle
├── Rank distribution chart
└── Leaderboard table

/matches (MatchesPage)
├── Header
├── Filter pills
└── Match groups (by date)
    ├── Date header (with stats)
    └── Match cards

/settings (SettingsPage)
├── Header
├── Connected accounts
└── Game switcher
```

---

## 🔮 v2 Improvements

1. Real agent icons (SVG or images from Valorant API)
2. Animated rank badges with tier-specific effects
3. Match detail page with round-by-round timeline
4. K/D and winrate progression charts (recharts)
5. Skeleton loading states + shimmer effect
6. Pull-to-refresh on mobile
7. Toast notifications for refresh/connect actions
8. Search player functionality
9. Compare players feature
10. Achievement badges system
