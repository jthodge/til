# Trigger Opt-in File Downloads with the `Content-Disposition` Response Header

In addition to indicating that browser content is expected to rendered `inline` as part of a web page e.g.

```
Content-Disposition: inline
```

the `Content-Disposition` header can also be used to specify that content should be downloaded and saved locally.
To trigger a "Save as" download using the response header:

```
Content-Disposition: attachment; filename="eight.three"
```
