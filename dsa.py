# Problem 1 — Warm Up
# Write a function find_max(arr) that:

# Takes a list of numbers
# Returns the largest number without using Python's built-in max()

# Expected output:
# pythonfind_max([3, 1, 9, 5, 7])  # 9
# find_max([10, 2, 45, 6])   # 45
# No built-in max() allowed — use a loop! 💪

def find_max(arr):
  max = arr[0]
  for i in range(len(arr)):
     if(arr[i] > max):
       max = arr[i]
  return max

x = find_max([3, 1, 9, 5, 7])
print(x)


# 🧩 Problem 2 — Reverse an Array
# Write a function reverse_arr(arr) that:

# Takes a list
# Returns the reversed list without using reverse() or [::-1]

# Expected output:
# pythonreverse_arr([1, 2, 3, 4, 5])   # [5, 4, 3, 2, 1]
# reverse_arr([10, 20, 30])       # [30, 20, 10]


def reverse_array(arr):
    reverse_arr =[]
    for num in range(len(arr)-1, -1, -1):
      reverse_arr.append(arr[num])

    return reverse_arr


x = reverse_array([1, 2, 3, 4, 5])
print(x)

# 🧩 Problem 3 — Remove Duplicates
# Write a function remove_duplicates(arr) that:

# Takes a list of numbers
# Returns a new list with duplicates removed
# Maintain the original order
# Do NOT use set() directly

# Expected output:
# pythonremove_duplicates([1, 2, 2, 3, 4, 4, 5])  # [1, 2, 3, 4, 5]
# remove_duplicates([10, 10, 20, 30, 20])    # [10, 20, 30]
# 💪 Go for it!