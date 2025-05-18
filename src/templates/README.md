# TIL Templates Documentation

This directory contains the Jinja2 templates used by the TIL application.

## Template Hierarchy

```
base.html                    # Root template with HTML structure
├── til_base.html           # Extends base, provides TIL-specific structure
    ├── index.html          # Homepage
    ├── query-til-search.html # Search results page
    └── pages/
        ├── all.html        # All TILs listing
        ├── {topic}.html    # Topic-specific listing
        ├── {topic}/{slug}.html # Individual TIL page
        └── tools/
            └── render-markdown.html # Markdown rendering tool
```

## Components

The `components/` directory contains reusable template fragments:

- `feed_icon.html` - RSS/Atom feed icon
- `til_item.html` - Single TIL item display
- `topic_list.html` - Topic listing

## Configuration

- `site_config.html` - Global site configuration and variables
- `macros.html` - Jinja2 macros for common patterns

## Template Features

### Blocks

The template system provides several blocks for customization:

- `title` - Page title
- `meta` - Meta tags
- `stylesheets` - CSS includes
- `extra_head` - Additional head elements
- `header` - Page header
- `navigation` - Navigation area
- `content` - Main content area
- `footer` - Page footer
- `scripts` - JavaScript includes

### Usage Examples

#### Including a component:
```jinja2
{% include "components/feed_icon.html" %}
```

#### Using macros:
```jinja2
{% import "macros.html" as macros %}
{{ macros.meta_tags(title="My Page", description="Description") }}
```

#### Extending templates:
```jinja2
{% extends "til_base.html" %}
{% block title %}My Page Title{% endblock %}
```

## CSS Organization

- `/static/til-base.css` - Base styles
- `/static/components.css` - Component-specific styles
- `/static/forms.css` - Form styles
- `/static/search.css` - Search functionality styles
- `/static/github-light.css` - Code highlighting styles