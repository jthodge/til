# Inconsistencies in `Date`

JavaScript's `Date` [built-in objects](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date) have some...strange behaviors and inconsistencies.

To begin: the name. Despite being called `Date`, it also represents time.

## `getYear()`

`getYear()` returns the year as a number with an offset of 1900. This means that years >= 2000 return values >= 100. Years <= 1999 and >= 1900 are between 0 and 99. And years < 1900 return negative values. Wat.

E.g. in 2020

```javascript
new Date().getYear();
```

returns `120`.

To get the current year without an offset, use `getFullYear()`.

## `getMonth()`

`getMonth()` unexpectedly returns a zero-based number value from 0-11 indicating the month, instead of...the actual month. I.e. `0` === January, `1` === February, etc.

## `getDay()`

`getDay()` unexpectedly returns a zero-based number value from 0-6 indicating weekday, instead of the day of the month. I.e. `0` === Monday, `1` === Tuesday, etc.
