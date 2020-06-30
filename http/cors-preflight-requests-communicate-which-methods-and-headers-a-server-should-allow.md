# CORS Preflight Requests Communicate Which Methods and Headers a Server Should Allow

A CORS preflight request is an `OPTIONS` request sent before the main HTTP request. This `OPTIONS` request communicates to the receiving server what specific methods and headers should expect and allow.

The `OPTIONS` preflight request uses the following three HTTP request headers:

* `Access-Control-Request-Method`
* `Access-Control-Request-Headers`
* `Origin`

A CORS preflight request is automatically triggered by a browser when a request does not meet the requirements for a "[simple request](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Simple_requests)."

E.g. a client might send a request to a server to allow a `POST` request. But, before sending the desired `POST` request, the client would make the following preflight request:

```bash
OPTIONS /resource/endpoint HTTP/1.1
Access-Control-Request-Method: POST 
Access-Control-Request-Headers: content-type, x-csrf-token
Origin: https://example.com
...
```

Then, if the server allows the request, then the server will respond to the preflight request with an `Access-Control-Allow-Methods` response header that explicitly lists `POST`:

```bash
HTTP/1.1 204 No Content
Connection: keep-alive
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Accept, X-Real-IP, X-CSRF-Token, X-Polling-Query
...
```

The client will then go on to make the main `POST` request, and the server will respond accordingly.

NB. If you're ever debugging HTTP requests and notice that an `OPTIONS` request is made, but there is no accompanying `204` response—odds are you're now facing a CORS issue (godspeed).
