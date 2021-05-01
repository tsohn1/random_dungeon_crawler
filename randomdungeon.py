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


def appStarted(app):
    createLevel(app)
    
    #called in main.py
def createLevel(app):
    app.showMap = False
    app.showCurrentRoom = True
    app.rectangleNumber = random.randint(16, 20)
    app.rectangles = []
    app.centers = []
    app.currentPortal = (0, 0)
    app.graph = {}
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
    app.currentRoom = app.entrance
    createCurrentRoom(app)

#make randomly sized rectangular rooms
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
    

#determines a random location for portal to spawn
def getRandomEdge(app, x0, y0, x1, y1):
    edge = random.randint(1,4)
    offset = 50
    if edge == 1:
        cx = random.randint(x0, x1)
        cy = random.randint(y0, y0 + offset)
    elif edge == 2:
        cx = random.randint(x1 - offset, x1)
        cy = random.randint(y0, y1)
    elif edge == 3:
        cx = random.randint(x0, x1)
        cy = random.randint(y1 - offset, y1)
    else:
        cx = random.randint(x0, x0 + offset)
        cy = random.randint(y0, y1)
    return cx, cy

#creates the current room
def createCurrentRoom(app):
    currentRectangle = app.rectangles[app.currentRoom]
    (originalCenterX, originalCenterY) = currentRectangle.center
    app.currentCenterX = app.width / 2
    app.currentCenterY = app.height / 2
    app.scrollX = 0
    app.scrollY = 0
    app.displaceX = app.currentCenterX - originalCenterX
    app.displaceY = app.currentCenterY - originalCenterY 
    app.x0 = int(app.currentCenterX - (currentRectangle.width * 10))
    app.x1 = int(app.x0 + currentRectangle.width * 20)
    app.y0 = int(app.currentCenterY - (currentRectangle.height * 10))
    app.y1 = int(app.y0 + currentRectangle.height * 20)
    app.currentPortal = getRandomEdge(app, app.x0, app.y0, app.x1, app.y1)
    
#switches "current" room
def switchRoom(app, room):
    app.currentRoom = room
    app.paused = False
    app.isChoosing = False
    app.showMap = False
    app.showCurrentRoom = True
    createCurrentRoom(app)
    
def keyPressed(app, event):
    pass

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
        canvas.create_rectangle(x0, y0, x1, y1, fill = "white", outline = "white")
        canvas.create_text(x0 + rectangle.width/2,  y0 + rectangle.height/2, 
                            text = str(roomIndex))
        roomIndex += 1

#colors entrance green and exit red in map
def highlightStartAndEnd(app, canvas):
    (x0, y0, x1, y1, x2, y2, x3, y3) = getStartAndEnd(app)
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
                canvas.create_line(x0, y0, x1, y1)
        else:
            index = list(app.graph[node])[0]
            (x1, y1) = app.centers[index]
            canvas.create_line(x0, y0, x1, y1)
    
#draws the portal, blue circle
def drawPortal(app, canvas):
    r = 25
    (cx, cy) = app.currentPortal
    cx += app.scrollX
    cy += app.scrollY
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = "blue")

#draws currentroom, which is about 15 times the size than that in the map
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
    canvas.create_text(xc, yc, text = f'Room {app.currentRoom}', 
                            font="arial 30 bold")

def redrawAll(app, canvas):
    canvas.create_rectangle(-app.width, -app.height, app.width * 10, app.height * 10, fill="grey")
    if app.showMap:
        drawRooms(app, canvas)
        drawConnections(app, canvas)
        highlightStartAndEnd(app, canvas)
        
    if app.showCurrentRoom:
        drawCurrentRoom(app, canvas)
        drawPortal(app, canvas)
    
    

#runApp(width = 1920, height = 1080)

