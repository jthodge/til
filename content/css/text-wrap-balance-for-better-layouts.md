# `text-wrap: balance` for Better Layouts

`text-wrap: balance` prevents awkward single-word lines in headings and can be creatively applied to icons and navigation elements for more visually pleasing layouts.

## Basic Usage

The property automatically balances text across multiple lines to avoid orphaned words:

```css
/* Before: awkward single word on last line */
h1 {
  width: 200px;
}
/* "This is a very long heading that wraps"
   → "This is a very long heading that"
   → "wraps" (orphaned) */

/* After: balanced distribution */
h1 {
  width: 200px;
  text-wrap: balance;
}
/* "This is a very long heading that wraps"
   → "This is a very long"
   → "heading that wraps" (balanced) */
```

## Practical Examples

### Headlines and Captions

```css
.article-title {
  text-wrap: balance;
  max-width: 600px;
  font-size: 2.5rem;
  line-height: 1.2;
}

.image-caption {
  text-wrap: balance;
  max-width: 400px;
  font-size: 0.9rem;
  color: #666;
}

.blockquote-text {
  text-wrap: balance;
  font-style: italic;
  max-width: 500px;
}
```

### Navigation Menus

Balance navigation items across multiple lines:

```css
.navigation-menu {
  display: flex;
  flex-wrap: wrap;
  text-wrap: balance;
  max-width: 300px;
}

.nav-item {
  padding: 0.5rem 1rem;
  white-space: nowrap;
}
```

```html
<nav class="navigation-menu">
  <a href="#" class="nav-item">Home</a>
  <a href="#" class="nav-item">Products</a>
  <a href="#" class="nav-item">Services</a>
  <a href="#" class="nav-item">About</a>
  <a href="#" class="nav-item">Contact</a>
</nav>
```

## Creative Applications with Icons

### Icon Grid Layouts

Apply to containers with icons and labels for better distribution:

```css
.icon-grid {
  display: flex;
  flex-wrap: wrap;
  text-wrap: balance;
  max-width: 400px;
  gap: 1rem;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  text-align: center;
  min-width: 80px;
}

.icon-item svg {
  width: 32px;
  height: 32px;
  margin-bottom: 0.5rem;
}
```

```html
<div class="icon-grid">
  <div class="icon-item">
    <svg><!-- email icon --></svg>
    <span>Email</span>
  </div>
  <div class="icon-item">
    <svg><!-- calendar icon --></svg>
    <span>Calendar</span>
  </div>
  <div class="icon-item">
    <svg><!-- documents icon --></svg>
    <span>Documents</span>
  </div>
  <div class="icon-item">
    <svg><!-- settings icon --></svg>
    <span>Settings</span>
  </div>
</div>
```

### Social Media Links

Balance social media icons across multiple rows:

```css
.social-links {
  display: flex;
  flex-wrap: wrap;
  text-wrap: balance;
  max-width: 200px;
  gap: 0.75rem;
  justify-content: center;
}

.social-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 0.25rem;
  background: #f5f5f5;
  text-decoration: none;
}
```

## Important Limitations

### Line Count Restrictions

```css
/* Won't work: too many lines */
.long-content {
  text-wrap: balance; /* Ignored for content > 6-10 lines */
}

/* Works: short content */
.short-headline {
  text-wrap: balance; /* Perfect for 2-5 lines */
}
```

### Performance Considerations

```css
/* Avoid on body text */
p {
  text-wrap: balance; /* Computationally expensive for long text */
}

/* Good for headings and short content */
h1, h2, h3, figcaption, .card-title {
  text-wrap: balance;
}
```

## Browser Support and Fallbacks

```css
/* Progressive enhancement approach */
.balanced-heading {
  /* Base styles work everywhere */
  max-width: 600px;
  line-height: 1.3;
}

/* Modern browsers get the enhancement */
@supports (text-wrap: balance) {
  .balanced-heading {
    text-wrap: balance;
  }
}

/* Alternative for older browsers */
@supports not (text-wrap: balance) {
  .balanced-heading {
    /* Maybe use a slightly larger line-height */
    line-height: 1.4;
  }
}
```

## Real-World Implementation

### Card Components

```css
.feature-card {
  max-width: 300px;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.feature-card h3 {
  text-wrap: balance;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.feature-card p {
  /* Don't use balance on longer descriptions */
  line-height: 1.6;
}
```

### Dashboard Widgets

```css
.widget-title {
  text-wrap: balance;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  max-width: 250px;
}

.stat-label {
  text-wrap: balance;
  font-size: 0.875rem;
  color: #666;
  max-width: 120px;
}
```

## Best Practices

1. **Use for short text blocks** - Headlines, captions, labels, navigation items
2. **Avoid for body text** - Performance impact and line limits make it unsuitable
3. **Test across browsers** - Behavior may vary between Chrome (6 lines) and Firefox (10 lines)
4. **Combine with max-width** - Control where text wrapping occurs
5. **Progressive enhancement** - Use `@supports` for graceful fallbacks

