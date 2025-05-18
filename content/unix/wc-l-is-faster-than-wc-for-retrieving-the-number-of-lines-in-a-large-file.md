# `wc -l` is Faster than `wc` For Retrieving the Number of Lines in a Large File

If you only need to know the number of lines in a large file, then using `wc -l` is faster than using `wc`, because the number of bytes and number of words in the file are not calculated.
