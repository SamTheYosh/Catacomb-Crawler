import pygame

from util import *
from circles import *

class Graph:
    # Stores nodes and the edges between them.
    def __init__(self, app):
        self.app = app
        self.nodes = []

    def add_node(self, node):
        # Adds a node to self.nodes.
        self.nodes.append(node)

    def add_edge(self, node1, node2):
        # Connects two nodes with an edge.
        node1.add_neighbour(node2)
        node2.add_neighbour(node1)

    def add_node_with_edge_to_last(self, node):
        # Creates an edge between the given node and the
        # closest node in self.nodes.
        self.add_edge(node, self.nodes[-1])
        self.add_node(node)

    def add_node_with_edge_close_enough(self, node, range = None):
        # Creates an edge between the given node and any nodes
        # in self.nodes that are within a certain distance.
        if range is None:
            range = 100
        
        for n in self.nodes:
            if n.pos.distance_to(node.pos) <= range:
                self.add_edge(n, node)
        self.add_node(node)

    def add_nodes_and_edges(self, nodes, edges):
        # Takes a list of node positions and a list of tuples
        # of nodes to connect with edges. Adds all of the nodes
        # to self.nodes and creates all of the edges.
        nodes = [GraphNode(self.app, node) for node in nodes]

        for node in nodes:
            self.add_node(node)
        
        for index1, index2 in edges:
            self.add_edge(nodes[index1], nodes[index2])

    def remove_node(self, index):
        # Removes a node, and makes sure all of its
        # neighbours remove it as a neighbour.
        nodeToRemove = self.nodes[index]
        for node in self.nodes:
            node.remove_neighbour(nodeToRemove)
        self.nodes.pop(index)
    
    def reset_costs(self):
        # Resets the g and h cost values of all nodes in
        # self.nodes.
        for node in self.nodes:
            node.reset_costs()

class GraphNode:
    # Used by Graphs.
    # Also stores some information relating to A* pathfinding.
    def __init__(self, app, pos):
        self.app = app

        self.pos = pos
        self.neighbours = []
        # g and h cost are values used in A* pathfinding.
        self.g = 0
        self.h = 0
        # self.parent is used to retrace the path found using
        # A* pathfinding.
        self.parent = None

    def add_neighbour(self, node):
        # Adds a node as a neighbour of this node.
        # This is used to create edges between nodes.
        if not node in self.neighbours:
            self.neighbours.append(node)

    def remove_neighbour(self, node):
        # Removes a node as a neighbour.
        if node in self.neighbours:
            self.neighbours.remove(node)
    
    def reset_costs(self):
        # Resets g and h ready for another path to be found.
        self.g = 0
        self.h = 0

