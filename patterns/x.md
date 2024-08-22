# Lazy-Iteration Over Multiple Sorted Enumerables, Preserving Order

Assume you have multiple sorted enumerables. These functions will lazy-iterate
over all of them, returning items in a globally-sorted order.

## Two Implementations: Heap and Buffer

### 1. Heap-Based Implementation

```python
from typing import Iterable, Any
from itertools import count

def sorted_iterate_heap(*enums: Iterable[Any], with_index: bool = False):
    def generator():
        iters = [iter(e) for e in enums]
        heap = []
        for i, it in enumerate(iters):
            try:
                heap.append((next(it), i, it))
            except StopIteration:
                pass
        heap.sort(reverse=True)

        while heap:
            value, i, it = heap.pop()
            if with_index:
                yield value, i
            else:
                yield value
            try:
                next_value = next(it)
                insertion_point = len(heap)
                while insertion_point > 0 and next_value > heap[insertion_point-1][0]:
                    insertion_point -= 1
                heap.insert(insertion_point, (next_value, i, it))
            except StopIteration:
                pass

    return generator()

# Example usage
list1 = [1, 3, 5]
list2 = [2, 4, 6]
print("Simple list iteration:")
print(list(sorted_iterate_heap(list1, list2)))

print("\nWith index:")
print(list(sorted_iterate_heap(list1, list2, with_index=True)))

# Output:
# Simple list iteration:
# [1, 2, 3, 4, 5, 6]

# With index:
# [(1, 0), (2, 1), (3, 0), (4, 1), (5, 0), (6, 1)]
```

And accompanying tests:

```python
import unittest

class TestSortedIterateHeap(unittest.TestCase):
    def test_simple_lists(self):
        list1 = [1, 3, 5]
        list2 = [2, 4, 6]
        result = list(sorted_iterate_heap(list1, list2))
        self.assertEqual(result, [1, 2, 3, 4, 5, 6])

    def test_with_index(self):
        list1 = ['a', 'c', 'e']
        list2 = ['b', 'd', 'f']
        result = list(sorted_iterate_heap(list1, list2, with_index=True))
        self.assertEqual(result, [('a', 0), ('b', 1), ('c', 0), ('d', 1), ('e', 0), ('f', 1)])

    def test_empty_lists(self):
        result = list(sorted_iterate_heap([], [], []))
        self.assertEqual(result, [])

    def test_uneven_lists(self):
        list1 = [1, 4, 7]
        list2 = [2, 5]
        list3 = [3, 6, 8, 9]
        result = list(sorted_iterate_heap(list1, list2, list3))
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_custom_objects(self):
        class CustomObj:
            def __init__(self, value):
                self.value = value
            def __lt__(self, other):
                return self.value < other.value
            def __eq__(self, other):
                return self.value == other.value
            def __gt__(self, other):
                return self.value > other.value

        list1 = [CustomObj(1), CustomObj(3), CustomObj(5)]
        list2 = [CustomObj(2), CustomObj(4), CustomObj(6)]
        result = list(sorted_iterate_heap(list1, list2))
        self.assertEqual([obj.value for obj in result], [1, 2, 3, 4, 5, 6])

suite = unittest.TestLoader().loadTestsFromTestCase(TestSortedIterateHeap)
unittest.TextTestRunner(verbosity=2).run(suite)
```

### 2. Buffer-Based Implementation

```python
from typing import Iterable, Any
import heapq

def sorted_iterate_buffer(*enums: Iterable[Any]):
    def generator():
        iterators = [iter(enum) for enum in enums]
        heap = []

        # Initialize heap with first values
        for i, iterator in enumerate(iterators):
            try:
                heapq.heappush(heap, (next(iterator), i))
            except StopIteration:
                pass

        while heap:
            value, index = heapq.heappop(heap)
            yield value

            try:
                next_value = next(iterators[index])
                heapq.heappush(heap, (next_value, index))
            except StopIteration:
                pass

    return generator()

# Example usage
list1 = [1, 3, 5]
list2 = [2, 4, 6]
print(list(sorted_iterate_buffer(list1, list2)))

#Output:
# [1, 2, 3, 4, 5, 6]
```

And accompanying tests:

```python
import unittest
from typing import List, Any

class TestSortedIterateBuffer(unittest.TestCase):
    def test_simple_lists(self):
        list1 = [1, 3, 5]
        list2 = [2, 4, 6]
        result = list(sorted_iterate_buffer(list1, list2))
        self.assertEqual(result, [1, 2, 3, 4, 5, 6])

    def test_empty_lists(self):
        result = list(sorted_iterate_buffer([], [], []))
        self.assertEqual(result, [])

    def test_single_list(self):
        result = list(sorted_iterate_buffer([1, 2, 3]))
        self.assertEqual(result, [1, 2, 3])

    def test_uneven_lists(self):
        list1 = [1, 4, 7]
        list2 = [2, 5]
        list3 = [3, 6, 8, 9]
        result = list(sorted_iterate_buffer(list1, list2, list3))
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_duplicate_values(self):
        list1 = [1, 3, 3, 5]
        list2 = [2, 3, 4, 5]
        result = list(sorted_iterate_buffer(list1, list2))
        self.assertEqual(result, [1, 2, 3, 3, 3, 4, 5, 5])

    def test_custom_objects(self):
        class CustomObj:
            def __init__(self, value):
                self.value = value
            def __lt__(self, other):
                return self.value < other.value
            def __eq__(self, other):
                return self.value == other.value

        list1 = [CustomObj(1), CustomObj(3), CustomObj(5)]
        list2 = [CustomObj(2), CustomObj(4), CustomObj(6)]
        result = list(sorted_iterate_buffer(list1, list2))
        self.assertEqual([obj.value for obj in result], [1, 2, 3, 4, 5, 6])

    def test_large_number_of_lists(self):
        lists = [[i] for i in range(1000)]
        result = list(sorted_iterate_buffer(*lists))
        self.assertEqual(result, list(range(1000)))

    def test_iterator_input(self):
        iter1 = iter([1, 3, 5])
        iter2 = iter([2, 4, 6])
        result = list(sorted_iterate_buffer(iter1, iter2))
        self.assertEqual(result, [1, 2, 3, 4, 5, 6])

suite = unittest.TestLoader().loadTestsFromTestCase(TestSortedIterateBuffer)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
```

