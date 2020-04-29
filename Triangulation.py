import math


class Point:
    def __init__(self, point):
        self.point = point
        self.x = point[0]
        self.y = point[1]
        self.pointInEdges = []
        self.pointInTriangles = []

    def getx(self):
        return self.x

    def gety(self):
        return self.y


class Edge:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.edgeInTriangles = []
        self.drawn = False


class Triangle:
    def __init__(self, point1, point2, point3, edge1, edge2, edge3):
        self.points = (point1, point2, point3)
        self.edges = (edge1, edge2, edge3)
        self.center = InCenter(self.calculateCenter([point1, point2, point3]), self)

    def calculateCenter(self, tri):
        A = tri[2]
        B = tri[1]
        C = tri[0]
        a = math.sqrt(abs((tri[0].x) - (tri[1].x)) ** 2 + abs((tri[0].y) - (tri[1].y)) ** 2)
        b = math.sqrt(abs((tri[0].x) - (tri[2].x)) ** 2 + abs((tri[0].y) - (tri[2].y)) ** 2)
        c = math.sqrt(abs((tri[1].x) - (tri[2].x)) ** 2 + abs((tri[1].y) - (tri[2].y)) ** 2)

        center = [((a * A.x) + (b * B.x) + (c * C.x)) / (a + b + c), ((a * A.y) + (b * B.y) + (c * C.y)) / (a + b + c)]
        return center


class InCenter:
    def __init__(self, point, triangle):
        self.x = point[0]
        self.y = point[1]
        self.triangle = triangle


