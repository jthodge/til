# The Difference Between `Ctrl+c` and `Ctrl+\`

`Ctrl+c` ("c" for "cancel") is a command in CLI environments that's commonly used to abort or terminate a running process.

More specifically, the `Ctrl+c` sequence sends a `SIGINT` interruption signal to the active process. Then, if the process does not specify how to handle this signal, then the process is terminated. It's also common for a process that does handle `SIGINT` signals to explicitly terminate itself.

However, there are edge case processes that will handle `Ctrl+c` differently, and this can be quite confusing when trying to terminate an errant process.

This is where `Ctrl+\` comes in.

`Ctrl+\` is a command in CLI environments that explicitly terminates a running process, as well as producing a memory core dump of the process too.

`Ctrl+\` will terminate any pesky processes that don't handle `Ctrl+c` as expected, because `Ctrl+\` sends a `SIGQUIT` signal instead of a `SIGINT`.
