# Quiet Mode

Move in and out of a Python REPL without ceremony and fluff:

Python 3:

```bash
12:43:29.140 with jth in ~ at arroyo via 🐍 3.13.2 via base
➜ python -q
>>>
```

Python 2:

```bash
12:45:09.540 with jth in ~ at arroyo via 🐍 2.7.18 via base
➜ python -ic ""
>>>
```

Python added [the `-q` option](https://docs.python.org/3/using/cmdline.html#cmdoption-q) in 3.2.
In Python 2, `-ic ""` is a workaround. Combining the `-i` and `-c` options
command Python to "run the following script, and then enter interpreter mode."
But, in this case, the script is only the empty string, so Python noops and then
quietly enters the interpreter.
