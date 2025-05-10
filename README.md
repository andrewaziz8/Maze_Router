# Automated Grid-Based Net Routing using Lee's Algorithm

## Objective
This project implements a grid-based routing system using **Lee's algorithm** to connect electronic components (pins) on a 2D grid while avoiding obstacles. It reads a structured input file, computes optimal paths for each net, and generates both a text-based and visual output showing the routing.

## Contributors
- Kareem Sayed  
- Andrew Aziz  
- Shaza Ali  
- Adham Hassan  

## Input Format (Abstract)
- The first line defines the grid size:  
  `WIDTHxHEIGHT` (e.g., `8x8`)
- Following lines include:
  - Obstacles: `OBS (x, y)`
  - Nets: `netName (layer, x, y) (layer, x, y) ...`

## Output Format (Abstract)
- A routed path per net in this format:  
  `netName (1, x1, y1) (1, x2, y2) ... (1, xn, yn)`
- A matplotlib plot is also generated to visually represent the routing layout, including:
  - Obstacles (black squares)
  - Pins (red stars)
  - Routed paths (blue lines)

## Usage
```python
main("input3.txt", "output.txt")
visualize_routing("output.txt", "input3.txt")
