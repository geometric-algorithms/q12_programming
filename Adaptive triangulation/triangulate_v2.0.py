import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y
        
    def __hash__(self):
        return hash((self.x, self.y))

class Polygon:
    def __init__(self, vertices):
        """
        vertices: list of Point objects defining the polygon
        """
        self.vertices = vertices
        
    def intersects_square(self, x0, y0, width, height):
        square_corners = [
            (x0, y0),
            (x0 + width, y0),
            (x0 + width, y0 + height),
            (x0, y0 + height)
        ]

        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % len(self.vertices)]
            if self._line_square_intersection(v1.x, v1.y, v2.x, v2.y, x0, y0, width, height):
                return True

        if all(self._point_in_polygon(x, y) for (x, y) in square_corners):
            return True

        for v in self.vertices:
            if x0 <= v.x <= x0 + width and y0 <= v.y <= y0 + height:
                return True

        return False


    def _line_square_intersection(self, x1, y1, x2, y2, sq_x, sq_y, sq_w, sq_h):
        """Check if line segment intersects with square"""
        
        # Check intersection with each edge of the square
        if self._line_segment_intersection(x1, y1, x2, y2, sq_x, sq_y, sq_x + sq_w, sq_y): return True
        if self._line_segment_intersection(x1, y1, x2, y2, sq_x + sq_w, sq_y, sq_x + sq_w, sq_y + sq_h): return True
        if self._line_segment_intersection(x1, y1, x2, y2, sq_x + sq_w, sq_y + sq_h, sq_x, sq_y + sq_h): return True
        if self._line_segment_intersection(x1, y1, x2, y2, sq_x, sq_y + sq_h, sq_x, sq_y): return True
        return False
    
    def _line_segment_intersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """Check if two line segments intersect"""
        # Calculate direction vectors
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x4 - x3
        dy2 = y4 - y3
        
        det = dx1 * dy2 - dy1 * dx2
        
        if det == 0:
            return False  # Parallel lines
            
        s = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / det
        t = ((x3 - x1) * dy1 - (y3 - y1) * dx1) / det
        
        return 0 <= s <= 1 and 0 <= t <= 1


    
    def _point_in_polygon(self, x, y):
        """Check if point is inside polygon using ray casting algorithm"""
        inside = False
        n = len(self.vertices)
        j = n - 1
        
        for i in range(n):
            vi = self.vertices[i]
            vj = self.vertices[j]
            
            if ((vi.y > y) != (vj.y > y)) and (x < (vj.x - vi.x) * (y - vi.y) / (vj.y - vi.y) + vi.x):
                inside = not inside
                
            j = i
            
        return inside

class QuadTreeNode:
    def __init__(self, x0, y0, width, height, depth=0, parent=None):
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.depth = depth
        self.parent = parent
        self.children = []
        self.is_leaf = True
        
    def subdivide(self):
        if not self.is_leaf:
            return
            
        w_half = self.width / 2
        h_half = self.height / 2
        
        # Create four children (NW, NE, SW, SE)
        nw = QuadTreeNode(self.x0, self.y0 + h_half, w_half, h_half, self.depth + 1, self)
        ne = QuadTreeNode(self.x0 + w_half, self.y0 + h_half, w_half, h_half, self.depth + 1, self)
        sw = QuadTreeNode(self.x0, self.y0, w_half, h_half, self.depth + 1, self)
        se = QuadTreeNode(self.x0 + w_half, self.y0, w_half, h_half, self.depth + 1, self)
        
        self.children = [nw, ne, sw, se]
        self.is_leaf = False
        
        return self.children

