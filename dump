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
    return routed_path
