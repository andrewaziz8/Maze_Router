def write_output(routed, output_path):
    with open(output_path, 'w') as f:
        for net, path in routed.items():
            line = f"{net} " + " ".join(f"(1, {x}, {y})" for (x, y) in path)
            f.write(line + "\n")
