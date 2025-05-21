import random
import time

# Configuration constants
VIA_COST = 10  # Cost for switching between layers
WRONG_DIRECTION_COST = 2  # Cost for routing in non-preferred direction
MAX_RIP_UP_ITERATIONS = 5  # Maximum number of rip-up iterations
RIP_UP_THRESHOLD = 3  # Number of failed nets before considering rip-up
import heapq

def select_start_pin_lowest_y_then_x(pins):
    # Sort pins by y first, then x, both ascending
    # Assumes pins have attributes .x and .y
    return min(pins, key=lambda pin: (pin.y, pin.x))

# def select_start_pin_lowest_y_then_x(pins, width, height):
#     corners = [
#         (0, 0),
#         (0, height - 1),
#         (width - 1, 0),
#         (width - 1, height - 1)
#     ]

#     # Check for exact corner match first
#     for cx, cy in corners:
#         exact_pins = [pin for pin in pins if pin.x == cx and pin.y == cy]
#         if exact_pins:
#             return exact_pins[0]  # or apply a tie-breaker if needed

#     # Fallback to closest to any corner
#     def min_corner_distance(pin):
#         return min(abs(pin.x - cx) + abs(pin.y - cy) for cx, cy in corners)

#     return min(pins, key=min_corner_distance)



def route_net(net_name, nets, pins_by_net, grid, width, height, via_cost=VIA_COST, wrong_direction_cost=WRONG_DIRECTION_COST, routed_nets=None):
    used_cells = set()

    # Track cells already used by other nets to prevent overlaps
    for other_net in routed_nets.values():
        for cell in other_net:
            used_cells.add((cell.x, cell.y, cell.layer))

    pins = nets[net_name]
    if len(pins) < 2:
        print(f"Warning: Net {net_name} has fewer than 2 pins. Skipping.")
        return []
    
    routed_path = []
    start_pin = select_start_pin_lowest_y_then_x(pins)
    sources = [start_pin]

    # sources = [pins[0]]
    # targets = pins[1:]
    targets = [p for p in pins if p != start_pin]

    
    # Temporarily mark pins on grid
    for pin in pins:
        grid[pin.layer][pin.y][pin.x] = -3
    
    congestion_map = get_congestion_map(width, height, routed_nets, grid) if routed_nets else None
    
    while targets:
        shortest_path = None
        best_source = None
        best_target = None
        
        for source in sources:
            for target in targets:
                grid[target.layer][target.y][target.x] = 0  # unmark target temporarily
                
                # path = lee_search(grid, source, target, width, height, via_cost, wrong_direction_cost, congestion_map)
                path = lee_search(grid, source, target, width, height, via_cost, wrong_direction_cost, congestion_map, used_cells)

                
                grid[target.layer][target.y][target.x] = -3  # re-mark target
                
                if path and (shortest_path is None or len(path) < len(shortest_path)):
                    shortest_path = path
                    best_source = source
                    best_target = target
        
        if not shortest_path:
            # Failed, unmark pins
            for pin in pins:
                grid[pin.layer][pin.y][pin.x] = 0
            return []
        
        routed_path.extend(shortest_path)
        
        for cell in shortest_path:
            if (cell.x, cell.y, cell.layer) not in [(p.x, p.y, p.layer) for p in pins]:
                grid[cell.layer][cell.y][cell.x] = -2
        
        sources.append(best_target)
        targets.remove(best_target)
    
    for pin in pins:
        grid[pin.layer][pin.y][pin.x] = -2
    
    # Remove duplicates while preserving order
    unique_path = []
    seen = set()
    for cell in routed_path:
        key = (cell.x, cell.y, cell.layer)
        if key not in seen:
            seen.add(key)
            unique_path.append(cell)
    
    return unique_path


