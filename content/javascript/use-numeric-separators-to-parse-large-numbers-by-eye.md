# Use Numeric Separators to Parse Large Numbers by Eye

Large numeric literals are difficult to quickly parse with the human eye, especially when there are many repeating digits. E.g.

`1000000000000`
`3141592653.58`

To improve readability of large numeric literals, [use underscores as numeric separators](https://github.com/tc39/proposal-numeric-separator). E.g.

`1_000_000_000_000`
`3_141_592_653.58`

Numeric separators improve readability for many different kinds of numeric literals:

```javascript
// A decimal integer literal with digits grouped per thousand:
1_000_000_000_000;
// A decimal literal with digits grouped per thousand:
1_000_000.123_456;
// A binary integer literal with bits grouped per octet:
0b01010110_00111000;
// A binary integer literal with bits grouped per nibble:
0b0101_0110_0011_1000;
// A hexadecimal integer literal with digits grouped by byte:
0x40_76_38_6a_73;
// A BigInt literal with digits grouped per thousand:
4_642_473_943_484_686_707n;
// A numeric separator in an octal integer literal:
0o123_456;
```
