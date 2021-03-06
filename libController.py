import pygame, random, sys, math
import numpy as np
from pygame.locals import *
from libSystem import *
from libNode import *

system = System(800, 800)


# ------------------------------------------------
# Game controller class
class GameController:
    def __init__(self):
        # Node related variables
        self.nodes = []
        self.size = 15
        self.thickness = 5
        self.edges = []
        self.tempEdge = []
        # Drawing related variables
        self.activeNode = None
        self.activePos = None
        self.mousePos = None
        self.drawing = False
        self.lastPos = None
        self.moved = False
        self.overlap = False
        self.space = False
        self.c = False
        self.l = False
        # AI related
        self.p1ai = False
        self.p2ai = False
        # Turn
        self.done = False
        self.error = False
        self.turn = 0
        # Button
        self.p1AIcount = 0
        self.p2AIcount = 0

    def getNodes(self):
        return self.nodes

    def getEdges(self):
        return self.edges

    def getDrawing(self):
        return self.drawing

    def setDrawing(self, drawing):
        self.drawing = drawing

    def getLastPos(self):
        return self.lastPos

    def setLastPos(self, lastPos):
        self.lastPos = lastPos

    def getMousePos(self):
        return self.mousePos

    def setMousePos(self, mousePos):
        self.mousePos = mousePos

    def getMoved(self):
        return self.moved

    def setMoved(self, moved):
        self.moved = moved

    def getOverlap(self):
        return self.overlap

    def setOverlap(self, overlap):
        self.overlap = overlap

    def getTempEdge(self):
        return self.tempEdge

    def setTempEdge(self, tempEdge):
        self.tempEdge = tempEdge

    def getSize(self):
        return self.size

    def setSize(self, size):
        if size < 8:
            self.size = 8
        else:
            self.size = size

    def getThickness(self):
        return self.thickness

    def setThickness(self, thickness):
        self.thickness = thickness

    def getActiveNode(self):
        return self.activeNode

    def setActiveNode(self, node):
        self.activeNode = node

    def getActivePos(self):
        return self.activePos

    def setActivePos(self, activePos):
        self.activePos = activePos

    def getError(self):
        return self.error

    def setError(self, error):
        self.error = error

    def getSpace(self):
        return self.space

    def setSpace(self, space):
        self.space = space

    def getC(self):
        return self.c

    def setC(self, c):
        self.c = c

    def getL(self):
        return self.l

    def setL(self, l):
        self.l = l

    def getDone(self):
        return self.done

    def setDone(self, done):
        self.done = done

    def getPlayer(self):
        return (self.turn % 2) + 1

    def getTurn(self):
        return self.turn

    def setTurn(self, turn):
        self.turn = turn

    def setTurn(self, turn):
        self.turn = turn

    def getP1AIcount(self):
        return self.p1AIcount

    def toggleP1ai(self):
        self.p1AIcount += 1

    def getP2AIcount(self):
        return self.p2AIcount

    def toggleP2ai(self):
        self.p2AIcount += 1

    def getP1AI(self):
        if self.getP1AIcount() % 2 == 0:
            return False
        else:
            return True

    def getP2AI(self):
        if self.getP2AIcount() % 2 == 0:
            return False
        else:
            return True

    # Method for adding vertices
    def addNode(self, x, y):
        v = Node(len(self.getNodes()), x, y, [], False, False)
        self.getNodes().append(v)

    def findNode(self, id):
        for n in self.getNodes():
            if n.getId() == id:
                return n
        return None

    # Method for setting up initial nodes
    def startGame(self, n):
        self.getNodes().clear()
        self.addNode((system.getWidth() / 2), ((system.getHeight()+100) / 2))
        angle = 0
        for i in range(n-1):
            x = (system.getWidth() / 2.7) * math.cos(angle * 0.0174532925)
            y = (system.getHeight() / 2.7) * math.sin(angle * 0.0174532925)
            self.addNode((system.getWidth() / 2) + x, ((system.getHeight()+100) / 2) + y)
            angle += 360 / (n)

    # Method for checking whether a node
    def nodeCollision(self, node, mousePos, type):
        if type == "node":
            dx = node.getX() - mousePos[0]
            dy = node.getY() - mousePos[1]
            dis = math.sqrt(dx ** 2 + dy ** 2)
            #if dis < self.getSize():
            if dis < 12:

                return True
            return False
        elif type == "node2":
            if not ((abs(mousePos[0] - node.getX())) < self.getSize()) & ((abs(mousePos[1] - node.getY())) < self.getSize()):
                return False
            return True
        else:
            if not ((abs(mousePos[0] - node[0])) < self.getSize()) & ((abs(mousePos[1] - node[1])) < self.getSize()):
                return False
            return True

    # Method for checking a position has reached a certain distance away from a node
    def reverseNodeCollision(self, node, mousePos):
        dx = node.getX() - mousePos[0]
        dy = node.getY() - mousePos[1]
        dis = math.sqrt(dx ** 2 + dy ** 2)
        if dis < self.getSize() + 10:
            return False
        return True

    # Method for checking whether the current mouse-position collides with a node or an edge
    def checkCollision(self):
        color = system.getScreen().get_at(pygame.mouse.get_pos())
        if color == system.getRed():
            return False
        else:
            currPos = pygame.mouse.get_pos()
            for pos in self.getTempEdge():
                if pos[0] == currPos:
                    return False
        return True

    # Method for checking whether an edge overlaps itself
    def checkEdge(self, tempEdge):
        seen = []
        for i, pos in enumerate(tempEdge):
            if pos in seen:
                return False
            elif pos[0] == 0 or pos[0] > system.getHeight() - 3:
                return False
            elif pos[1] == 0 or pos[1] > system.getHeight() - 3:
                return False
            else:
                seen.append(pos)
        return True

    def isEdgeOverlapping(self, tempEdge, edge2):
        for pos1 in tempEdge:
            for i, pos2 in enumerate(edge2):
                if i > 10 or i + 10 < len(edge2):
                    if pos1 == pos2:
                        return True
        return False

    # Method for removing placeholder item
    def removePlaceholder(self):
        if self.getActiveNode() is not None:
            if -1 in self.getActiveNode().getRelations():
                self.getActiveNode().getRelations().remove(-1)

    # Method for filling blank coordinates between two registered points in an edge
    def fillBlank(self, pos1, pos2):
        # ADD TO X AND ADD TO Y
        new_posX = ()
        new_posY = ()
        new_pos = ()
        if pos2[0] - pos1[0] > 1 and pos2[1] - pos1[1] > 1:
            new_posX = (pos1[0] + 1, pos1[1])
            new_posY = (pos1[0], pos1[1] + 1)
            new_pos = (pos1[0] + 1, pos1[1] + 1)

        # ADD TO X AND SUBTRACT FROM Y
        elif pos2[0] - pos1[0] > 1 and pos1[1] - pos2[1] > 1:
            new_posX = (pos1[0] + 1, pos1[1])
            new_posY = (pos1[0], pos1[1] - 1)
            new_pos = (pos1[0] + 1, pos1[1] - 1)
        # SUBTRACT FROM X AND ADD TO Y
        elif pos1[0] - pos2[0] > 1 and pos2[1] - pos1[1] > 1:
            new_posX = (pos1[0] - 1, pos1[1])
            new_posY = (pos1[0], pos1[1] + 1)
            new_pos = (pos1[0] - 1, pos1[1] + 1)
        # SUBTRACT FROM X AND SUBTRACT FROM Y
        elif pos1[0] - pos2[0] > 1 and pos1[1] - pos2[1] > 1:
            new_posX = (pos1[0] - 1, pos1[1])
            new_posY = (pos1[0], pos1[1] - 1)
            new_pos = (pos1[0] - 1, pos1[1] - 1)
        # ADD TO X
        elif pos2[0] - pos1[0] > 1:
            new_posX = (pos1[0] + 1, pos1[1])
            new_pos = new_posX
        # SUBTRACT FROM X
        elif pos1[0] - pos2[0] > 1:
            new_posX = (pos1[0] - 1, pos1[1])
            new_pos = new_posX
        # ADD TO Y
        elif pos2[1] - pos1[1] > 1:
            new_posY = (pos1[0], pos1[1] + 1)
            new_pos = new_posY
        # SUBTRACT FROM Y
        elif pos1[1] - pos2[1] > 1:
            new_posY = (pos1[0], pos1[1] - 1)
            new_pos = new_posY

        if new_posX != ():
            self.getTempEdge().append(new_posX)
        if new_posY != ():
            self.getTempEdge().append(new_posY)

        if new_pos != pos2 and new_pos != ():
            self.fillBlank(new_pos, pos2)
