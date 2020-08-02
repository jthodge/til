# Git Only Stores Timestamps and Author Information on Commits

Git only stores timestamps and author information on commmits, not trees. So, the same state of file contents for a given commit will return the same hexadecimal ID for a tree, regardless of who made changes to the files, and when.

So e.g. if you run the following:

```terminal
example-directory on  master
➜ echo "hello" > hello.txt

example-directory on  master [?]
➜ echo "world" > world.txt

example-directory on  master [?]
➜ git add .

example-directory on  master [+]
➜ git commit -m "first commit"
[master (root-commit) 3d27731] first commit
 2 files changed, 2 insertions(+)
 create mode 100644 hello.txt
 create mode 100644 world.txt

example-directory on  master
➜ git cat-file -p 3d27731
tree 88e38705fdbd3608cddbe904b67c731f3234c45b
author Taylor Hodge <j.taylor.hodge@gmail.com> 1596388561 -0400
committer Taylor Hodge <j.taylor.hodge@gmail.com> 1596388561 -0400

first commit

example-directory on  master
➜ git cat-file -p 88e38705fdbd3608cddbe904b67c731f3234c45b
100644 blob ce013625030ba8dba906f756967f9e9ca394464a	hello.txt
100644 blob cc628ccd10742baea8241c5924df992b5c019f71	world.txt
```

Then you'll receive the same tree ID `88e38705fdbd3608cddbe904b67c731f3234c45b` and `cat-file $TREE_ID` contents.
