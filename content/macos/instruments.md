# Instruments

📖: [User Guide](https://help.apple.com/instruments/mac/current/)

## Use

Launch Instruments from the CLI:

```sh
open /Applications/Xcode.app/Contents/Applications/Instruments.app
```

Profile with the Instruments CLI:

```sh
cd /Applications/Utilities
instruments -t "Allocations" -D ~/trace_file_name.trace path/to/profiled/app
```

## Options

| Configuration option | Description |
|----------------------|-------------|
| `-t template` | The name or path of the profiling template to use when analyzing your app. |
| `-s` | Returns a list of all installed profiling templates. |
| `-D document` | The path where the .trace document should be saved. If the file already exists, the newly recorded data is appended to it as a new run. |
| `-l #` | The amount of time to record, in milliseconds, before terminating. If not provided, recording occurs indefinitely, until the app is manually terminated. |
| `-i #` | The index of the instrument to use for recording. |
| `-p pid` | The process ID of the app to be recorded. |
| `application` | The path of the app to be recorded. |
| `-w hardware device` | The ID of the device to target. |
| `-e variable value` | An environment variable to be applied while profiling. |
| `argument` | A command-line argument to be passed to the app being profiled. Multiple arguments may be specified, if desired. |
| `-v` | Enables verbose logging while profiling. |
