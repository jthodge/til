# `grid-area`

## `grid-template-areas`

Allows you to define your layout in a pseudo-visual manner, e.g.:

```css
grid-template-areas:
  "header header"
  "sidebar content"
  "footer footer";
```

## 1. Define Markup

```html
<div class="grid">
    <div class="header"></div>
    <div class="sidebar"></div>
    <div class="content"></div>
    <div class="footer"></div>
</div>
```

## 2. Define Areas

```css
.grid {
    display: grid;
    grid-template-areas:
        "header header"
        "sidebar content"
        "footer footer";
}
```

## 3. Set Areas

```css
.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.content { grid-area: content; }
.footer { grid-area: footer; }
```
