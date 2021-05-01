#name: Teo Sohn
#andrewid: tsohn

import random
from cmu_112_graphics import *
import time
import math

#https://docs.python.org/3/library/random.html
#gained information about random library methods and techniques here

#https://scs.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=24ed2567-5420-4014-9fb8-ad00012bf223
#graphs mini lecture
#idea from https://www.reddit.com/r/gamedev/comments/1dlwc4/procedural_dungeon_generation_algorithm_explained/
#generate rectangular rooms of random sizes at random positions
#construct a graph such that there is a path from beginning to end

################################################################################
# helper functions
################################################################################

def almostEqual(d1, d2, epsilon= 20):
    # from https://www.cs.cmu.edu/~112/notes/notes-data-and-operations.html#FloatingPointApprox
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

#from hw1
def rectanglesOverlap(x1, y1, w1, h1, x2, y2, w2, h2):
    left = min(x1,x2)
    top = min(y1,y2)
    widthOverlap = False
    heightOverlap = False
    

    if (left == x1):
        right = x2
        leftLength = w1
        rightLength = w2
    else:
        right = x1
        leftLength = w2
        rightLength = w1
    
    if (top == y1):
        bottom = y2
        topHeight = h1
        bottomHeight = h2
    else:
        bottom = y1
        topHeight = h2
        bottomHeight = h1

    leftX = left + leftLength
    topY = top + topHeight

    if (leftX >= right):
        widthOverlap = True
    else:
        widthOverlap = False

    if (topY >= bottom):
        heightOverlap = True
    else:
        heightOverlap = False

    if(heightOverlap == True and widthOverlap == True):
        return True
    else:
        return False

#checks if rectangles touch, used to separate rooms
def rectanglesTouch(x1, y1, w1, h1, x2, y2, w2, h2):
    sidesTouch = False
    endsTouch = False

    x1InRangeX2 = x2 <= x1 <= (x2 + w2)
    x2InRangeX1 = x1 <= x2 <= (x1 + w1)
    y1InRangeY2 = y2 <= y1 <= (y2 + h2)
    y2InRangeY1 = y1 <= y2 <= (y1 + h1)
    xInRange = x1InRangeX2 or x2InRangeX1
    yInRange = y1InRangeY2 or y2InRangeY1

    if ((almostEqual((x1 + w1), x2) and yInRange) or 
        (almostEqual((x2 + w2), x1) and yInRange)):
        sidesTouch = True
    if ((almostEqual((y1 + h1), y2) and xInRange) or 
        (almostEqual((y2 + h2), y1)) and xInRange):
        endsTouch = True

    if sidesTouch or endsTouch:
        return True
    else:
        return False

def distance(x0, y0, x1, y1):
    return math.sqrt((y1-y0)**2+(x1-x0)**2)

################################################################################
# Actual Functions
################################################################################


#stores room info
class Rectangle(object):

    def __init__(self, x, y, width, height):
        self.x = x - (x % 10)
        self.y = y - (y % 10)
        self.width = width - (width % 10)
        self.height = height - (height % 10)
        self.center = (self.x + (self.width / 2), self.y + (self.height / 2))
        self.rightX = self.x + self.width
        self.bottomY = self.y + self.height
        self.portals = 0
        self.portalList = []
        self.connectedPortals = set()
        self.visited = set()
    
    def addPortal(self, cx, cy, start, end):
        self.portals += 1
        self.portalList.append((cx, cy, start, end))


def appStarted(app):
    app.showGraph = False
    app.showRoomNumber = True
    app.showPortalNetwork = True
    app.showRooms = True
    app.showPortals = True
    app.showCurrentRoom = False
    app.rectangleNumber = random.randint(24, 26)
    app.rectangles = []
    app.centers = []
    app.portals = []
    app.graph = {}
    app.portalNetwork = {}
    app.visited = set()
    app.entrance = 0
    app.exit = 0
    app.scrollX = 0
    app.scrollY = 0
    (app.x0, app.y0, app.x1, app.y1) = (0, 0, 0, 0)
    makeRooms(app)
    getStartAndEnd(app)
    getCenters(app)
    app.visited = {app.entrance}
    createPath(app, app.entrance, app.exit)
    if app.exit not in app.visited:
        appStarted(app)
    createBranches(app)
    createBacktrack(app)
    createPortals(app)
    createPortalNetwork(app)
    app.currentRoom = app.entrance
    createCurrentRoom(app)
    print(app.graph)

