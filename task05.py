from typing import List


def find_maximal_subarray_sum(nums: List[int], k: int) -> int:
    max_sum = float('-inf')

    for i in range(len(nums)):
        current_sum = 0
        for j in range(i, min(i + k, len(nums))):
            current_sum += nums[j]
            max_sum = max(max_sum, current_sum)

    return max_sum


# пример
print(find_maximal_subarray_sum([1, 3, -1, -3, 5, 3, 6, 7], 3))  # 16
print(find_maximal_subarray_sum([1, 1, -1, -3, 5, 3, 12, 7, 5, 8, 10, 9], 5))  # 42
print(find_maximal_subarray_sum([1, 1, -1, 0, 42, 0, 0, 22, 7], 3))  # 42