def clear_net_route(net_name, routed_nets, pins_by_net, grid):
    """Clear a previously routed net from the grid."""
    if net_name not in routed_nets:
        return
        
    # Unmark the cells used by this net
    path = routed_nets[net_name]
    for cell in path:
        # Only unmark if it's not a pin
        is_pin = False
        for pin in pins_by_net.get(net_name, []):
            if cell.x == pin.x and cell.y == pin.y and cell.layer == pin.layer:
                is_pin = True
                break
        
        if not is_pin:
            grid[cell.layer][cell.y][cell.x] = 0
    
    # Remove from routed nets
    del routed_nets[net_name]
    print(f"Cleared route for {net_name}")

def select_nets_to_rip_up(failed_net_name, routed_nets, nets, width, height, grid):
    """Select nets to rip up based on congestion and conflicts."""
    # Calculate congestion
    congestion = get_congestion_map(width, height, routed_nets, grid)
    
    # Find path of the failed net (partial routing)
    failed_pins = nets[failed_net_name]
    
    # Identify nets that might be causing congestion along the potential path
    candidate_nets = []
    
    # Check all routed nets for potential conflicts
    for net_name, path in routed_nets.items():
        conflict_score = 0
        
        # Check if this net's path crosses near the pins of the failed net
        for pin in failed_pins:
            for cell in path:
                # Check if the cell is near the pin (Manhattan distance ≤ 2)
                if (cell.layer == pin.layer and 
                    abs(cell.x - pin.x) + abs(cell.y - pin.y) <= 2):
                    conflict_score += 5
        
        # Check congestion along this net's path
        path_congestion = sum(congestion[cell.layer][cell.y][cell.x] for cell in path 
                             if 0 <= cell.x < width and 0 <= cell.y < height and 0 <= cell.layer < 2)
        
        # Consider the net's length too (prefer to rip up shorter nets)
        path_length = len(path)
        
        # Calculate a score for ripping up this net
        # Higher score = more likely to be ripped up
        rip_up_score = (conflict_score + path_congestion) / (path_length + 1)
        
        # Add to candidates with score
        candidate_nets.append((net_name, rip_up_score))
    
    # Sort by score (highest first)
    candidate_nets.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top candidates (at most 3)
    return [net for net, _ in candidate_nets[:3]]

def calculate_net_bounding_box_area(pins):
    if not pins:
        return float('inf')
    min_x = min(pin.x for pin in pins)
    max_x = max(pin.x for pin in pins)
    min_y = min(pin.y for pin in pins)
    max_y = max(pin.y for pin in pins)
    return (max_x - min_x + 1) * (max_y - min_y + 1)

def net_ordering_heuristic(nets, timing_criticality=None):
    """Return a list of (net_name, pins) sorted by the custom heuristic."""
    scored_nets = []

    for net_name, pins in nets.items():
        area = calculate_net_bounding_box_area(pins)
        length_estimate = sum(
            abs(pins[i].x - pins[i + 1].x) + abs(pins[i].y - pins[i + 1].y)
            for i in range(len(pins) - 1)
        ) if len(pins) >= 2 else 0
        criticality = timing_criticality.get(net_name, 0) if timing_criticality else 0

        scored_nets.append((net_name, pins, area, length_estimate, criticality))

    # Sort by:
    # 1. Bounding box area (ascending)
    # 2. Estimated length (ascending)
    # 3. Timing criticality (descending)
    scored_nets.sort(key=lambda x: (x[2], x[3], -x[4]))

    return [(net_name, pins) for net_name, pins, _, _, _ in scored_nets]

def order_nets_by_length(nets):
    """Order nets by estimated total pin-to-pin Manhattan length ascending."""
    net_lengths = []
    for net_name, pins in nets.items():
        if len(pins) < 2:
            length = 0
        else:
            length = 0
            for i in range(len(pins) - 1):
                length += abs(pins[i].x - pins[i+1].x) + abs(pins[i].y - pins[i+1].y)
        net_lengths.append((net_name, pins, length))
    # Sort by length ascending
    net_lengths.sort(key=lambda x: x[2])
    return [(net_name, pins) for net_name, pins, _ in net_lengths]