def makeRooms(app):
    while len(app.rectangles) < app.rectangleNumber:

        #random position
        x = random.randint(100, int(app.width) - 200)
        y = random.randint(100, int(app.height) - 200)

        minDim = int(min(app.width, app.height)) 
        minDim //= 15
        #random width and height
        width = random.randint(minDim, minDim * 2)
        height = random.randint(minDim, minDim * 2)
        currentRectangle = Rectangle(x, y, width, height)

        #check if currentRectangle overlaps with others
        if checkOverlap(app, x, y, width, height) == False:
            app.rectangles.append(currentRectangle)
        
        
#checks if rectangles overlap with each other
def checkOverlap(app, x, y, width, height):
    index = 0
    (x1, y1, w1, h1) = (x, y, width, height)
    if app.rectangles != []:
        while index < (len(app.rectangles)):
            (x2, y2, w2, h2) = (app.rectangles[index].x, 
            app.rectangles[index].y, app.rectangles[index].width, 
                                        app.rectangles[index].height)   

            overlap = rectanglesOverlap(x1, y1, w1, h1, x2, y2, w2, h2)
            touch = rectanglesTouch(x1, y1, w1, h1, x2, y2, w2, h2)

            if (overlap or touch) == True:
                return True
            index += 1
    return False    

#start is the room that has the minimum combined xy coordinates
#end is the room that has the max combined xy coordinates
def getStartAndEnd(app):
    minIndex = -1
    maxIndex = -1
    minCombined = (app.width + app.height)
    maxCombined = -1
    for i in range(len(app.rectangles)):
        currentCombined = app.rectangles[i].x + app.rectangles[i].y
        if currentCombined > maxCombined:
            maxIndex = i
            maxCombined = currentCombined
        if currentCombined < minCombined:
            minIndex = i
            minCombined = currentCombined

    app.entrance = minIndex
    app.exit = maxIndex
    x0 = app.rectangles[minIndex].x
    y0 = app.rectangles[minIndex].y
    x1 = x0 + app.rectangles[minIndex].width 
    y1 = y0 + app.rectangles[minIndex].height
    x2 = app.rectangles[maxIndex].x
    y2 = app.rectangles[maxIndex].y
    x3 = x2 + app.rectangles[maxIndex].width
    y3 = y2 + app.rectangles[maxIndex].height

    return (x0, y0, x1, y1, x2, y2, x3, y3)

def getCenters(app):
    for rectangle in app.rectangles:
        app.centers.append(rectangle.center)
    
#checks if path does not overlap, and that it is the closest node
def pathIsLegal(app, start, current, end):
    if current == start or current in app.visited:
        return False
    
    (startX, startY) = app.centers[start]
    (nextX, nextY) = app.centers[current]
    (endX, endY) = app.centers[end]

    nodeDist = distance(startX, startY, nextX, nextY)

    distancesFromCurrent = getDistances(app, start, current)
    minDist = min(distancesFromCurrent)
    if nodeDist > minDist or nodeDist > 300: 
        return False
    
    return True


#returns a list of the distances from current node to all other nodes
def getDistances(app, start, current):
    result = []
    (x0, y0) = app.centers[start]
    for i in range(len(app.centers)):
        if i not in app.visited and i != start:
            (x1, y1) = app.centers[i]
            currentDistance = distance(x0, y0, x1, y1)
            result.append(currentDistance)
    return result

def circlesDoNotIntersect(app, cx, cy):
    x0 = cx
    y0 = cy
    for circle in app.portals:
        (x1, y1) = circle[0], circle[1]
        if distance(x0, y0, x1, y1) < 30:
            return False
    return True
        

#https://en.wikipedia.org/wiki/Breadth-first_search
#creates a path from the start to end
def createPath(app, start, end):

    (x0, y0) = app.centers[start]
    
    #base case
    if start == end:
        return app.graph
    #recursive case
    else:
        for i in range(len(app.centers)):
            if pathIsLegal(app, start, i, end):
                (x0, y0) = app.centers[start]
                (x1, y1) = app.centers[i]
                app.graph[start] = {i}
                app.visited.add(i)
                solution = createPath(app, i, end)
                if solution != None:
                    return solution
                del app.graph[start]
                app.visited.remove(i)
        return None
    

