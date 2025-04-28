import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Node():
    def __init__(self, x0, y0, w, h, points):
        self.x0 = x0
        self.y0 = y0
        self.width = w
        self.height = h
        self.points = points
        self.children = []

    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_points(self):
        return self.points
    


def recursive_subdivide(node, k):
   if len(node.points)<=k:
       return
   
   w_ = float(node.width/2)
   h_ = float(node.height/2)

   p = contains(node.x0, node.y0, w_, h_, node.points)
   x1 = Node(node.x0, node.y0, w_, h_, p)
   recursive_subdivide(x1, k)

   p = contains(node.x0, node.y0+h_, w_, h_, node.points)
   x2 = Node(node.x0, node.y0+h_, w_, h_, p)
   recursive_subdivide(x2, k)

   p = contains(node.x0+w_, node.y0, w_, h_, node.points)
   x3 = Node(node.x0 + w_, node.y0, w_, h_, p)
   recursive_subdivide(x3, k)

   p = contains(node.x0+w_, node.y0+h_, w_, h_, node.points)
   x4 = Node(node.x0+w_, node.y0+h_, w_, h_, p)
   recursive_subdivide(x4, k)

   node.children = [x1, x2, x3, x4]
   
   
def contains(x, y, w, h, points):
   pts = []
   for point in points:
       if point.x >= x and point.x <= x+w and point.y>=y and point.y<=y+h:
           pts.append(point)
   return pts


def find_children(node):
   if not node.children:
       return [node]
   else:
       children = []
       for child in node.children:
           children += (find_children(child))
   return children


class QTree():
    def __init__(self, k, n, points):
        self.points = points
        self.threshold = k

        min_x = min(p.x for p in self.points)
        max_x = max(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_y = max(p.y for p in self.points)

        side_len = max(max_x-min_x, max_y-min_y)
        self.root = Node(min_x, min_y, side_len, side_len, self.points)

    
    def get_points(self):
        return self.points
    
    def subdivide(self):
        recursive_subdivide(self.root, self.threshold)
    
    def graph(self):
        fig = plt.figure(figsize=(12, 8))
        plt.title("Quadtree")
        c = find_children(self.root)
        print("Number of segments: %d" %len(c))
        areas = set()
        for el in c:
            areas.add(el.width*el.height)
        print("Minimum segment area: %.3f units" %min(areas))
        for n in c:
            plt.gcf().gca().add_patch(patches.Rectangle((n.x0, n.y0), n.width, n.height, fill=False))
        x = [point.x for point in self.points]
        y = [point.y for point in self.points]
        plt.plot(x, y, 'ro') # plots the points as red dots
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
        return
    
choice = int(input("Please Enter the input type, Random(0) or Manual(1)\nIf Manual, make sure your input is stored in input.txt file : "))
k = 1 
points = []
n = 0
if choice == 0:
    n = int(input("Enter the no. of points in Quadtree: "))

    set_points = set()
    while len(set_points) < n:
        x = random.randint(0, 25)
        y = random.randint(0, 25)
        set_points.add((x, y))
    
    points = [Point(x, y) for x, y in set_points]

else:
    file = f"input.txt"
    try:
        with open(file, 'r') as f:
            for line in f:
                n += 1
                x, y = map(float, line.strip().split())
                points.append(Point(x, y))
    except FileNotFoundError:
        print(f"File '{file}' not found.")
        exit()
    except ValueError as e:
        print(f"Error reading file '{file}': {e}")
        exit()


QuadTree = QTree(k,n,points)
QuadTree.subdivide()
QuadTree.graph()