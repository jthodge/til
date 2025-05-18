# `{% querystring %}` Template Tag

Django 5.1 introduces [a new template tag](https://docs.djangoproject.com/en/5.1/ref/templates/builtins/#std-templatetag-querystring): `{% querystring %}`.

This tag output a URL-encoded, formatted query string based on the provided parameters. E.g.:

```html
{% querystring color="blue" size="L" %}
```

Appends the `?color=blue&size=L` query params to the current URL..._while_ keeping any existing
parameters, and replacing the current value for `color` or `size` if the value's already set

```html
{% querystring color=None %} 
```

Removes the `?color=` query param from the current URL, if it's already set.

And, if the value passed is a list, then it will append `?color=blue&color=green` to the current URL, for as many items as exist in the list.

```html
{% querystring page=page.next_page_number as next_page %}
```

Further, you can access values in the variables. And, you can also assign the result to a
new template variable rather than outputting it directly to the page:

```html
{% querystring page=page.next_page_number as next_page %}
```
