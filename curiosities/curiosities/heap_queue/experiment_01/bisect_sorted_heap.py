from bisect import insort_left

def insort_descending(a, x):
    """Insert item x in list a, and keep it sorted assuming a is sorted in descending order."""
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > x:
            lo = mid + 1
        else:
            hi = mid

def heappush(heap, item):
    """Push item onto heap, maintaining the heap sorted."""
    heap.append(item)

def heappop(heap):
    """Pop the smallest item off the heap, maintaining the heap sorted."""
    return heap.pop()

def heapify(x):
    """Transform list into a heap, in-place."""
    x.sort(reverse=True)
