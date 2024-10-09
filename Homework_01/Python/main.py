def dfs(space):
    if found_solution[0] or tuple(initial_state) in seen:
        return

    path.append(initial_state[:])
    seen.add(tuple(initial_state))

    if initial_state == target_state:
        for p in path:
            print(''.join(p))
        found_solution[0] = True
        return

    # Check for move from left to right
    for i in range(1, 3):
        if space - i >= 0 and initial_state[space - i] == '>':
            initial_state[space], initial_state[space - i] = initial_state[space - i], initial_state[space]
            dfs(space - i)
            initial_state[space], initial_state[space - i] = initial_state[space - i], initial_state[space]

    # Check for move from right to left
    for i in range(1, 3):
        if space + i < slots and initial_state[space + i] == '<':
            initial_state[space], initial_state[space + i] = initial_state[space + i], initial_state[space]
            dfs(space + i)
            initial_state[space], initial_state[space + i] = initial_state[space + i], initial_state[space]

    path.pop()


if __name__ == '__main__':
    N = int(input("Enter N: "))
    slots = 2 * N + 1
    initial_state = ['>'] * N + ['-'] + ['<'] * N
    target_state = ['<'] * N + ['-'] + ['>'] * N
    seen = set()
    found_solution = [False]
    path = []
    dfs(slots // 2)