#takes the remaining rooms that are not connected to the main path and 
#connects them to the graph
def createBranches(app):
    i = 0
    
    while len(app.visited) < len(app.centers):
        #gets unvisited rooms
        if ((i not in app.visited) and (i < len(app.centers))):
            (x0, y0) = app.centers[i]
            minDist = app.width * 10
            minDistNode = -1
            #gets the closest room in the visited set
            for j in range(len(app.centers)):
                (x1, y1) = app.centers[j]
                nodeDist = distance(x0, y0, x1, y1)
                if ((nodeDist < minDist) and 
                    (j in app.visited) and (j != app.exit)):
                    minDist = nodeDist
                    minDistNode = j
            if minDistNode in app.visited:
                #if the closest room is not a key in dictionary, add it
                if minDistNode not in app.graph:
                    app.graph[minDistNode] = {i}
                    app.visited.add(i)
                #else add the unvisited room to 
                #the set corresponding to the value
                else:
                    app.graph[minDistNode].add(i)
                    app.visited.add(i)
        i += 1

    key = 0
    while len(app.graph) < len(app.rectangles):
        if app.graph.get(key, None) != None:
            currentSet = app.graph[key]
            for value in currentSet:
                if value not in app.graph:
                    app.graph[value] = {key}
        key += 1

#modifies the graph such that it can go both ways   
def createBacktrack(app):
    for key in app.graph:
        for value in app.graph[key]:
            if value not in app.graph:
                app.graph[value] = {key}
            else:
                app.graph[value].add(key)





#creates portals connecting rooms
def createPortals(app):
    app.portals = []
    for rectangle in app.rectangles:
        rectangle.portals = 0
        rectangle.portalList = []
        rectangle.connectedPortals = set()
        rectangle.visited = set()

    #loop through all rooms
    for key in app.graph:
        portalsNeeded = len(app.graph[key])
        currentRectangle = app.rectangles[key]
        #loop until current object has all the portals it needs
        while currentRectangle.portals < portalsNeeded:
            #loop through destinations
            for value in app.graph[key]:
                (cx, cy) = getRandomEdge(app, currentRectangle)
                #make sure that portals are not so close to each other
                if circlesDoNotIntersect(app, cx, cy):
                    #add it to the list of all portals
                    app.portals.append((cx, cy, key, value))
                    currentRectangle.addPortal(cx, cy, key, value)

    
def getRandomEdge(app, currentRectangle):
    edge = random.randint(1,4)
    if edge == 1:
        cx = random.randint(currentRectangle.x, currentRectangle.rightX)
        cy = random.randint(currentRectangle.y, currentRectangle.y + 5)
    elif edge == 2:
        cx = random.randint(currentRectangle.rightX - 5, currentRectangle.rightX)
        cy = random.randint(currentRectangle.y, currentRectangle.bottomY)
    elif edge == 3:
        cx = random.randint(currentRectangle.x, currentRectangle.rightX)
        cy = random.randint(currentRectangle.bottomY - 5, currentRectangle.bottomY)
    else:
        cx = random.randint(currentRectangle.x, currentRectangle.x + 5)
        cy = random.randint(currentRectangle.y, currentRectangle.bottomY)
    return cx, cy

def createPortalNetwork(app):
    app.portalNetwork = {}


    for i in range(len(app.rectangles)):
        currentRectangle = app.rectangles[i]
        targets = app.graph[i]
        for portal in currentRectangle.portalList:
            for target in targets:
                targetPortalList = app.rectangles[target].portalList
                for item in targetPortalList:
                    if ((portal not in app.portalNetwork) and 
                    (item not in app.portalNetwork) and 
                    (target not in currentRectangle.visited) and
                    (item not in currentRectangle.connectedPortals) and 
                    (portal not in app.rectangles[target].connectedPortals)):
                        app.portalNetwork[portal] = item
                        app.portalNetwork[item] = portal
                        currentRectangle.visited.add(target)
                        currentRectangle.connectedPortals.add(item)
                        app.rectangles[target].connectedPortals.add(portal)



def createCurrentRoom(app):
    currentRectangle = app.rectangles[app.currentRoom]
    (originalCenterX, originalCenterY) = currentRectangle.center
    app.currentCenterX = app.width / 2
    app.currentCenterY = app.height / 2
    app.displaceX = app.currentCenterX - originalCenterX
    app.displaceY = app.currentCenterY - originalCenterY
    app.x0 = app.currentCenterX - (currentRectangle.x * 5)
    app.x1 = app.x0 + currentRectangle.width * 10
    app.y0 = app.currentCenterY - (currentRectangle.y * 5)
    app.y1 = app.y0 + currentRectangle.height * 10
    app.currentRoomPortals = []
    for portal in currentRectangle.portalList:
        (portalX, portalY) = portal[0], portal[1]
        portalX += app.displaceX
        portalY += app.displaceY
        app.currentRoomPortals.append((portalX, portalY, portal[2], portal[3]))
    










