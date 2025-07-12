# Dump pickle files to readable text

Python's pickle format is a binary serialization format.
These binaries  can be difficult to inspect.
When working with a pickle file, you can convert it to a readable text format using either the `pprint` or `json` module.

## Basic unpickling

```python
import pickle

# Load the pickled object
obj = pickle.load(open("data.pickle", "rb"))
```

## Pretty printing with pprint

```python
import pickle
import pprint

obj = pickle.load(open("data.pickle", "rb"))

# Write formatted output to file
with open("output.txt", "w") as f:
    pprint.pprint(obj, stream=f)
```

This is especially useful for nested data structures e.g. dictionarys, lists.

## JSON formatting for better readability

```python
import pickle
import json

obj = pickle.load(open("data.pickle", "rb"))

# JSON dump with indentation
with open("output.json", "w") as f:
    json.dump(obj, f, indent=2)
```

## `json` + `pprint`

Handle both formats, with error handling:

```python
import pickle
import json
import pprint
import sys

def dump_pickle_file(pickle_file, output_format="json"):
    """Convert a pickle file to readable text format."""
    try:
        # Load the pickle file
        with open(pickle_file, "rb") as f:
            obj = pickle.load(f)

        # Generate output filename
        base_name = pickle_file.rsplit(".", 1)[0]

        if output_format == "json":
            output_file = f"{base_name}.json"
            with open(output_file, "w") as f:
                json.dump(obj, f, indent=2, default=str)
            print(f"Dumped to {output_file}")
        else:
            output_file = f"{base_name}.txt"
            with open(output_file, "w") as f:
                pprint.pprint(obj, stream=f, width=120)
            print(f"Dumped to {output_file}")

    except Exception as e:
        print(f"Error processing pickle file: {e}")
        sys.exit(1)

# Usage
if __name__ == "__main__":
    dump_pickle_file("data.pickle", output_format="json")
```

## Security considerations (!)

Pickle files can execute arbitrary code during deserialization.
Only unpickle data from trusted sources, and default to safer data exchange formats when possible.

pickle is also Python-specific and version-dependent. This is limiting.
For long-term storage or cross-language compatibility, prefer standard formats like JSON, CSV, or protobufs.
