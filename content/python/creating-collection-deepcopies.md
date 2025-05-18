# Creating Deep Copies of Collections

Python has a [built-in `copy` module](https://docs.python.org/3/library/copy.html#module-copy):

> "Assignment statements in Python do not copy objects, they create bindings between a target and an object. For collections that are mutable or contain mutable items, a copy is sometimes needed so one can change one copy without changing the other. This module provides generic shallow and deep copy operations."

This binding is especially useful for solving in-place modification of lists within a user-defined function:

```python
def rotate_list_plus_one_index(list):
    list.insert(0, list.pop())

nums = [1, 2, 3, 4, 5]
rotate_list_plus_one_index(nums)
print(nums)
# [5, 1, 2, 3, 4]
```

However, if we want to recursively create new copies of all the nested elements contained within a mutable object (vs. modifying in place), we can use the `deepcopy` method:

```python
import copy

nums_2d = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
nums_2d_deepcopy = copy.deepcopy(nums_2d)
nums_2d_deepcopy[0][0] = 0

print(nums_2d)
# [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

print(nums_2d_deepcopy)
# [[0, 2, 3], [4, 5, 6], [7, 8, 9]]
```
