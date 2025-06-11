# Regex-Flavored Attribute Selectors in CSS

CSS supports attribute selectors that work similarly to regex anchors. This allows pattern matching on attribute values, but without full regex support.

## The Three Operators

- `^=` matches attributes that **start with** a value (like `^` in regex)
- `*=` matches attributes that **contain** a value (like `.*` in regex)
- `$=` matches attributes that **end with** a value (like `$` in regex)

## Examples

```css
/* Select all links to secure sites */
a[href^="https://"] {
  color: green;
  padding-left: 20px;
  background: url('secure-icon.svg') no-repeat left center;
}

/* Select all images with 'thumbnail' anywhere in the alt text */
img[alt*="thumbnail"] {
  border: 2px solid #ccc;
  max-width: 150px;
}

/* Select all documents ending with .pdf */
a[href$=".pdf"] {
  padding-right: 25px;
  background: url('pdf-icon.svg') no-repeat right center;
}
```

## Practical Use Cases

### File Type Indicators

```css
/* Style different file types */
a[href$=".doc"], a[href$=".docx"] {
  color: #2b579a;
}

a[href$=".xls"], a[href$=".xlsx"] {
  color: #217346;
}

a[href$=".zip"], a[href$=".rar"] {
  color: #8b4513;
}
```

### Form Validation Hints

```css
/* Highlight email inputs */
input[type="email"],
input[name*="email"] {
  background-color: #f0f8ff;
}

/* Style inputs with specific data attributes */
input[data-validate^="required"] {
  border-left: 3px solid #ff6b6b;
}
```

### Language-Specific Styling

```css
/* Style elements by language */
[lang^="en"] {
  quotes: """ """ "'" "'";
}

[lang^="fr"] {
  quotes: "« " " »" "‹ " " ›";
}
```

## Combining Selectors

```css
/* External links that aren't secure */
a[href^="http://"][href*="external"] {
  color: orange;
  text-decoration: underline wavy;
}

/* Development environment links */
a[href^="http://"][href*="localhost"],
a[href^="http://"][href$=".local"] {
  outline: 2px dashed red;
}
```

