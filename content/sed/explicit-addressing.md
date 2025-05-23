# Explicit Addressing

When a `sed` command doesn't have an explicit address, then the command is
applied to all lines.

E.g.

```bash
# Create example file
$ cat > fruits.txt <<'EOF'
apple
apricot
banana
avocado
EOF

# Run substitution _without_ an address
$ sed 's/a/A/' fruits.txt
Apple
Apricot
bAnana
AvocAdo

# Contra:
$ sed '1s/a/A/' fruits.txt
Apple      # substitution only applied to line 1
apricot
banana
avocado
```