def keyPressed(app, event):
    if (event.key == "r"):
        appStarted(app)
    if (event.key == "g"):
        app.showGraph = not app.showGraph
    if (event.key == "n"):
        app.showRoomNumber = not app.showRoomNumber
    if (event.key == "p"):
        app.showPortalNetwork = not app.showPortalNetwork
    if (event.key == "q"):
        app.showRooms = not app.showRooms
    if (event.key == "e"):
        app.showPortals = not app.showPortals
    if (event.key == "t"):
        app.showCurrentRoom = not app.showCurrentRoom
    if (event.key == "w"):
        app.scrollY += 10
    if (event.key == "s"):
        app.scrollY -= 10
    if (event.key == "a"):
        app.scrollX += 10
    if (event.key == "d"):
        app.scrollX -= 10
    

#each mousepress restarts app
def mousePressed(app, event):
    pass

def timerFired(app):
    pass

################################################################################
# Draw Functions
################################################################################
#draws the room from the list of rectangles
def drawRooms(app, canvas):
    roomIndex = 0
    for rectangle in app.rectangles:
        x0 = rectangle.x 
        y0 = rectangle.y
        x1 = x0 + rectangle.width
        y1 = y0 + rectangle.height
        x0 += app.scrollX
        y0 += app.scrollY
        x1 += app.scrollX
        y1 += app.scrollY
        canvas.create_rectangle(x0, y0, x1, y1, fill = "white", outline = "white")
        if app.showRoomNumber == True:
            canvas.create_text(x0 + rectangle.width/2,  y0 + rectangle.height/2, 
                            text = str(roomIndex))
        roomIndex += 1

#colors entrance green and exit red
def highlightStartAndEnd(app, canvas):
    (x0, y0, x1, y1, x2, y2, x3, y3) = getStartAndEnd(app)
    x0 += app.scrollX
    y0 += app.scrollY
    x1 += app.scrollX
    y1 += app.scrollY
    x2 += app.scrollX
    y2 += app.scrollY
    x3 += app.scrollX
    y3 += app.scrollY
    canvas.create_rectangle(x0, y0, x1, y1, fill = "green", outline = "green") 
    canvas.create_rectangle(x2, y2, x3, y3, fill = "red" , outline = "red") 
    canvas.create_text(x0, y0, text = app.entrance)
    canvas.create_text(x2, y2, text = app.exit)

#draws lines of graph
def drawConnections(app, canvas):
    for node in app.graph:
        (x0, y0) = app.centers[node]
        if len(app.graph[node]) > 1:
            for target in app.graph[node]:
                (x1, y1) = app.centers[target]
                x0 += app.scrollX
                y0 += app.scrollY
                x1 += app.scrollX
                y1 += app.scrollY
                canvas.create_line(x0, y0, x1, y1)
        else:
            index = list(app.graph[node])[0]
            (x1, y1) = app.centers[index]
            x0 += app.scrollX
            y0 += app.scrollY
            x1 += app.scrollX
            y1 += app.scrollY
            canvas.create_line(x0, y0, x1, y1)
    

def drawPortals(app, canvas):
    r = 5
    for portal in app.portals:
        (cx, cy) = (portal[0], portal[1])
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="blue")    

def drawPortalConnections(app, canvas):
    for key in app.portalNetwork:
        (x0, y0) = (key[0], key[1])
        (x1, y1) = (app.portalNetwork[key][0], app.portalNetwork[key][1])
        canvas.create_line(x0, y0, x1, y1)
    
def drawCurrentRoom(app, canvas):
    r = 25
    (x0, y0, x1, y1) = (app.x0, app.y0, app.x1, app.y1)
    x0 += app.scrollX
    y0 += app.scrollY
    x1 += app.scrollX
    y1 += app.scrollY
    xc = app.currentCenterX
    yc = app.currentCenterY
    xc += app.scrollX
    yc += app.scrollY
    canvas.create_rectangle(x0, y0, x1, y1, fill = "white")
    canvas.create_text(xc, yc, text = f'Room {app.currentRoom}')
    for portal in app.currentRoomPortals:
        (cx, cy) = (portal[0], portal[1])
        cx += app.scrollX
        cy += app.scrollY
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = "blue")
        canvas.create_text(cx, cy, text = f'to room {portal[2]}')

def redrawAll(app, canvas):
    canvas.create_rectangle(-app.width, -app.height, app.width * 10, app.height * 10, fill="grey")
    if app.showRooms:
        drawRooms(app, canvas)
    
    if app.showGraph:
        drawConnections(app, canvas)
    highlightStartAndEnd(app, canvas)
    if app.showPortals:
        drawPortals(app, canvas)
    if app.showPortalNetwork:    
        drawPortalConnections(app, canvas)
    if app.showCurrentRoom:
        drawCurrentRoom(app, canvas)
    
    

runApp(width = 1920, height = 1080)

