# Dates as Keys are not Equal

Dates in JavaScript never cease to amaze.

When using dates as keys in a Map (or, similarly, as values in a Set), those "dates as keys" (expectedly, considering how Dates work in JavaScript) behave in unexpected ways.

```typescript
dateMap = new Map([
  [new Date(Date.UTC(2021, 0, 1)), "blue"], // this key is distinct from the key below
  [new Date(Date.UTC(2021, 0, 1)), "red"], // this key is distinct from the key above
]);
```

```typescript
dateMap.get(new Date(Date.UTC(2021, 0, 1)));
// returns undefined
```

We would expect, given that each of these keys is the same date, that these dates are the same, but they're not. Why's that?

Because [JavaScript Maps use `sameValueZero` to determine key equality](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map#key_equality). This means that for any two dates to be considered equal, then they must be _the same instance of the same object, not just same moment in datetime_.

Just as with key lookups, this same quirk holds true when using the equality operator as well:

```typescript
const date0 = new Date(Date.UTC(2021, 0, 1));
const date1 = new Date(Date.UTC(2021, 0, 1));
return date0 === date1;
// returns false
```

Luckily, we can avoid this issue by choosing to use primitive data type values like numbers or strings as keys instead of dates.

```typescript
numberMap = new Map([[5144401358, "blue"]]);
```

However, keep in mind that this can be a bit cumbersome and tedious, since it's too easy to forget to coerce types correctly.

```typescript
numberMap.get(5144401358);
// returns "blue"
```

```typescript
numberMap.get(new Date(5144401358));
//returns undefined
```