def route_all_nets(nets, pins_by_net, grid, width, height, via_cost=VIA_COST, wrong_direction_cost=WRONG_DIRECTION_COST):
    """Route all nets with rip-up and re-route capability."""
    # Order nets by length
    sorted_nets = order_nets_by_length(nets)
    
    routed_nets = {}
    failed_nets = []
    
    # First pass: route nets in order
    for net_name, pins in sorted_nets:
        print(f"Routing {net_name}...")
        path = route_net(net_name, nets, pins_by_net, grid, width, height, 
                         via_cost, wrong_direction_cost, routed_nets)
        if path:
            routed_nets[net_name] = path
            print(f"Successfully routed {net_name} with {len(path)} cells")
        else:
            print(f"Failed to route {net_name}")
            failed_nets.append(net_name)
    
    # Rip-up and re-route if there are failed nets
    if failed_nets:
        print(f"\nRip-up and re-route phase - {len(failed_nets)} failed nets")
        return rip_up_and_reroute(failed_nets, nets, pins_by_net, grid, width, height, 
                                  routed_nets, via_cost, wrong_direction_cost)
    
    return routed_nets


def rip_up_and_reroute(failed_nets, nets, pins_by_net, grid, width, height, 
                       routed_nets, via_cost=VIA_COST, wrong_direction_cost=WRONG_DIRECTION_COST):
    """Perform rip-up and re-route for failed nets."""
    iteration = 0
    max_iterations = MAX_RIP_UP_ITERATIONS
    
    while failed_nets and iteration < max_iterations:
        iteration += 1
        print(f"\nRip-up iteration {iteration}/{max_iterations}")
        
        # Process each failed net
        current_failed = failed_nets.copy()
        failed_nets = []
        
        for failed_net_name in current_failed:
            # Select nets to rip up
            nets_to_rip = select_nets_to_rip_up(failed_net_name, routed_nets, nets, width, height, grid)
            
            if not nets_to_rip:
                print(f"No candidates for rip-up found for {failed_net_name}")
                failed_nets.append(failed_net_name)
                continue
            
            print(f"Ripping up nets for {failed_net_name}: {', '.join(nets_to_rip)}")
            
            # Clear the selected nets
            for net_name in nets_to_rip:
                clear_net_route(net_name, routed_nets, pins_by_net, grid)
            
            # Try routing the failed net again
            print(f"Retrying route for {failed_net_name}...")
            path = route_net(failed_net_name, nets, pins_by_net, grid, width, height, 
                             via_cost, wrong_direction_cost, routed_nets)
            
            if path:
                routed_nets[failed_net_name] = path
                print(f"Successfully routed {failed_net_name} after rip-up")
                
                # Re-route the ripped-up nets
                for ripped_net in nets_to_rip:
                    print(f"Re-routing {ripped_net}...")
                    ripped_path = route_net(ripped_net, nets, pins_by_net, grid, width, height, 
                                            via_cost, wrong_direction_cost, routed_nets)
                    if ripped_path:
                        routed_nets[ripped_net] = ripped_path
                        print(f"Re-routed {ripped_net} successfully")
                    else:
                        print(f"Failed to re-route {ripped_net}")
                        failed_nets.append(ripped_net)
            else:
                print(f"Still failed to route {failed_net_name} after rip-up")
                failed_nets.append(failed_net_name)
                
                # Put back the original routes that were ripped up
                for net_name in nets_to_rip:
                    if net_name not in routed_nets:
                        print(f"Re-routing {net_name}...")
                        path = route_net(net_name, nets, pins_by_net, grid, width, height, 
                                         via_cost, wrong_direction_cost, routed_nets)
                        if path:
                            routed_nets[net_name] = path
                            print(f"Re-routed {net_name} successfully")
        
        # If we've made no progress, try randomizing the order
        if len(failed_nets) == len(current_failed):
            random.shuffle(failed_nets)
    
    # Final summary
    if failed_nets:
        print(f"\nAfter rip-up and re-route, {len(failed_nets)} nets still failed:")
        for net in failed_nets:
            print(f"  - {net}")
    else:
        print("\nAll nets routed successfully after rip-up and re-route!")
    
    return routed_nets