class QuadTree:
    def __init__(self, x0, y0, width, height, max_depth=10, min_size=1):
        self.root = QuadTreeNode(x0, y0, width, height)
        self.max_depth = max_depth
        self.min_size = min_size
        
    def create_quadtree(self, polygons, U):
        self._recursive_subdivide(self.root, polygons, U)
        return self

    def _recursive_subdivide(self, node, polygons, U):
       
        min_size = 1
        coarse_threshold = U//4
        
        boundary_intersection = self.check_if_intersects_boundary(node, polygons)
        
        if boundary_intersection:
            if node.width > min_size:  
                children = node.subdivide()
                for child in children:
                    self._recursive_subdivide(child, polygons, U)
        elif node.width > coarse_threshold:
            children = node.subdivide()
            for child in children:
                self._recursive_subdivide(child, polygons, U)


    def check_if_intersects_boundary(self, node, polygons):
        """Check if node intersects with any polygon boundary"""
        for polygon in polygons:
            for i in range(len(polygon.vertices)):
                v1 = polygon.vertices[i]
                v2 = polygon.vertices[(i + 1) % len(polygon.vertices)]
                
                if polygon._line_square_intersection(v1.x, v1.y, v2.x, v2.y, 
                                                node.x0, node.y0, node.width, node.height):
                    return True
        
        return False

    
    def balance(self):
        """Ensure 2:1 balance between adjacent leaf nodes (full convergence)"""
        changed = True
        while changed:
            changed = False
            leaves = self.get_leaves()
            queue = deque(leaves)

            while queue:
                node = queue.popleft()
                neighbors = self.find_neighbors(node)

                for neighbor in neighbors:
                    if neighbor.is_leaf and neighbor.depth < node.depth - 1:
                        children = neighbor.subdivide()
                        queue.extend(children)  
                        changed = True  
        return self

    
    def find_neighbors(self, node):
        """Find all neighboring nodes at the same or higher level"""
        neighbors = []
        
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (-1, 1), (1, -1), (-1, -1)
        ]
        
        for dx, dy in directions:
            check_x = node.x0 + (0.5 + dx * 0.6) * node.width
            check_y = node.y0 + (0.5 + dy * 0.6) * node.height
            
            neighbor = self._find_leaf_containing_point(check_x, check_y)
            
            if neighbor and neighbor != node:
                neighbors.append(neighbor)
        
        return neighbors
    
    def _find_leaf_containing_point(self, x, y):
        """Find the leaf node containing the given point"""
        if not (self.root.x0 <= x <= self.root.x0 + self.root.width and 
                self.root.y0 <= y <= self.root.y0 + self.root.height):
            return None
            
        return self._recursive_find_leaf(self.root, x, y)
    
    def _recursive_find_leaf(self, node, x, y):
        """Recursively find leaf node containing point"""
        if node.is_leaf:
            return node
            
        mid_x = node.x0 + node.width / 2
        mid_y = node.y0 + node.height / 2
        
        if x < mid_x:
            if y < mid_y:
                return self._recursive_find_leaf(node.children[2], x, y)  # SW
            else:
                return self._recursive_find_leaf(node.children[0], x, y)  # NW
        else:
            if y < mid_y:
                return self._recursive_find_leaf(node.children[3], x, y)  # SE
            else:
                return self._recursive_find_leaf(node.children[1], x, y)  # NE
    
    def get_leaves(self):
        """Get all leaf nodes in the quadtree"""
        leaves = []
        self._collect_leaves(self.root, leaves)
        return leaves
    
    def _collect_leaves(self, node, leaves):
        """Recursively collect all leaf nodes"""
        if node.is_leaf:
            leaves.append(node)
        else:
            for child in node.children:
                self._collect_leaves(child, leaves)

