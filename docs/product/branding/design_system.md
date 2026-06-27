# Sentinel Design System

## Design Tokens

### Spacing Scale
| Token | Value | Rem | Usage |
| :--- | :--- | :--- | :--- |
| `space-1` | 4px | `0.25rem` | Between tight inline elements |
| `space-2` | 8px | `0.5rem` | Standard inner padding for small chips |
| `space-4` | 16px | `1rem` | Standard padding for cards, margins |
| `space-6` | 24px | `1.5rem` | Section gaps within panels |
| `space-8` | 32px | `2rem` | Major layout gutters |

### Typography Scale
| Token | Size | Line Height | Usage |
| :--- | :--- | :--- | :--- |
| `text-xs` | 12px | 16px | Overlines, dense table cells |
| `text-sm` | 14px | 20px | Standard body text, secondary labels |
| `text-base`| 16px | 24px | Primary text, regular inputs |
| `text-lg` | 18px | 28px | Card headings, panel titles |
| `text-xl` | 20px | 28px | Sub-section headers |
| `text-2xl` | 24px | 32px | Main page headings |

## Core Components

### Cards (Panels)
Cards are the fundamental unit of the Mission Control layout.
- **Background:** `surface-dark` (`#111827`)
- **Border:** `1px solid #1F2937`
- **Border Radius:** `4px`
- **Padding:** `16px` (`space-4`)
- **Header:** Uppercase, `text-xs`, bold, muted text, bottom border separating header from content.

### Buttons
Buttons should feel tactical and precise.
- **Primary:** Background `#3B82F6`, Text `#FFFFFF`, Hover `#2563EB`.
- **Secondary / Ghost:** Background transparent, Border `1px solid #374151`, Text `#D1D5DB`, Hover background `#1F2937`.
- **Destructive:** Background `#DC2626`, Text `#FFFFFF`.
- **Size:** Height `32px` for dense UI, `40px` for standard.

### Status Chips & Severity Colors
Used extensively in Compliance and Risk panels to denote system state.

| State | Background | Text Color | Border |
| :--- | :--- | :--- | :--- |
| **Normal / Safe** | `#064E3B` (Dark Emerald) | `#34D399` | `#047857` |
| **Warning / Elevated** | `#78350F` (Dark Amber) | `#FBBF24` | `#B45309` |
| **Critical / Danger** | `#7F1D1D` (Dark Red) | `#F87171` | `#B91C1C` |
| **Offline / Unknown** | `#1F2937` (Dark Gray) | `#9CA3AF` | `#374151` |
| **Active / Info** | `#1E3A8A` (Dark Blue) | `#60A5FA` | `#1D4ED8` |

### Data Tables
Tables are optimized for massive datasets.
- **Header Row:** Muted background (`#1F2937`), `text-xs` uppercase.
- **Row Height:** Dense (`32px` height).
- **Dividers:** Subtle bottom border (`#374151`) on every row.
- **Hover:** Entire row highlights to `#111827` slightly lighter shade to aid tracking across wide screens.
