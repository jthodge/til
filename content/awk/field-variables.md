# Field Variables

When `awk` reads an input record, `awk` parses the record to separate it into
discrete chunks called _fields_.

Fields make it easier to refer to specific chunks of the input record. We can
refer to these fields using using variables notated by bling-prepended integers.

I.e. we use `$` to refer to a field in the `awk` input record, followed by the
integer of the field we want. E.g.:

- `$1` refers to the first record field
- `$2` refers to the second record field
- `$3` refers to the third record field
(...)
- `$0` refers to a container that contains all fields

N.B. Integer field identifiers are not limited to single digits (as in Unix
shells). E.g. `$101` is the 101st field in the record.