class AStarPathfinder:
    # Uses a graph to find the shortest path between two nodes.
    def __init__(self, app):
        self.app = app
        # self.graph will be set when self.setup_graph is called.
        self.graph = None
    
    def pathfind(self, obj, targetPos, targetObj):
        # First we create a new Circle object, using the target object's
        # position and radius. This is done so we can find which boundary
        # the circle is currently on.
        # By providing the target's position separately, we allow enemies
        # to store the last position they saw the player at and pathfind
        # towards that.
        targetCircle = Circle(self.app, targetPos, targetObj.radius)
        targetCircle.find_overlapping_grid_spaces()

        # Here we find the boundaries that the pathfinding object and the target
        # object can be considered to be standing on. This is important because
        # we eventually want to calculate a vector from the pathfinding object's
        # position to the centre of the next boundary in the path. This is explained
        # in more detail in the document, in the A* pathfinding section of development.
        startBoundary = self.get_current_boundary(obj)
        endBoundary = self.get_current_boundary(targetCircle)
        # If for some reason the player and the enemy aren't touching any boundaries,
        # we just return a vector of (0, 0), so the pathfinding object doesn't move.
        if startBoundary is None or endBoundary is None: return pygame.math.Vector2()

        # Each boundary in the level has an associated node in self.graph.
        # We access this here, so we can calculate the shortest path between them.
        startNode = self.graph.nodes[startBoundary.nodeIndex]
        endNode = self.graph.nodes[endBoundary.nodeIndex]

        # If the start node is the same as the end node, then we should just head
        # straight towards the target object as it is within the same boundary as
        # the pathfinding object.
        if startNode == endNode:
            vector = targetPos - obj.pos
            # If we try to normalise a vector of length 0, pygame throws an error.
            # Normalising is when you scale the vector to have a length of 1.
            if vector.magnitude_squared() == 0: return pygame.math.Vector2()
            return vector.normalize()

        # These are the two lists that will be used to keep track of which
        # nodes we need to check and and which we don't need to check.
        openList = []
        closedList = []
        # We need to reset all of the cost values of all of the nodes in the
        # graph back to 0 before we use it again. The nodes will still be
        # storing their cost values from the last time we used them.
        self.graph.reset_costs()
        # We append the start node to the open list so we check it first, making
        # sure to calculate its heuristic value.
        startNode.h = self.heuristic(startNode, endNode.pos)
        openList.append(startNode)

        # Now we start pathfinding!
        while True:
            # If the open list is empty, return an empty vector.
            # In theory this shouldn't happen, but just in case
            # we have this failsafe.
            if not openList: return pygame.math.Vector2()
            # Pop the lowest cost node from the open list.
            current = openList.pop(0)
            # If this node is the end node, we have reached the
            # end of the path, so break the loop.
            if current == endNode: break
            # We shouldn't check this node again next iteration,
            # so we add it to the closed list.
            closedList.append(current)
            # Iterate through all of the neighbours of the current
            # node.
            for neighbour in current.neighbours:
                # Calculate a new cost for the current node using
                # its g and h costs.
                cost = current.g + current.h
                if neighbour in openList and cost < neighbour.g:
                    # If the neighbour is in the open list and its g cost is
                    # lower than the current node's calculated cost, we remove
                    # it from the open list because we are already on a better
                    # path than it is.
                    openList.remove(neighbour)
                elif not neighbour in openList and not neighbour in closedList:
                    # If the neighbour isn't already open and it isn't closed
                    # we can add it to the open list because it could be on the
                    # shortest path. We give it a g and a h cost and add it to
                    # the open list.
                    neighbour.g = cost
                    neighbour.h = self.heuristic(neighbour, endNode.pos)
                    openList.append(neighbour)
                    # Then we sort the open list by each node's g cost + h cost
                    # (known as the node's f cost). This allows us to pop the
                    # lowest cost node from the open list back at the start of
                    # the while loop.
                    openList.sort(key = lambda x: x.g + x.h)
                    # We the set the neighbour node's parent to the current node.
                    # This allows us to trace the path back to the start.
                    neighbour.parent = current
        
        # self.retrace_path() returns the first node in the path after
        # the start node. This node's position is the position that the
        # vector we are trying to eventually calculate will point towards.
        firstNodeInPath = self.retrace_path(current, startNode)
        # Another failsafe.
        if firstNodeInPath is None: return pygame.math.Vector2()

        # Now we calculate the vector between the pathfinding object's
        # position and the position of the first node in the path.
        vector = firstNodeInPath.pos - obj.pos
        # We also normalise this vector - it is now the vector pointing
        # from the pathfinding object to the first node in the path.
        if vector.magnitude_squared() == 0: return pygame.math.Vector2()
        return vector.normalize()
    
    def get_current_boundary(self, obj):
        # Looks at all of the boundaries an object is touching, and returns the
        # closest one to that object.
        nearbyBoundaries = self.app.levelContainer.boundaryHandler.get_nearby(obj)
        nearbyBoundaries = [i for i in nearbyBoundaries if i.get_colliding(obj)]
        # If the object isn't near any boundaries, find the nearest boundary
        # and return it.
        if not nearbyBoundaries:
            return sorted(
                self.app.levelContainer.boundaryHandler.boundaries,
                key = lambda x: x.pos.distance_to(obj.pos)
            )[0]
        nearbyBoundaries = sorted(nearbyBoundaries, key = lambda x: x.pos.distance_to(obj.pos))
        return nearbyBoundaries[0]

    def setup_graph(self, nodes, edges):
        # Creates a graph and adds the provided nodes and edges to it.
        self.graph = Graph(self.app)
        self.graph.add_nodes_and_edges(nodes, edges)

    def heuristic(self, current, target):
        # Calculates a value that will be used to eliminate
        # nodes from the pathfinding search, speeding up the
        # process.
        # There are many different ways of calculating a
        # heuristic, the one I have chosen is just to calculate
        # the direct distance to the target position.
        return current.pos.distance_to(target)

    def retrace_path(self, current, startNode):
        # Uses the parent attribute of GraphNodes to retrace
        # the path we have found back to the first node in the
        # path other than the starting node.
        while True:
            if current.parent is startNode: return current
            else: current = current.parent