class Triangulation(Point, Edge, Triangle):
    def __init__(self):

        self.allPoints = []
        self.allEdges = []
        self.allTriangles = []

    def exportCentroids(self):
        centroids = []
        for tri in self.allTriangles:
            c = tri.center
            centroids.append([c.x, c.y])
        return centroids

    def orientation(self, p, q, r):
        # to find the orientation of an ordered triplet (p,q,r)
        # function returns the following values:
        # 0 : Colinear points
        # 1 : Clockwise points
        # 2 : Counterclockwise

        val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1]))
        if (val > 0):

            # Clockwise orientation
            return 1
        elif (val < 0):

            # Counterclockwise orientation
            return 2
        else:

            # Colinear orientation
            return 0

    # The main function that returns true if
    # the line segment 'p1q1' and 'p2q2' intersect.
    def doIntersect(self, p1, q1, p2, q2):

        # Find the 4 orientations
        o1 = self.orientation(p1, q1, p2)
        o2 = self.orientation(p1, q1, q2)
        o3 = self.orientation(p2, q2, p1)
        o4 = self.orientation(p2, q2, q1)

        # intersect is true
        if ((o1 != o2) and (o3 != o4)):
            return True

        # else not intersect
        return False

    def addPoint(self, currentPoint):
        pointAsPoint = Point(currentPoint)
        connections = []
        for point in self.allPoints:
            intersect = False

            # Check if an edge between currentPoint and another point intersect with an existed edge
            for edge in self.allEdges:
                if self.doIntersect(currentPoint, point.point, edge.start.point, edge.end.point):
                    # Intersect in the starting or ending points is allowed
                    if ((point.point == edge.start.point) or (point.point == edge.end.point)
                            or (currentPoint == edge.start.point) or (currentPoint == edge.end.point)):
                        continue
                    else:
                        intersect = True
                        break
            # Add new edge, if it not collide in the existed edges
            if not intersect:
                newEdge = Edge(pointAsPoint, point)
                self.allEdges.append(newEdge)
                pointAsPoint.pointInEdges.append(newEdge)
                point.pointInEdges.append(newEdge)
                connections.append(point)

        # if there are more than 1 connection will there be minimum 1 new triangle
        if len(connections) > 1:
            for i, point in enumerate(connections):
                for point2 in connections[(i + 1):]:
                    for edgeConnect in point.pointInEdges:
                        if edgeConnect in point2.pointInEdges:
                            # Check if there are a point inside
                            pInside = False
                            for tri in edgeConnect.edgeInTriangles:
                                for p in tri.points:
                                    if p == point or p == point2:
                                        continue
                                    if p in connections:
                                        pInside = self.pointInsideTriangle(point, point2, pointAsPoint, p)
                            if not pInside:
                                self.addTriangle(pointAsPoint, point, point2)

        self.allPoints.append(pointAsPoint)

    def addPath(self, start, end, centroids, midPoint):
        if len(centroids) == 0:
            p1 = self.getPoint(start)
            p2 = self.getPoint(end)

            oldEdge = self.getEdge(p1, p2)

            # Delete triangles with this edge
            for tri in oldEdge.edgeInTriangles:
                self.deleteTriangle(tri, [oldEdge])
            self.deleteEdge(oldEdge)

            # Add midpoint, new edges and triangles
            self.addPoint(midPoint)

            # mark the the drawn edges
            mid = self.getPoint(midPoint)
            newEdge1 = self.getEdge(p1, mid)
            newEdge2 = self.getEdge(mid, p2)

            newEdge1.drawn = True
            newEdge2.drawn = True

        if len(centroids) == 1:
            center = self.getCenter(centroids[0])
            self.deleteTriangle(center.triangle, [])

            self.addPoint(midPoint)

            p1 = self.getPoint(start)
            p2 = self.getPoint(end)
            mid = self.getPoint(midPoint)
            newEdge1 = self.getEdge(p1, mid)
            newEdge2 = self.getEdge(mid, p2)

            # mark the the drawn edges
            newEdge1.drawn = True
            newEdge2.drawn = True

        if len(centroids) > 1:
            # Add first centroid
            center = self.getCenter(centroids[0])
            self.deleteTriangle(center.triangle, [])

            self.addPoint(centroids[0])

            p1 = self.getPoint(start)
            p2 = self.getPoint(centroids[0])
            newEdge = self.getEdge(p1, p2)

            # mark the the first drawn edge
            newEdge.drawn = True

            # update triangulation with one more centroid one at a time
            for i, c in enumerate(centroids):
                if (i > 0):
                    c2 = c
                    c1 = centroids[i - 1]
                    # Find the edge that colide with the connection of the two centroids
                    for oldEdge in self.allEdges:
                        if self.doIntersect(c1, c2, oldEdge.start.point, oldEdge.end.point):

                            # Delete triangles with this edge
                            for tri in oldEdge.edgeInTriangles:
                                self.deleteTriangle(tri, [oldEdge])
                            self.deleteEdge(oldEdge)
                            break

                    self.addPoint(c2)

                    po1 = self.getPoint(c1)
                    po2 = self.getPoint(c2)
                    newEdge = self.getEdge(po1, po2)

                    # mark the the drawn edge
                    newEdge.drawn = True

            # Mark the last drawn edge
            pt1 = self.getPoint(centroids[-1])
            pt2 = self.getPoint(end)
            newEdge = self.getEdge(pt1, pt2)

            newEdge.drawn = True

    def getTriangle(self, points):
        point1 = points[0]
        point2 = points[1]
        point3 = points[2]
        for tri in self.allTriangles:
            if (tri.points == (point1, point2, point3) or tri.points == (point1, point3, point2) or
                    tri.points == (point2, point1, point3) or tri.points == (point2, point3, point1) or
                    tri.points == (point3, point1, point2) or tri.points == (point3, point2, point1)):
                return tri

    def deleteTriangle(self, tri, saveEdge):
        (e1, e2, e3) = tri.edges
        (p1, p2, p3) = tri.points

        if len(saveEdge) > 0:
            for e in [e1, e2, e3]:
                if (e != saveEdge[0]):
                    e.edgeInTriangles.remove(tri)
        else:
            e1.edgeInTriangles.remove(tri)
            e2.edgeInTriangles.remove(tri)
            e3.edgeInTriangles.remove(tri)

        p1.pointInTriangles.remove(tri)
        p2.pointInTriangles.remove(tri)
        p3.pointInTriangles.remove(tri)

        self.allTriangles.remove(tri)

    def addTriangle(self, p1, p2, p3):
        edge1, edge2, edge3 = self.getEdges(p1, p2, p3)

        # Make new triangle
        newTriangle = Triangle(p1, p2, p3, edge1, edge2, edge3)
        # Add triangle to Triangulation memory
        self.allTriangles.append(newTriangle)

        # Add triangle to points and edges
        p1.pointInTriangles.append(newTriangle)
        p2.pointInTriangles.append(newTriangle)
        p3.pointInTriangles.append(newTriangle)
        edge1.edgeInTriangles.append(newTriangle)
        edge2.edgeInTriangles.append(newTriangle)
        edge3.edgeInTriangles.append(newTriangle)

    def pointInsideTriangle(self, p1, p2, p3, mid):
        if (((p1.x > mid.x) and (p2.x > mid.x) and (p3.x > mid.x)) or
                ((p1.x < mid.x) and (p2.x < mid.x) and (p3.x < mid.x)) or
                ((p1.y > mid.y) and (p2.y > mid.y) and (p3.y > mid.y)) or
                ((p1.y < mid.y) and (p2.y < mid.y) and (p3.y < mid.y))):
            return False
        else:
            return True

    def getEdges(self, point1, point2, point3):
        edges = []
        for edge in self.allEdges:
            if (edge.start.point == point1.point and edge.end.point == point2.point) or (
                    edge.start.point == point2.point and edge.end.point == point1.point):
                edges.append(edge)
            elif (edge.start.point == point1.point and edge.end.point == point3.point) or (
                    edge.start.point == point3.point and edge.end.point == point1.point):
                edges.append(edge)
            elif (edge.start.point == point3.point and edge.end.point == point2.point) or (
                    edge.start.point == point2.point and edge.end.point == point3.point):
                edges.append(edge)
            # Stop search if all edges are found
            if len(edges) == 3:
                break
        return edges

    def getEdge(self, point1, point2):
        for edge in self.allEdges:
            if (edge.start.point == point1.point and edge.end.point == point2.point) or (
                    edge.start.point == point2.point and edge.end.point == point1.point):
                return edge

    def deleteEdge(self, edge):
        (p1, p2) = edge.start, edge.end

        p1.pointInEdges.remove(edge)
        p2.pointInEdges.remove(edge)

        self.allEdges.remove(edge)

    def getPoint(self, point):
        for p in self.allPoints:
            if (int(p.x) == int(point[0])) and (int(p.y) == int(point[1])):
                return p

    def getCenter(self, point):
        for tri in self.allTriangles:
            c = tri.center
            if (c.x == point[0]) and (c.y == point[1]):
                return c

    def exportNeighbours(self, coords, typeOfNode, alreadyChosen):
        Neighbours = []
        if typeOfNode == "node":
            chosenPoint = self.getPoint(coords)
            # Add all points where there are an edge between and the centroid for the triangles the point is a part of
            for edge in self.allEdges:
                if edge.start == chosenPoint:
                    Neighbours.append(edge.end.point)
                elif edge.end == chosenPoint:
                    Neighbours.append(edge.start.point)
            for tri in chosenPoint.pointInTriangles:
                Neighbours.append([tri.center.x, tri.center.y])
        elif typeOfNode == "centerNode":
            # Add all points of the triangle the centroid is in and the centroids in the neighbouring triangles
            center = self.getCenter(coords)
            tri = center.triangle
            for point in tri.points:
                Neighbours.append(point.point)
            for edge in tri.edges:
                if not edge.drawn:
                    for triangle in edge.edgeInTriangles:
                        if triangle != tri:
                            if [triangle.center.x, triangle.center.y] not in alreadyChosen:
                                Neighbours.append([triangle.center.x, triangle.center.y])
        return Neighbours