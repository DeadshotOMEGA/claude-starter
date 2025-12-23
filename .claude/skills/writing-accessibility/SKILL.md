---
name: writing-accessibility
description: WCAG-compliant accessibility patterns with ARIA, keyboard navigation, and screen reader support. Use when implementing accessible UI components or auditing accessibility.
---

# Writing Accessible UI Components

## WCAG 2.1 AA Compliance Essentials

- **Perceivable**: Information presented in multiple ways (text alternatives, color contrast ratios ≥4.5:1)
- **Operable**: Keyboard navigation, sufficient time for interactions, avoid seizure-inducing content
- **Understandable**: Clear language, predictable navigation, input error prevention
- **Robust**: Valid HTML, proper semantic structure, ARIA used correctly

## ARIA Attributes & Landmarks

**Landmarks** (semantic structure):
```html
<header role="banner">Navigation</header>
<main role="main">Content</main>
<nav role="navigation">Links</nav>
<aside role="complementary">Sidebar</aside>
<footer role="contentinfo">Footer</footer>
```

**Essential ARIA attributes**:
- `aria-label` — Descriptive label for elements without visible text
- `aria-labelledby` — Link to visible heading/label element
- `aria-describedby` — Additional description for complex elements
- `aria-live="polite|assertive"` — Announce dynamic content changes
- `aria-hidden="true"` — Hide decorative elements from screen readers
- `aria-expanded` — Toggle button state (true/false)
- `aria-current="page"` — Indicate current page in navigation

## Keyboard Navigation Patterns

- Tab order follows visual flow (use `tabindex="0"` rarely, never `-1` for interactive elements)
- `Escape` closes modals/dropdowns
- `Enter/Space` activates buttons
- `Arrow keys` navigate menus, tabs, sliders
- Focus trap in modals (trap Tab/Shift+Tab within modal)
- Visible focus indicator (don't remove default `:focus` styles)

## Focus Management

- Set initial focus on modal open: `useEffect(() => { modalRef.current?.focus() }, [])`
- Restore focus on modal close
- Skip repetitive navigation links: `<a href="#main">Skip to content</a>`
- Use `document.activeElement` to detect focus programmatically

## Screen Reader Considerations

- Use semantic HTML (`<button>`, `<form>`, `<input>`, `<select>`)
- Announce form validation errors via `aria-invalid="true"` + `aria-describedby`
- Provide context for icon-only buttons: `<button aria-label="Close menu">×</button>`
- Hide loading spinners from screen readers: `aria-hidden="true"`
- Describe complex data with `aria-label` or hidden text

## Common Component Accessibility Patterns

**Buttons**:
```html
<!-- Icon button with label -->
<button aria-label="Delete item" type="button">🗑️</button>

<!-- Toggle button -->
<button aria-pressed="false" aria-label="Mute audio">🔊</button>
```

**Forms**:
```html
<label htmlFor="email">Email</label>
<input id="email" type="email" aria-required="true" />
<span id="error" role="alert">Invalid format</span>
```

**Modals**:
```html
<div role="dialog" aria-labelledby="title" aria-modal="true">
  <h1 id="title">Confirm Action</h1>
  <p>Are you sure?</p>
</div>
```

**Menus/Dropdowns**:
```html
<button aria-haspopup="menu" aria-expanded="false">Menu</button>
<ul role="menu" hidden>
  <li role="menuitem">Option 1</li>
</ul>
```

**Tabs**:
```html
<div role="tablist">
  <button role="tab" aria-selected="true" aria-controls="panel1">Tab 1</button>
  <div id="panel1" role="tabpanel" aria-labelledby="tab1">Content</div>
</div>
```

## Testing & Validation

- Use axe DevTools or WAVE browser extensions
- Test with screen readers (NVDA, JAWS, VoiceOver)
- Verify keyboard-only navigation works end-to-end
- Check color contrast with contrast checker tools
- Test with Playwright accessibility tests
