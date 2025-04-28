# Project: CS603 - Quadtree Decomposition and Adaptive Triangular Mesh Generation

---

## Overview

This project addresses two computational geometry problems:

- **Part (a)**: Implementing a **quadtree decomposition** of a point set in 2D.
- **Part (b)**: Generating an **adaptive triangular mesh** for a set of disjoint octilinear polygons.

Both parts use efficient spatial decomposition strategies to ensure correctness and optimal performance.

---

## Problem Statements

### Part (a): Quadtree Decomposition

- **Input**: A finite set \( P \) of points in ℝ².
- **Output**: A quadtree decomposition of the bounding square of \( P \), with each leaf cell containing at most a constant number of points.

### Part (b): Adaptive Triangular Mesh

- **Input**: A set \( S \) of disjoint, octilinear polygons (edges axis-aligned or at 45° angles), all contained within a square \( Q \).
- **Output**: An adaptive triangular mesh that conforms to \( S \).
- **Performance Target**: The mesh should have \( O(p(S)log U) \) triangles, where \( p(S) \) is the total perimeter and \( U \) is the bounding square size.
- **Hint Used**: Compressed quadtree-based refinement.

---

## How to Run the Code

### Part (a): Quadtree Decomposition

1. **Navigate** to the `Quadtree/` directory:
   ```bash
   cd Quadtree
   ```

2. **Run the script**:
   ```bash
   python3 quadtree.py
   ```
   or if using Windows:
   ```bash
   py quadtree.py
   ```

3. **Choose input mode**:
   - **Random (0)**: 
     - You will be asked to enter the total number of random distinct points to generate.
     - The program then creates \( n \) points and constructs the corresponding quadtree.

   - **Manual (1)**:
     - Fill the `input.txt` file with your points (one point per line, space-separated, e.g.):
       ```
       2 5
       3 8
       9 4
       ```
     - Ensure points are **distinct**.
     - The code reads your input and generates the quadtree decomposition.

### Part (b): Adaptive Triangulation

1. **Navigate** to the `Adaptive traingulation/` directory:
   ```bash
   cd "Adaptive traingulation"
   ```

2. **Run the script**:
   ```bash
   python3 triangulate_v2.0.py
   ```
   or on Windows:
   ```bash
   py triangulate_v2.0.py
   ```

3. **Select a testcase**:
   - Upon running, the code displays a list of available polygon shapes:
     ```
     L-shape : 0
     Z-shape : 1
     Cross   : 2
     Stairs  : 3
     ...
     Combination of 3 distinct polygons : 8
     ```
   - Enter the corresponding number for the desired testcase.

4. **Output**:
   - The program generates and displays the triangulated mesh for the chosen polygon(s).

---

## Code Working Summary

### Part (a): Quadtree

- Recursively splits the bounding box into four quadrants.
- Stops splitting when the number of points within a cell falls below a fixed threshold.
- Useful for spatial indexing and efficient geometric operations.

### Part (b): Adaptive Triangulation

- Constructs a compressed quadtree that refines regions near polygon edges.
- Adapts the triangulation density based on geometry complexity.
- Ensures fewer triangles while maintaining boundary conformity.
- Handles multiple disjoint polygons efficiently.

---

## Dependencies

- Python 3.x
- Standard libraries only (`math`, `os`, `random`)

No external installations are required.

---

## Notes

- Read the report for clear understanding of the code and algorithms used.
- For best results, ensure distinct points and correct formatting in manual inputs.
- Additional testcases for new polygons can be added in the `testcases/` folder, Also set the appropriate boundaries(U) as well.

---
