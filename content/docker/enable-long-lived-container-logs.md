# Enable Long-Lived Container Logs

An all-too-common, frustrating and time-consuming, pain point: tailed container logs terminate silently in a seemingly non-deterministic manner, forcing you to terminate your connection to the container and execute the `logs` command again.
A workaround to prevent this behavior (when using `docker-compose`) is to use [the `COMPOSE_HTTP_TIMEOUT` environment variable](https://docs.docker.com/compose/reference/envvars/)[^1], and increase the default timeout value to a more suitable duration, in seconds:

```bash
COMPOSE_HTTP_TIMEOUT=86400 docker-compose logs -ft --tail="all" --no-log-prefix $CONTAINER_NAME
```

[^1]: `COMPOSE_HTTP_TIMEOUT` was deprecated in `docker-compose` v2. I'm unsure if this workaround still works in versions >= 2, or what an equivalent workaround would be.
