import random

def merge(a1, a2):
    mergedList = []
    i, j = 0, 0
    n, m = len(a1), len(a2)
    while i < n and j < m:
        if a1[i] < a2[j]:
            mergedList.append(a1[i])
            i += 1
        else:
            mergedList.append(a2[j])
            j += 1
    if i < n:
        for k in range(i, n):
            mergedList.append(a1[k])
    if j < m:
        for k in range(j, m):
            mergedList.append(a2[k])
    return mergedList

def mergeSort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    leftPart = mergeSort(arr[:mid])
    rightPart = mergeSort(arr[mid:])
    sortedList = merge(leftPart, rightPart)
    return sortedList

if __name__ == "__main__":
    for i in range(10):
        unsorted = []
        for j in range(15):
            unsorted.append(random.randrange(50))
        print("Unsorted: ")
        print(unsorted)
        print("Sorted: ")
        print(mergeSort(unsorted))
        print()