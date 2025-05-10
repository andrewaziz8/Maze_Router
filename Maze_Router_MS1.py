from collections import deque
import re

def parse_input(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    size_line = lines[0].strip()
    width, height = map(int, size_line.lower().split('x'))
    MAX_SIZE = 1000
    if width > MAX_SIZE or height > MAX_SIZE:
        raise ValueError(f"Grid size {width}x{height} exceeds limit of {MAX_SIZE}x{MAX_SIZE}")
    grid = [[0 for _ in range(width)] for _ in range(height)]

    obstacles = []
    nets = {}
    pins_by_net = {}
    for line in lines[1:]:
        if line.startswith('OBS'):
            x, y = map(int, re.findall(r'\((\d+),\s*(\d+)\)', line)[0])
            obstacles.append((x, y))
            grid[y][x] = -1  # Mark obstacle
        elif line.startswith('net'):
            net_name = line.split()[0]
            coords = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            pins = [(int(x), int(y)) for (layer, x, y) in coords if layer == '1']
            pins_by_net[net_name] = pins
            nets[net_name] = [
                (int(x), int(y))
                for (layer, x, y) in coords
                if layer == '1' and 0 <= int(x) < width and 0 <= int(y) < height
            ]
    return grid, nets, width, height, obstacles, pins_by_net

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
    
def route_net(grid, pins):
    routed_path = []
    sources = [pins[0]]
    targets = set(pins[1:])
    current_grid = [row[:] for row in grid]
    while targets:
        # Find nearest target from sources
        shortest_path = None
        for s in sources:
            for t in targets:
                path = lee_algorithm(current_grid, s, t)
                if path and (shortest_path is None or len(path) < len(shortest_path)):
                    shortest_path = path
                    best_target = t
        if not shortest_path:
            print("Routing failed.")
            return []
        routed_path.extend(shortest_path)
        for cell in shortest_path:
            current_grid[cell[1]][cell[0]] = -2
        sources.extend(shortest_path)
        targets.remove(best_target)
    return routed_path

def write_output(routed, output_path):
    with open(output_path, 'w') as f:
        for net, path in routed.items():
            line = f"{net} " + " ".join(f"(1, {x}, {y})" for (x, y) in path)
            f.write(line + "\n")

def main(input_path, output_path):
    grid, nets, width, height, obstacles,_ = parse_input(input_path)
    routed_nets = {}
    for net, pins in nets.items():
        if not pins:
          print(f"Skipping {net}: no valid pins on layer 1 within bounds.")
          continue
        print(f"Routing {net}...")
        path = route_net(grid, pins)
        if not path:
            print(f"Failed to route {net}")
        routed_nets[net] = path
        for x, y in path:
            grid[y][x] = -2
    write_output(routed_nets, output_path)
    print("Routing complete. Output saved.")

# Example usage:
main("input3.txt", "output.txt")
