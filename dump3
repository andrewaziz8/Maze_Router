from collections import deque
def lee_algorithm(grid, start, goal):
    h, w = len(grid), len(grid[0])
    visited = [[False]*w for _ in range(h)]
    parent = [[None]*w for _ in range(h)]
    q = deque()
    q.append(start)
    visited[start[1]][start[0]] = True

    directions = [(0,1), (1,0), (-1,0), (0,-1)]
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            break
        for dx, dy in directions:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx] and grid[ny][nx] == 0:
                visited[ny][nx] = True
                parent[ny][nx] = (x, y)
                q.append((nx, ny))

    # Backtrack path
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = parent[cur[1]][cur[0]]
        if cur is None:
            return []  # No path
    path.append(start)
    path.reverse()
    return path
