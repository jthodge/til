# `=` Serves as Padding in Base64 Encoded Strings

The `=` symbol has *one* purpose in Base64 encoding: padding.

[RFC2045](https://tools.ietf.org/rfc/rfc2045.txt) specifies that `=` is used as a padding character when fewer than 24 bits are available at the end of the encoded data:

```
When fewer than 24 input bits
are available in an input group, zero bits are added (on the right)
to form an integral number of 6-bit groups.  Padding at the end of
the data is performed using the "=" character.
```

Stated a bit differently, this means that `=` padding is used when the number of bits in the encoded data is not a multiple of 3.
By extension, that means that there's four cases of encoded output that can arise:

1. zero-padded (no `=`)
2. `=` padded
3. `==` padded
4. `===` padded
