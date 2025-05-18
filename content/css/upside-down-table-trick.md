# Upside Down Table Trick

It can be difficult to build highly customizable, scrollable tables.
Relocating a horizontal table's scrollbar from the default bottom position, to the top of a table, is one such finnicky customization.

To accomplish this:

1. Flip the table's parent wrapper `<div>` upside down, using `rotateX(180deg)`
2. Place the header at the bottom (which, at this point, is the top)
3. Flip the `<tbody>` inside th table
4. Flip the content inside the `<thead>`.

This will relocate the table's scrollbar to the top. And, moreso, it will be sticky, so it's always within reach.

via. [RGBCube](https://lobste.rs/s/dghv8d/please_make_your_table_headings_sticky#c_iztvit).

[PoC](https://lobste.rs/s/dghv8d/please_make_your_table_headings_sticky#c_hww77t)
