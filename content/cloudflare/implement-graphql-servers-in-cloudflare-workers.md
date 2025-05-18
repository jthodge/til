# Implement GraphQL Servers in Cloudflare Workers

Because the `graphql` library is isomorphic, it's possible to implement GraphQL servers in Cloudflare Workers. E.g.

`handler.ts`

```typescript
export const handleRequest = async (request: Request) => {
  const result = await graphql({
    schema,
    source: "query testQuery {hello, __typename}",
    contextValue: request,
  });

  return new Response(JSON.stringify(result));
};
```

Response

```json
{
  "data": {
    "hello": "hello world",
    "__typename": "Query"
  }
}
```

This can be especially useful as a lightweight alternative to more bloated solutions like Apollo Server.
