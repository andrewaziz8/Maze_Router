from collections import deque
def lee_algorithm(grid, start, goal):
    h, w = len(grid), len(grid[0])
    visited = [[False]*w for _ in range(h)]
    parent = [[None]*w for _ in range(h)]
    q = deque()
    q.append(start)
    visited[start[0]][start[1]] = True

    directions = [(0,1), (1,0), (-1,0), (0,-1)]
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            break
        for dx, dy in directions:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny] and grid[nx][ny] == 1:
                visited[nx][ny] = True
                parent[nx][ny] = (x, y)
                q.append((nx, ny))

    # Backtrack path
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = parent[cur[0]][cur[1]]
        if cur is None:
            return []  # No path
    path.append(start)
    path.reverse()
    return path