class Mesh:
    def __init__(self):
        self.vertices = []  
        self.triangles = []  

    def triangulate_quadtree(self, quadtree, polygons):
        # Get all leaf nodes
        leaves = quadtree.get_leaves()
        
        vertex_map = {} 
        
        for node in leaves:
            corners = [(node.x0, node.y0),
                    (node.x0 + node.width, node.y0),
                    (node.x0 + node.width, node.y0 + node.height),
                    (node.x0, node.y0 + node.height)]
            for x, y in corners:
                if (x, y) not in vertex_map:
                    vertex_map[(x, y)] = len(self.vertices)
                    self.vertices.append(Point(x, y))
        
        for node in leaves:
            # Get corner vertices
            sw = vertex_map[(node.x0, node.y0)]
            se = vertex_map[(node.x0 + node.width, node.y0)]
            ne = vertex_map[(node.x0 + node.width, node.y0 + node.height)]
            nw = vertex_map[(node.x0, node.y0 + node.height)]
            
            cell_x = round(node.x0)
            cell_y = round(node.y0)
            
            # Check if interior is intersected by polygon
            interior_intersected = self.check_if_interior_intersected(node, polygons)
            
            if interior_intersected:
                if (cell_x + cell_y) % 2 == 0:
                    self.triangles.append((sw, se, ne))
                    self.triangles.append((sw, ne, nw))
                else:
                    self.triangles.append((sw, se, nw))
                    self.triangles.append((se, ne, nw))

            elif self.vertices_only_add_corners(node, polygons):
                if (cell_x + cell_y) % 2 == 0:
                    self.triangles.append((sw, se, ne))
                    self.triangles.append((sw, ne, nw))
                else:
                    self.triangles.append((sw, se, nw))
                    self.triangles.append((se, ne, nw))
            else:
                # Create Steiner point and connect to all boundary vertices
                center_x = node.x0 + node.width/2
                center_y = node.y0 + node.height/2
                
                if (center_x, center_y) not in vertex_map:
                    vertex_map[(center_x, center_y)] = len(self.vertices)
                    self.vertices.append(Point(center_x, center_y))
                
                center = vertex_map[(center_x, center_y)]
                
                self.triangles.append((center, sw, se))
                self.triangles.append((center, se, ne))
                self.triangles.append((center, ne, nw))
                self.triangles.append((center, nw, sw))

    def check_if_interior_intersected(self, node, polygons):
        """Check if the interior of the node is intersected by any polygon"""
        interior_x = node.x0 + node.width/4
        interior_y = node.y0 + node.height/4
        interior_width = node.width/2
        interior_height = node.height/2
        
        for polygon in polygons:
            if polygon.intersects_square(interior_x, interior_y, interior_width, interior_height):
                return True
        return False

    def vertices_only_add_corners(self, node, polygons):
        """Check if vertices only add corners (no interior polygon vertices)"""
        for polygon in polygons:
            for vertex in polygon.vertices:
                if (node.x0 < vertex.x < node.x0 + node.width and 
                    node.y0 < vertex.y < node.y0 + node.height):
                    return False
        return True
   

    def plot(self, polygons=None):
        """Plot the triangular mesh"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Plot triangles
        for i, j, k in self.triangles:
            v1 = self.vertices[i]
            v2 = self.vertices[j]
            v3 = self.vertices[k]
            
            triangle = patches.Polygon([(v1.x, v1.y), (v2.x, v2.y), (v3.x, v3.y)], 
                                       fill=False, edgecolor='blue', linewidth=0.5)
            ax.add_patch(triangle)
        
        # Plot vertices
        x = [v.x for v in self.vertices]
        y = [v.y for v in self.vertices]
        ax.scatter(x, y, color='red', s=6)
        
        # Plot polygons if provided
        if polygons:
            for polygon in polygons:
                x = [v.x for v in polygon.vertices]
                y = [v.y for v in polygon.vertices]
                x.append(x[0])  # Close the polygon
                y.append(y[0])
                ax.plot(x, y, color='green', linewidth=2)

        
        ax.set_aspect('equal')
        ax.set_title('Triangular Mesh')
        plt.grid(True)
        plt.show()

def create_mesh(polygons, U):
    
    # Create quadtree
    quadtree = QuadTree(0, 0, U, U)
    quadtree.create_quadtree(polygons, U)
    
    # Balance quadtree
    quadtree.balance()
    
    # Triangulate quadtree
    mesh = Mesh()
    mesh.triangulate_quadtree(quadtree, polygons)
    
    return mesh

if __name__ == "__main__":

    print("Please choose your choice of input from below: ")
    print("**********************************************\n")
   
    dictionary = {
        0 : "L-shape",   
        1 : "Z-shape",  
        2 : "Cross",  
        3 : "Stairs",    
        4 : "Key Shape", 
        5 : "U-shape",   
        6 : "Octagon",  
        7 : "Rectangle",  
        8 : "Combination of 3 disjoint polygons "
        }
    
    for key in dictionary:
        print(f"{dictionary[key]} : {key}")

    print("  ")

    cnt = int(input("Please enter your choice: "))

    if cnt > 8 or cnt < 0:
        print("Please enter valid input!!!")
        exit(0)
    
    if cnt != 8:
        U = 16
        if cnt == 7:
            U = 32
        points = []
        with open(f"testcases/{dictionary[cnt]}.txt",'r') as f:
            for line in f:
                x, y = map(int, line.split())
                points.append(Point(x, y))
        polygon = Polygon(points)
        mesh = create_mesh([polygon], U)
        mesh.plot([polygon])

    else:
        U = 64
        polygons = []
        files = ["poly1.txt","poly2.txt","poly3.txt"]
        for file in files:
            points = []
            with open(f"testcases/"+file,'r') as f:
                for line in f:
                    x, y = map(int, line.split())
                    points.append(Point(x, y))
            polygon = Polygon(points)
            polygons.append(polygon)
        mesh = create_mesh(polygons, U)
        mesh.plot(polygons)
        
        
