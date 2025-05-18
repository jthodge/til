# Use `column` to View Pretty CSVs

So, here's two things that (I think many would agree) are True:

1. CSV files are ubiquitous, and
2. Viewing CSV files in a CLI is a notoriously annoying and fruitless experience.

Common tools like `head` and `less` make it _very_ difficult to take much of value from a CSV in a CLI.

But! `column` is an an unknown (to me) tool that can help us wrangle unwieldy CSVs into useful data that actually make sense. And by composing `column` with a couple of more common tools, we can construct a handy method of interacting with CSVs without having to exit a CLI.

At its most simple, `column` aligns data in proportional...columns:

```bash
cat lovely-data-about-trees.csv | column -t -s,
```

- `-t` determines the number of columns the input file contains. By default, columns are delimited by whitespace. (Which is why we need...)
- `-s` specifies the delimiter used to determine the number of columns in our table.

It can be helpful to get a broader view by viewing the data in its out page using `less`:

```bash
cat lovely-data-about-trees.csv | column -t -s, | less -S
```
