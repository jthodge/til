# Default Error Behavior

```bash
set -euo pipefail
```

Understanding and implementing the following will improve the predictability and reliability of bash scripts.

By default, bash will continue executing after encountering an error.
`set -e` will change this behavior, and halt execution on error.

By default, unset variables won't error.
`set -u` will change this behavior, and halt execution on unset variables.

By default, a single command in a pipeline will not cause the entire pipeline to fail.
`set -o pipefail` will change this behavior, and halt pipeline execution on single command errors.
