# Random sampling with `shuf`

The `shuf` command randomly permutes or samples lines from a file.

## Basic usage - random permutation

```bash
shuf data.txt
```

## Sampling without replacement

Use `-n` to select a specific number of lines without replacement:

```bash
# Select 10 random lines from the file
shuf -n 10 data.txt

# Select 100 random users from a user list
shuf -n 100 users.csv
```

N.B. If you request more lines than exist in the file, `shuf` returns all available lines without error.

## Sampling with replacement

Add `-r` to sample with replacement, allowing lines to appear multiple times:

```bash
# Sample 10 lines with replacement
shuf -r -n 10 data.txt

# Generate 1000 samples from a small dataset
shuf -r -n 1000 categories.txt
```

This is particularly useful when you need more samples than available lines, or for bootstrap sampling!

## Common Cases

### Create a test dataset from production data

```bash
# Extract 1% sample from large log file
total_lines=$(wc -l < production.log)
sample_size=$((total_lines / 100))
shuf -n "$sample_size" production.log > test_sample.log
```

### Random selection for A/B testing

```bash
# Split users into test groups
shuf users.txt | head -n 5000 > group_a.txt
shuf users.txt | head -n 5000 > group_b.txt
```

### Generate random training/validation splits

```bash
# Create 80/20 train/test split
shuf dataset.csv > shuffled.csv
total=$(wc -l < shuffled.csv)
train_size=$((total * 80 / 100))

head -n "$train_size" shuffled.csv > train.csv
tail -n +$((train_size + 1)) shuffled.csv > test.csv
```

## Controlling randomness

### Using a custom random source

```bash
# Use a specific random source (GNU coreutils)
shuf --random-source=/dev/urandom data.txt

# For reproducible results, use a fixed source
dd if=/dev/zero bs=1024 count=1 2>/dev/null | shuf --random-source=- data.txt
```

### Piping with other tools

```bash
# Random sample of specific patterns
grep "ERROR" logs.txt | shuf -n 50

# Random selection from command output
find . -name "*.jpg" | shuf -n 10

# Process random subset in parallel
shuf -n 1000 tasks.txt | parallel -j 4 process_task
```

## Performance considerations

`shuf` needs to read its complete input file into memory. For files too large to fit in memory:

```bash
# Use reservoir sampling with awk for streaming
awk -v n=1000 'BEGIN{srand()} {if(NR<=n)a[NR]=$0; else if(rand()<n/NR)a[int(rand()*n)+1]=$0} END{for(i in a)print a[i]}' huge_file.txt
```

## Platform availability

`shuf` is part of GNU coreutils and available on most Linux distributions.
But if you're like on a macOS daily driver, install via:

```bash
brew install coreutils
# Then use as 'gshuf'
```
