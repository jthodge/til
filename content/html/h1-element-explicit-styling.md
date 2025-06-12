# `<h1>` Element Explicit Styling

Browsers are removing automatic font-size scaling for nested `<h1>` elements.
Moving forward, always explicitly define `font-size` and `margin` for `<h1>` elements to ensure consistent styling and avoid deprecation warnings.

## The Change

Previously, browsers would automatically scale `<h1>`  font sizes based on sectioning context:

```html
<!-- Old behavior: progressively smaller H1s -->
<body>
  <h1>Main Title (2em)</h1>
  <article>
    <h1>Article Title (1.5em)</h1>
    <section>
      <h1>Section Title (1.17em)</h1>
      <section>
        <h1>Subsection (1em)</h1>
      </section>
    </section>
  </article>
</body>
```

Now all `<h1>` elements will have the same default styling regardless of nesting depth.

## Recommended Solution

Always explicitly style `<h1>` elements:

```css
h1 {
  margin-block: 0.67em;
  font-size: 2em;
  font-weight: bold;
}

/* Or create specific classes for different contexts */
.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 2rem;
  line-height: 1.2;
}

.article-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  line-height: 1.3;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  line-height: 1.4;
}
```

## Proper Semantic Structure

Instead of relying on automatic `<h1>` scaling, use proper heading hierarchy:

```html
<!-- Correct: Use proper heading levels -->
<body>
  <h1>Main Page Title</h1>
  <article>
    <h2>Article Title</h2>
    <section>
      <h3>Section Title</h3>
      <section>
        <h4>Subsection Title</h4>
      </section>
    </section>
  </article>
</body>
```

```css
/* Style each heading level appropriately */
h1 { font-size: 2.5rem; font-weight: 800; }
h2 { font-size: 2rem; font-weight: 700; }
h3 { font-size: 1.5rem; font-weight: 600; }
h4 { font-size: 1.25rem; font-weight: 600; }
h5 { font-size: 1.125rem; font-weight: 500; }
h6 { font-size: 1rem; font-weight: 500; }
```

## Context-Specific Styling

Create explicit styles for different page contexts:

```css
/* Homepage hero */
.hero h1 {
  font-size: clamp(2.5rem, 8vw, 4rem);
  font-weight: 900;
  margin-bottom: 1.5rem;
  line-height: 1.1;
}

/* Blog post titles */
.blog-post h1 {
  font-size: 2.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.25;
  color: #1a1a1a;
}

/* Card titles */
.card h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  line-height: 1.3;
}

/* Modal titles */
.modal h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  line-height: 1.3;
}
```

## Design System Integration

Define H1 styles as part of your design system:

```css
/* Design system typography */
:root {
  --font-size-h1-hero: 4rem;
  --font-size-h1-page: 2.5rem;
  --font-size-h1-section: 2rem;
  --font-size-h1-card: 1.5rem;

  --font-weight-bold: 700;
  --font-weight-black: 900;

  --line-height-tight: 1.1;
  --line-height-normal: 1.25;
}

.h1-hero {
  font-size: var(--font-size-h1-hero);
  font-weight: var(--font-weight-black);
  line-height: var(--line-height-tight);
}

.h1-page {
  font-size: var(--font-size-h1-page);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-normal);
}

.h1-section {
  font-size: var(--font-size-h1-section);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-normal);
}
```

## Responsive H1 Styling

Use responsive techniques for better mobile experience:

```css
h1 {
  /* Fluid typography */
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: clamp(1rem, 3vw, 2rem);
}

/* Breakpoint-specific adjustments */
@media (max-width: 768px) {
  h1 {
    font-size: 1.75rem;
    line-height: 1.25;
    margin-bottom: 1rem;
  }
}

@media (min-width: 1200px) {
  h1 {
    font-size: 3rem;
    line-height: 1.1;
    margin-bottom: 2rem;
  }
}
```

## Migration Strategy

If you have existing sites that might be affected:

```css
/* 1. Add explicit styles to maintain current appearance */
h1 {
  font-size: 2em;
  margin-block: 0.67em;
  font-weight: bold;
}

/* 2. Override for specific contexts if needed */
article h1,
section h1,
aside h1,
nav h1 {
  font-size: 1.5em; /* Adjust based on your design needs */
}

/* 3. Gradually migrate to semantic heading structure */
.legacy-h1-large { font-size: 2em; }
.legacy-h1-medium { font-size: 1.5em; }
.legacy-h1-small { font-size: 1.17em; }
```

## Accessibility Benefits

Explicit styling improves accessibility by:

1. **Clear hierarchy**: Proper heading levels help screen readers navigate
2. **Consistent experience**: Users get predictable heading sizes
3. **Better SEO**: Search engines understand document structure better

```html
<!-- Clear document outline -->
<h1>Page Title</h1>
  <h2>Main Section</h2>
    <h3>Subsection</h3>
    <h3>Another Subsection</h3>
  <h2>Another Main Section</h2>
    <h3>Subsection</h3>
```
