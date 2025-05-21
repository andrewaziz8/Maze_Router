import re
import os

def parse_input(file_path):
    """Parse the input file to extract grid size, obstacles, and nets.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        A tuple containing:
        - width: Grid width
        - height: Grid height
        - obstacles: List of obstacle coordinates (x, y)
        - nets: Dictionary of net names to lists of pins
        - pins_by_net: Dictionary of net names to lists of pins
        - grid: 3D grid representation [layer][y][x]
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Extract grid size
    size_line = lines[0].strip()
    width, height = map(int, size_line.lower().split('x'))
    
    MAX_SIZE = 1000
    if width > MAX_SIZE or height > MAX_SIZE:
        raise ValueError(f"Grid size {width}x{height} exceeds limit of {MAX_SIZE}x{MAX_SIZE}")
    
    # Initialize the grid for both layers (layer 1 and layer 2)
    # 0 = empty, -1 = obstacle, -2 = already routed
    grid = [[[0 for _ in range(width)] for _ in range(height)] for _ in range(2)]
    
    obstacles = []
    nets = {}
    pins_by_net = {}
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('OBS'):
            coords = re.findall(r'\((\d+),\s*(\d+)\)', line)
            for x_str, y_str in coords:
                x, y = int(x_str), int(y_str)
                obstacles.append((x, y))
                # Mark as obstacle on both layers
                grid[0][y][x] = -1  
                grid[1][y][x] = -1
        elif line.startswith('net'):
            parts = line.split()
            net_name = parts[0]
            coords = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            
            
            pins = []
            for layer_str, x_str, y_str in coords:
                layer = int(layer_str) - 1  # Convert to 0-indexed layers
                x, y = int(x_str), int(y_str)
                if 0 <= x < width and 0 <= y < height:
                    pins.append(Cell(x, y, layer))
            
            if pins:
                nets[net_name] = pins
                pins_by_net[net_name] = pins
    
    return width, height, obstacles, nets, pins_by_net, grid
