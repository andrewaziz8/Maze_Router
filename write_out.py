def write_output(routed_nets, output_path):
    """Write the routing results to an output file.
    
    Args:
        routed_nets: Dictionary of net names to routed paths
        output_path: Path to write the output file
    """
    with open(output_path, 'w') as f:
        for net_name, path in routed_nets.items():
        # for net_name, path in routed_nets:
            if path:  # Only write successfully routed nets
                # Convert layer from 0-indexed back to 1-indexed for output
                # Format: net_name (layer1, x1, y1) (layer2, x2, y2) ...
                line = f"{net_name}"
                
                # Add each coordinate in the path
                for cell in path:
                    # Convert from 0-based to 1-based layer indexing
                    line += f" ({cell.layer + 1}, {cell.x}, {cell.y})"
                    
                f.write(line + "\n")
    
    print(f"Routing complete. Output saved to {output_path}")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import itertools
import re

def visualize_routing(output_file, input_file):
    width, height, obstacles, nets, pins_by_net, grid = parse_input(input_file)

    width += 1
    height += 1

    with open(output_file, 'r') as f:
        lines = f.readlines()

    fig, axs = plt.subplots(1, 2, figsize=(24, 12))
    layer_names = ['Horizontal Layer (Layer 1)', 'Vertical Layer (Layer 2)']
    base_colors = ['blue', 'green', 'orange', 'purple', 'red', 'brown']
    colors = itertools.cycle(base_colors)

    routes_by_layer = {1: {}, 2: {}}
    pin_layer_presence = {1: set(), 2: set()}
    full_routes_by_net = {}

    # Map each net to a color (keep this to show in legend)
    net_color_map = {}

    for line in lines:
        net_name = line.split()[0]
        route_parts = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
        route_cells = [(int(z), int(x), int(y)) for (z, x, y) in route_parts if int(z) in [1, 2]]

        for z, x, y in route_cells:
            routes_by_layer.setdefault(z, {}).setdefault(net_name, []).append((x, y))
            pin_layer_presence[z].add((x, y))

        full_routes_by_net[net_name] = route_cells

    # Assign colors to nets, preserving order from nets dict if possible
    for net_name in nets:
        net_color_map[net_name] = next(colors)

    fig_width, fig_height = fig.get_size_inches()
    cell_size_px = min((fig_width * fig.dpi) / width, (fig_height * fig.dpi) / height)
    font_size = max(6, int(0.4 * cell_size_px))
    marker_size = max(30, int(0.25 * cell_size_px ** 2))

    lowest_pin_per_net = {}
    for net_name, pins in pins_by_net.items():
        if pins:
            sorted_pins = sorted(pins, key=lambda p: (p.y, p.x))
            lowest_pin_per_net[net_name] = sorted_pins[0]
        else:
            lowest_pin_per_net[net_name] = None

    vias_all_layers = set()
    for net_name, route_cells in full_routes_by_net.items():
        for i in range(len(route_cells) - 1):
            z1, x1, y1 = route_cells[i]
            z2, x2, y2 = route_cells[i + 1]
            if (z1 != z2) and (x1 == x2) and (y1 == y2):
                vias_all_layers.add((x1, y1))

    for idx, layer in enumerate([1, 2]):
        ax = axs[idx]
        ax.set_title(layer_names[idx], fontsize=font_size + 4)
        ax.set_xlim(-0.5, width - 0.5)
        ax.set_ylim(-0.5, height - 0.5)
        ax.set_xticks(range(width))
        ax.set_yticks(range(height))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_xlabel("")
        ax.set_ylabel("")

        if not routes_by_layer[layer]:
            continue

        if obstacles:
            obs_xs = [x + 0.5 for x, _ in obstacles]
            obs_ys = [y + 0.5 for _, y in obstacles]
            ax.scatter(obs_xs, obs_ys, marker='s', s=marker_size * 1.5, color='black', zorder=1)

        for net_name, coords in routes_by_layer.get(layer, {}).items():
            color = net_color_map.get(net_name, 'black')
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                if abs(x1 - x2) + abs(y1 - y2) == 1:
                    ax.plot([x1 + 0.5, x2 + 0.5], [y1 + 0.5, y2 + 0.5], '-', color=color, linewidth=2)
                    ax.scatter([x1 + 0.5, x2 + 0.5], [y1 + 0.5, y2 + 0.5], s=marker_size, color=color, alpha=0.5)

        for net_name, pins in pins_by_net.items():
            if pins:
                lowest_pin = lowest_pin_per_net.get(net_name)
                for pin in pins:
                    x, y = pin.x, pin.y
                    if (x, y) not in pin_layer_presence[layer]:
                        continue
                    x_centered = x + 0.5
                    y_centered = y + 0.5
                    if pin == lowest_pin:
                        ax.text(x_centered, y_centered, 'S', ha='center', va='center', color='white',
                                fontsize=font_size, bbox=dict(facecolor='red', edgecolor='black', boxstyle='circle'),
                                zorder=10)
                    else:
                        ax.scatter(x_centered, y_centered, marker='*', s=marker_size * 2, color='red',
                                   edgecolors='black', zorder=10)

        if vias_all_layers:
            via_xs = [x + 0.5 for x, _ in vias_all_layers]
            via_ys = [y + 0.5 for _, y in vias_all_layers]
            ax.scatter(via_xs, via_ys, marker='o', s=marker_size * 1.5, color='cyan', edgecolors='blue', zorder=8)

    # Create legend handles for nets:
    net_handles = [mpatches.Patch(color=color, label=net_name) for net_name, color in net_color_map.items()]

    # Create legend handles for other items:
    other_handles = [
        mpatches.Patch(color='black', label='Obstacle'),
        mpatches.Patch(color='cyan', label='Via'),
        mpatches.Patch(color='red', label='Start Pin (S)'),
    ]

    # Add global legend below plots with more bottom space
    plt.tight_layout(rect=[0, 0.12, 1, 1])  # leave more room below for legend
    fig.subplots_adjust(bottom=0.15)  # extra bottom margin

    # Show two legends in one place, stacked vertically
    legend1 = fig.legend(handles=net_handles, loc='lower center', ncol=len(net_handles),
                         fontsize=font_size + 2, frameon=True, bbox_to_anchor=(0.5, 0.05))
    legend2 = fig.legend(handles=other_handles, loc='lower center', ncol=len(other_handles),
                         fontsize=font_size + 2, frameon=True, bbox_to_anchor=(0.5, 0.01))

    # Add both legends to figure
    fig.add_artist(legend1)
    fig.add_artist(legend2)

    plt.show()




def main(input_file, output_file, generate_visualization=True):
    import os
    import time
    from datetime import datetime

    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return 1

    print(f"\nMaze Router started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Reading input from: {input_file}")
    start_time = time.time()

    try:
        # Parse input file
        width, height, obstacles, nets, pins_by_net, grid = parse_input(input_file)
        print(f"\nGrid size: {width}x{height}")
        print(f"Number of obstacles: {len(obstacles)}")
        print(f"Number of nets to route: {len(nets)}")

        # Route all nets
        print("\nRouting nets...")
        routed_nets = route_all_nets(nets, pins_by_net, grid, width, height)

        # Count successful routes
        successful_routes = len([net for net, path in routed_nets.items() if path])
        # successful_routes = len([net for net, path in routed_nets if path])

        print(f"\nRouting completed: {successful_routes}/{len(nets)} nets routed successfully")

        # Write output file
        write_output(routed_nets, output_file)

        # Generate visualization (optional)
        if generate_visualization:
            print("\nGenerating visualizations...")
            visualize_routing(output_file, input_file)

        # Print timing summary
        elapsed_time = time.time() - start_time
        print(f"\nTotal runtime: {elapsed_time:.2f} seconds")

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0
