from collections import deque
import time
import itertools
import matplotlib.patches as mpatches

class Cell:
    def __init__(self, x, y, layer):
        self.x = x
        self.y = y
        self.layer = layer
    
    def __repr__(self):
        return f"({self.layer}, {self.x}, {self.y})"
    
    def __eq__(self, other):
        if not isinstance(other, Cell):
            return False
        return self.x == other.x and self.y == other.y and self.layer == other.layer
    
    def __hash__(self):
        return hash((self.x, self.y, self.layer))
    
    def __lt__(self, other):
        # For sorting in priority queue
        if not isinstance(other, Cell):
            return NotImplemented
        # Sort by layer first, then x, then y
        return (self.layer, self.x, self.y) < (other.layer, other.x, other.y)
    
    def __gt__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented
        return (self.layer, self.x, self.y) > (other.layer, other.x, other.y)
    
    def __le__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented
        return (self.layer, self.x, self.y) <= (other.layer, other.x, other.y)
    
    def __ge__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented
        return (self.layer, self.x, self.y) >= (other.layer, other.x, other.y)

def lee_search(grid, start, end, width, height, via_cost, wrong_direction_cost, congestion_map=None, used_cells=None):
    """Lee's algorithm with overlap avoidance and congestion-aware routing."""

    if start == end:
        return [start]

    moves = [
        (1, 0, 0, 1),    # Right
        (-1, 0, 0, 1),   # Left
        (0, 1, 0, wrong_direction_cost),   # Down
        (0, -1, 0, wrong_direction_cost),  # Up
    ]

    via_moves = []
    if start.layer == 0:
        via_moves.append((0, 0, 1, via_cost))
    elif start.layer == 1:
        via_moves.append((0, 0, -1, via_cost))

    def heuristic(cell):
        return abs(cell.x - end.x) + abs(cell.y - end.y)

    queue = [(heuristic(start), 0, start, [])]
    visited = set()

    while queue:
        queue.sort(key=lambda x: x[0])
        _, g_score, current, path = queue.pop(0)

        if current == end:
            return path + [current]

        cell_key = (current.x, current.y, current.layer)
        if cell_key in visited:
            continue
        visited.add(cell_key)

        for dx, dy, dlayer, base_cost in moves + via_moves:
            new_layer = current.layer + dlayer
            if not (0 <= new_layer <= 1):
                continue

            new_x = current.x + dx
            new_y = current.y + dy
            if not (0 <= new_x < width and 0 <= new_y < height):
                continue

            if grid[new_layer][new_y][new_x] < 0:
                continue

            new_cell = Cell(new_x, new_y, new_layer)
            new_cell_key = (new_x, new_y, new_layer)

            # Skip used cells (unless it's the end)
            if used_cells and new_cell_key in used_cells and new_cell != end:
                continue

            if new_cell_key in visited:
                continue

            cost = base_cost
            if congestion_map:
                cost += congestion_map[new_layer][new_y][new_x] * 2  # Heavier penalty for congested cells

            new_g = g_score + cost
            new_f = new_g + heuristic(new_cell)
            queue.append((new_f, new_g, new_cell, path + [current]))

    return []  # No path found


# def a_star_search(grid, start, end, width, height, via_cost, wrong_direction_cost, congestion_map=None):
#     """A* search algorithm optimized for layer preferences and via costs.
    
#     This is a wrapper for lee_search that follows the original function structure
#     but uses the Lee algorithm underneath (which is similar to A* for this application).
#     """
#     return lee_search(grid, start, end, width, height, via_cost, wrong_direction_cost, congestion_map)

def a_star_search(grid, start, end, width, height, via_cost, wrong_direction_cost, congestion_map=None, used_cells=None):
    return lee_search(grid, start, end, width, height, via_cost, wrong_direction_cost, congestion_map, used_cells)


def get_congestion_map(width, height, routed_nets, grid):
    """Calculate congestion for each grid cell."""
    congestion = [[[0 for _ in range(width)] for _ in range(height)] for _ in range(2)]
    
    # Count how many nets pass through each cell
    for net_name, path in routed_nets.items():
        for cell in path:
            if 0 <= cell.x < width and 0 <= cell.y < height and 0 <= cell.layer < 2:
                if grid[cell.layer][cell.y][cell.x] != -1:  # Not an obstacle
                    congestion[cell.layer][cell.y][cell.x] += 1
    
    return congestion
