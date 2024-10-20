def dfs(space, curr_state, target_state, seen, path, slots):
    tuple_curr_state = tuple(curr_state)
    if tuple_curr_state in seen:
        return False

    path.append(tuple_curr_state)
    seen.add(tuple_curr_state)

    if tuple_curr_state == target_state:
        for state in path:
            print(''.join(state))
        return True

    # Check for move from left to right
    for i in range(1, 3):
        new_space = space - i
        if new_space >= 0 and curr_state[new_space] == '>':
            curr_state[space], curr_state[new_space] = curr_state[new_space], curr_state[space]
            if dfs(new_space, curr_state, target_state, seen, path, slots):
                return True
            curr_state[space], curr_state[new_space] = curr_state[new_space], curr_state[space]

    # Check for move from right to left
    for i in range(1, 3):
        new_space = space + i
        if space + i < slots and curr_state[new_space] == '<':
            curr_state[space], curr_state[new_space] = curr_state[new_space], curr_state[space]
            if dfs(space + i, curr_state, target_state, seen, path, slots):
                return True
            curr_state[space], curr_state[new_space] = curr_state[new_space], curr_state[space]

    path.pop()
    return False


def main():
    N = int(input("Enter N: "))
    slots = 2 * N + 1
    initial_state = ['>'] * N + ['-'] + ['<'] * N
    target_state = tuple(['<'] * N + ['-'] + ['>'] * N)
    seen = set()
    path = []
    dfs(slots // 2, initial_state, target_state, seen, path, slots)


if __name__ == '__main__':
    main()

# Vol. 2
# Better implementation but slower execution
# from typing import Tuple, NamedTuple
#
#
# # Define a Node class to store the current state and the index of the empty space
# class Node(NamedTuple):
#     space_index: int
#     state: Tuple[str, ...]
#
#
# def is_goal_reached(curr_state, target_state):
#     return curr_state == target_state
#
#
# def dfs(node: Node, target_state: tuple, seen: set, slots: int) -> bool:
#     if node in seen:
#         return False
#
#     seen.add(node)
#
#     if is_goal_reached(node.state, target_state):
#         print(''.join(node.state))  # Print the state when the target is reached
#         return True
#
#     # If direction equals -1 we move left with i positions
#     # If direction equals 1 we move right with i positions
#     for direction in (-1, 1):
#         for i in range(1, 3):
#             new_space = node.space_index + (i * direction)
#             if 0 <= new_space < slots:
#                 if (direction == -1 and node.state[new_space] == '>') or (
#                         direction == 1 and node.state[new_space] == '<'):
#                     new_state = list(node.state)
#                     new_state[node.space_index], new_state[new_space] = new_state[new_space], new_state[node.space_index]
#                     new_node = Node(new_space, tuple(new_state))
#                     if dfs(new_node, target_state, seen, slots):
#                         print(''.join(new_node.state))
#                         return True
#
#     return False
#
#
# def main():
#     N = int(input("Enter N: "))
#     slots = 2 * N + 1
#     initial_state = tuple(['>'] * N + ['-'] + ['<'] * N)
#     target_state = tuple(['<'] * N + ['-'] + ['>'] * N)
#     seen = set()
#
#     # Initialize the starting node
#     start_node = Node(space_index=slots // 2, state=initial_state)
#
#     dfs(start_node, target_state, seen, slots)
#     print(''.join(initial_state))
#
#
# if __name__ == '__main__':
#     main()
