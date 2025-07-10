# Transform Origin Changes Animation Behavior

`transform-origin` property defines anchor point for CSS transforms.

By default, transformations occur around an element's center, but changing this origin point creates completely different animation effects.

## Default Center Origin

All transforms default to the element's center (`50% 50%`):

```css
.element {
  /* Rotates around center */
  transform: rotate(45deg);
  /* transform-origin: 50% 50%; (default) */
}
```

## Changing the Origin Point

Set a different anchor point to change how transformations behave:

```css
/* E.g. door opening animation */
.door {
  transform-origin: left center;
  transition: transform 0.3s ease;
}

.door:hover {
  transform: rotateY(-60deg);
}

/* E.g. notification badge pulse */
.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 12px;
  height: 12px;
  background: red;
  border-radius: 50%;
  transform-origin: center center;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.3);
  }
}

/* Change origin for different effect */
.notification-badge--corner {
  transform-origin: top right;
  /* Now pulses from top-right corner instead of center */
}
```

## Practical Applications

### Card Flip Effect

```css
.card-container {
  perspective: 1000px;
}

.card {
  transform-style: preserve-3d;
  transition: transform 0.6s;
  transform-origin: center center;
}

.card.flipped {
  transform: rotateY(180deg);
}

/* Alternative: flip from edge */
.card--edge-flip {
  transform-origin: right center;
  /* Creates a page-turning effect */
}
```

### Dropdown Menu Animation

```css
.dropdown-menu {
  transform-origin: top center;
  transform: scaleY(0);
  opacity: 0;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.dropdown-menu.open {
  transform: scaleY(1);
  opacity: 1;
}

/* Alternative origins for different effects */
.dropdown-menu--from-corner {
  transform-origin: top left;
  transform: scale(0);
}

.dropdown-menu--from-bottom {
  transform-origin: bottom center;
  /* Grows upward instead of downward */
}
```

## Multiple Transform Origins

```css
/* Loading spinner with offset rotation */
.spinner-dot {
  width: 8px;
  height: 8px;
  background: currentColor;
  border-radius: 50%;
  transform-origin: 20px center; /* Offset from center */
  animation: orbit 1.5s linear infinite;
}

@keyframes orbit {
  to {
    transform: rotate(360deg);
  }
}

/* Create multiple dots with delays */
.spinner-dot:nth-child(2) {
  animation-delay: 0.15s;
}
.spinner-dot:nth-child(3) {
  animation-delay: 0.3s;
}
```

## Common Origin Values

```css
/* Keywords */
transform-origin: top left;
transform-origin: center bottom;
transform-origin: right center;

/* Percentages */
transform-origin: 0% 0%;     /* top left */
transform-origin: 100% 100%; /* bottom right */
transform-origin: 25% 75%;   /* custom point */

/* Length values */
transform-origin: 10px 20px;
transform-origin: -5px center;

/* 3D transforms can use three values */
transform-origin: left center -50px;
```

## Real-World Examples

### Tooltip Arrow Rotation

```css
.tooltip {
  position: relative;
}

.tooltip::after {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  width: 10px;
  height: 10px;
  background: inherit;
  transform: rotate(45deg);
  transform-origin: center center;
}

/* Adjust origin for different arrow positions */
.tooltip--left::after {
  left: auto;
  right: -5px;
  bottom: 50%;
  transform-origin: top right;
}
```

### Accordion Collapse

```css
.accordion-content {
  overflow: hidden;
  transform-origin: top center;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.accordion-content.collapsed {
  transform: scaleY(0);
  opacity: 0;
}

/* Alternative: slide and fade from side */
.accordion-content--slide {
  transform-origin: left center;
}

.accordion-content--slide.collapsed {
  transform: scaleX(0) translateX(-20px);
}
```

## Performance Tips

1. **Avoid animating transform-origin itself** - it can cause janky animations
2. **Set origin before animating** - don't change it during the animation
3. **Use with transform** - transform-origin only affects transform properties
4. **Consider will-change** - for frequently animated elements