## Heap vs. Buffer

### Heap

The heap-based approach utilizes a min-heap data structure to efficiently track the smallest element across all iterables.

*Key Characteristics:*

Maintains a heap of size O(n), where n is the number of input iterables
Theoretical time complexity of O(N log n) for N total elements
Requires additional space for the heap structure

*Advantages:*

Theoretically efficient for a large number of input iterables
Cleanly separates the data structure (heap) from the merging logic

*Disadvantages:*

Overhead of heap operations (push and pop) can be significant
May suffer from poor cache locality due to indirect access patterns

### Buffer

The buffer-based approach maintains a simple list of buffers, one for each input iterable, and repeatedly selects the minimum value among the buffer heads.

*Key Characteristics:*

Maintains a list of buffers, each typically containing one element
Theoretical time complexity of O(N * n) for N total elements and n iterables
Minimal additional space requirements

*Advantages:*

Simpler implementation with less overhead
Better cache locality due to sequential access patterns
Performs well even with a large number of input iterables

*Disadvantages:*

Theoretically less efficient for a large number of iterables

### Performance

Performance benchmark tests:

```python
import timeit
import random
from typing import List, Any

def generate_test_data(num_lists: int, list_length: int, max_value: int = 1000000) -> List[List[int]]:
    return [sorted(random.sample(range(max_value), list_length)) for _ in range(num_lists)]

def performance_test(func, test_data):
    list(func(*test_data))  # Force evaluation of the generator

def run_performance_tests(num_lists_list, list_length_list, num_runs=3):
    results = []

    for num_lists in num_lists_list:
        for list_length in list_length_list:
            test_data = generate_test_data(num_lists, list_length)
            
            time_heap = timeit.timeit(lambda: performance_test(sorted_iterate_heap, test_data), number=num_runs) / num_runs
            time_buffer = timeit.timeit(lambda: performance_test(sorted_iterate_buffer, test_data), number=num_runs) / num_runs
            
            results.append({
                'num_lists': num_lists,
                'list_length': list_length,
                'time_heap': time_heap,
                'time_buffer': time_buffer
            })

    return results

num_lists_list = [2, 5, 10, 20, 50, 100]
list_length_list = [100, 1000, 10000]

results = run_performance_tests(num_lists_list, list_length_list)

print("Performance Comparison:")
print("----------------------")
for result in results:
    print(f"Number of lists: {result['num_lists']}, List length: {result['list_length']}")
    print(f"Heap-based:   {result['time_heap']:.6f} seconds")
    print(f"Buffer-based: {result['time_buffer']:.6f} seconds")
    print(f"Ratio (Buffer/Heap): {result['time_buffer'] / result['time_heap']:.2f}")
    print()
```

| Number of Lists | List Length | Heap-based (s) | Buffer-based (s) | Ratio (Buffer/Heap) |
|-----------------|-------------|----------------|------------------|---------------------|
| 2               | 100         | 0.000101       | 0.000090         | 0.89                |
| 2               | 1000        | 0.000842       | 0.000584         | 0.69                |
| 2               | 10000       | 0.002947       | 0.002582         | 0.88                |
| 5               | 100         | 0.000099       | 0.000092         | 0.93                |
| 5               | 1000        | 0.001175       | 0.001027         | 0.87                |
| 5               | 10000       | 0.008135       | 0.006455         | 0.79                |
| 10              | 100         | 0.000176       | 0.000139         | 0.79                |
| 10              | 1000        | 0.001849       | 0.001457         | 0.79                |
| 10              | 10000       | 0.019838       | 0.014543         | 0.73                |
| 20              | 100         | 0.000576       | 0.000329         | 0.57                |
| 20              | 1000        | 0.005748       | 0.003238         | 0.56                |
| 20              | 10000       | 0.057834       | 0.033085         | 0.57                |
| 50              | 100         | 0.002816       | 0.000918         | 0.33                |
| 50              | 1000        | 0.028246       | 0.009202         | 0.33                |
| 50              | 10000       | 0.284254       | 0.097240         | 0.34                |
| 100             | 100         | 0.010138       | 0.001995         | 0.20                |
| 100             | 1000        | 0.103604       | 0.020048         | 0.19                |
| 100             | 10000       | 1.039553       | 0.231553         | 0.22                |

![performance_vs_lists](https://github.com/user-attachments/assets/74e75978-0be7-4b18-aa57-dd677d6d941c)

![ratio_vs_lists](https://github.com/user-attachments/assets/9ad01e65-fb2a-4023-9975-d5b3ce0031bb)
