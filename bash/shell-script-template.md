# Shell Script Template

```bash
#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
  echo 'Usage: ./script.sh <arg1> <arg2>
    Your life improving bash script. 
  '
  exit
fi

cd "$(dirname "$0")"

main() {
    echo "Performing script operations..."
}

main "$@"
```
