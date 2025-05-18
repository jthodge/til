# `kill` Works on Any Process

So, it turns out that `kill` works on so much more than programs and applications!

You can use `kill` to send _any_ signal to a program:

```terminal
kill -SIGNAL PID
```

Shortlist of signals that `kill` can send:
| Command     | Name        | Number      |
| ----------- | ----------- | ----------- |
| kill        | SIGTERM     |     15      |
| kill -q     | SIGKILL     |      9      |
| kill -KILL  | SIGKILL     |      9      |
| kill -HUP   | SIGHUP      |      1      |
| kill -STOP  | SIGSTOP     |     19      |

For a longer list: `kill -l` will list all possible signal values

## A Few Useful Ways to Use `kill`

```terminal
killall -SIGNAL NAME
```

Sends the `-SIGNAL` parameter argument to all processes with `NAME`.

e.g.

```terminal
killall firefox
```

Useful flags:
- `-w`: wait for all signaled processes to die
- `-i`: ask before signalling the relevant process

---

```terminal
pgrep
```

Prints the PIDs of all running programs with a matchibg process ID.

e.g.

```terminal
pgrep fire
```

matches:
- firefox
- firebird

and _does not_ match:
- bash firefox.sh

You can also grep the entire command line (e.g. to include bash firefox.sh):
```terminal
pgrep -f
```

---

```terminal
pkill
```

Works the same as `pgrep`, but signals all found PIDs.

e.g.

```terminal
pkill -f firefox
```
