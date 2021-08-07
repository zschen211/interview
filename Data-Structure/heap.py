class Heap:
    def __init__(self):
        self.array = [None]

    def leftChild(self, idx):
        if idx * 2 >= len(self.array):
            return -1
        return idx * 2

    def rightChild(self, idx):
        if idx * 2 + 1 >= len(self.array):
            return -1
        return idx * 2 + 1
    
    def parent(self, idx):
        if idx <= 1:
            return -1
        return idx // 2

    def heapifyUp(self, idx):
        parentIdx = self.parent(idx)
        while parentIdx != -1:
            if self.array[parentIdx] > self.array[idx]:
                self.array[parentIdx], self.array[idx] = self.array[idx], self.array[parentIdx]
                idx = parentIdx
                parentIdx = self.parent(idx)
            else:
                break
    
    def heapifyDown(self, idx):
        leftIdx = self.leftChild(idx)
        rightIdx = self.rightChild(idx)
        swapIdx = idx
        if leftIdx != -1 and self.array[leftIdx] < self.array[swapIdx]:
            swapIdx = leftIdx
        if rightIdx != -1 and self.array[rightIdx] < self.array[swapIdx]:
            swapIdx = rightIdx
        if swapIdx != idx:
            self.array[swapIdx], self.array[idx] = self.array[idx], self.array[swapIdx]
            self.heapifyDown(swapIdx)

    def insert(self, val):
        self.array.append(val)
        self.heapifyUp(len(self.array) - 1)

    def remove(self):
        if len(self.array) == 1:
            return
        elif len(self.array) == 2:
            self.array.pop()
        else:
            self.array[1], self.array[-1] = self.array[-1], self.array[1]
            self.array.pop()
            self.heapifyDown(1)

    def peek(self):
        if len(self.array) < 2:
            return "no element"
        return self.array[1]

if __name__ == "__main__":
    heap = Heap()
    for i in reversed(range(10)):
        heap.insert(i)
    for i in range(10):
        print(heap.peek())
        heap.remove()
    