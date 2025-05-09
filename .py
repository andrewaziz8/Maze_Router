


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
    for line in lines[1:]:
        if line.startswith('OBS'):
            x, y = map(int, re.findall(r'\((\d+),\s*(\d+)\)', line)[0])
            obstacles.append((x, y))
            grid[y][x] = -1  # Mark obstacle
        elif line.startswith('net'):
            net_name = line.split()[0]
            coords = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            nets[net_name] = [
                (int(x), int(y))
                for (layer, x, y) in coords
                if layer == '1' and 0 <= int(x) < width and 0 <= int(y) < height

            ]
    return grid, nets, width, height, obstacles

