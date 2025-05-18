# Canceling Asynchronous Threads Can Be Tricky

Consider that we have a function managing two threads: one thread performs a query for our desired data, and the other thread cancels the first.

```typescript
const myFunction = () => {
  const [isCanceled, setCanceled] = useState(false);

  const start = () => {
    await fetchDataSlowly();
  };

  const cancel = () => setCanceled(true);

  return (
    <div>
      <Button onClick={start}>Start</Button>
      <Button onClick={cancel}>Cancel</Button>
    </div>
  );
};
```

Looks harmless enough, right?
Not so much...

Because, unfortunately, once we kick off the first thread, the external state remains locked and `false`. No matter how we try to manage these threads with our two buttons, or how long `fetchDataSlowly` takes, `isCanceled` will always return `false` from within the `start` function.
We can check this:

```typescript
...
  const start = () => {
    await fetchDataSlowly();

    console.log(canceled);
    // always returns false
  };
...
```

This is especially hairy since it can lead to a nefarious overwrite bug. Suppose:

1. Press the `Start` button; `start` is fired and we begin to `fetchDataSlowly`
2. Press the `Cancel` button; `cancel` is fired and the query is "canceled" (as far as we now, since we clicked the button, right?)
3. `fetchDataSlowly` completes and updates our query results because `isCancelled` is still `false`

We can avoid this by making two changes:

1. Pull a temporary value out of `start`, and store our query results in this temporary value, instead of within the `start` function. And
2. Check if the query was canceled with `useEffect`. If the query wasn't canceled, then we update the original results.

```typescript
const myImprovedFunction = () => {
  const [isCanceled, setCanceled] = useState(false);
  const [results, setResults] = useState();
  const [queryResults, setQueryResults] = useState();

  useEffect(() => {
    if (!isCanceled) {
      setResults(queryResults);
    }
  }, [queryResults]);

  const start = () => {
    setCanceled(false);
    const results = await fetchDataSlowly();

    setQueryResults(results);
  };

  const cancel = () => setCanceled(true);

  return (
    <div>
      <Button onClick={start}>Start</Button>
      <Button onClick={cancel}>Cancel</Button>
      {results}
    </div>
  );
};
```

This certainly solves our original issue of the locked thread within `start`. But! It doesn't solve this edge case:

1. Press the `Start` button; `start` is fired and we begin to `fetchDataSlowly`
2. Immediately press the `Cancel` button; `cancel` is fired and the query is canceled (but, with (more) certainty this time; I promise!)
3. Press the `Start` button; `start` is fired and we begin to `fetchDataSlowly` again with a new query
4. Patiently wait for the new query to resolve

During this workflow, if the second query is faster than the first query then the rapid change in state will visually cancel and the results of the second query will be displayed after Step 4. However, once the first query resolves, its results will overwrite the results of the second query! This overwrite occurs because we're resetting `isCanceled` and `useEffect` isn't able to determine whether or not the value of `isCanceled` has been set by the first or second query.

One potential solution for this edge case is to generate a unique ID when kicking off a query. We save this ID in the state as `currentQueryID`. And when we save the query results to a temporary variable, we also save the ID that we generated with that associated query. Then, within `useEffect`, we can compare the value of `currentQueryID` (in state) to the ID saved along with the results of the temporary value. If `currentQueryID` and the ID of the temporary value results are equal, only then do we update the actual results.
