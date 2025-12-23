---
name: writing-tailwind
description: Utility-first CSS with Tailwind patterns, responsive design, and theming. Use when styling components with Tailwind CSS or implementing responsive layouts.
---

# Tailwind CSS Writing Guide

Write efficient, maintainable styling with Tailwind's utility-first approach.

## Philosophy

Tailwind CSS uses utility classes instead of component classes:
- Compose styles directly in markup
- Avoid custom CSS files for common patterns
- Extract repeated patterns into components or `@apply` rules
- Build consistency through design tokens

## Responsive Design

Mobile-first breakpoints using Tailwind prefixes:

```html
<!-- Mobile: base styles, then override at breakpoints -->
<div class="w-full md:w-1/2 lg:w-1/3 xl:w-1/4">
  Mobile full width → Tablet 50% → Desktop 33% → XL 25%
</div>

<!-- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px) -->
```

## Common Component Patterns

### Buttons

```html
<!-- Primary button -->
<button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
  Click me
</button>

<!-- Secondary button -->
<button class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
  Cancel
</button>
```

### Cards

```html
<div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
  <h3 class="text-lg font-semibold mb-2">Card Title</h3>
  <p class="text-gray-600">Card content</p>
</div>
```

### Forms

```html
<input
  type="text"
  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
  placeholder="Enter text"
/>
```

### Layouts

```html
<!-- Flex container: space-between, center alignment -->
<div class="flex items-center justify-between gap-4">
  <div>Left item</div>
  <div>Right item</div>
</div>

<!-- Grid: responsive columns -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

## Theming & Dark Mode

Enable dark mode in `tailwind.config.js`:

```javascript
module.exports = {
  darkMode: 'class',
  // ...
}
```

Use `dark:` prefix for dark mode styles:

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Content adapts to theme
</div>
```

## Best Practices

- Use consistent spacing scale (gap, padding, margin)
- Leverage color palette from config for consistency
- Extract repeated patterns into component classes with `@apply`
- Keep utility chains readable (break into multiple lines if needed)
- Use semantic color tokens (e.g., `text-destructive` vs `text-red-600`)
