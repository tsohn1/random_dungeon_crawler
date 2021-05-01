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
    app.showGraph = False
    app.showCorridors = False
    app.showRoomNumber = False
    app.rectangleNumber = random.randint(24, 26)
    app.rectangles = []
    app.centers = []
    app.graph = {}
    app.visited = set()
    app.entrance = 0
    app.exit = 0
    app.corridorOutline = []
    makeRooms(app)
    getStartAndEnd(app)
    getCenters(app)
    app.visited = {app.entrance}
    createPath(app, app.entrance, app.exit)
    if app.exit not in app.visited:
        appStarted(app)
    createBranches(app)
    createCorridors(app)

def makeRooms(app):
    while len(app.rectangles) < app.rectangleNumber:

        #random position
        x = random.randint(100, app.width - 200)
        y = random.randint(100, app.height - 200)

        #random width and height
        width = random.randint(75, 150)
        height = random.randint(75, 150)
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
        if (i not in app.visited) and (i < len(app.centers)):
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

def createCorridors(app):
    app.corridorOutline = []
    linesDrawn = set()
    for room in app.graph:
        connections = list(app.graph[room])
        for destination in connections:
            if destination not in linesDrawn:
                lineCoords = getCorridorCoords(app, room, destination)
                app.corridorOutline.append(lineCoords)

        linesDrawn.add(room)
    
        

def getCorridorCoords(app, room, destination):
    twoLines = False
    (x0, y0) = app.centers[room]
    (x1, y1) = app.centers[destination]
    yFirst = random.randint(0, 1)
    if abs(x1-x0) < 50:
        startX = (x0 + x1)/2
        endX = startX
        if y1 < y0: #up
            startY = app.rectangles[room].y
            endY = app.rectangles[destination].bottomY
        else: #down
            startY = app.rectangles[room].bottomY
            endY = app.rectangles[destination].y
    elif abs(y1-y0) < 50:
        startY = (y0 + y1)/2
        endY = startY
        if x1 > x0: #right
            startX = app.rectangles[room].rightX
            endX = app.rectangles[destination].x
        else: #left
            startX = app.rectangles[room].x
            endX = app.rectangles[destination].rightX
    else:
        twoLines = True
        if x1 > x0:
            #East
            if y0 > y1:
                #NE
                
                if yFirst == 1: #y changes first
                    startX = x0
                    endX = app.rectangles[destination].x
                    startY = app.rectangles[room].y
                    endY = y1
                    midX = startX
                    midY = endY
                else:
                    startX = app.rectangles[room].rightX
                    endX = x1
                    startY = y0
                    endY = app.rectangles[destination].bottomY
                    midX = endX
                    midY = startY

            else:
                #SE
                
                if yFirst == 1: #y changes first
                    startX = x0
                    endX = app.rectangles[destination].x
                    startY = app.rectangles[room].bottomY
                    endY = y1
                    midX = startX
                    midY = endY
                else:
                    startX = app.rectangles[room].rightX
                    endX = x1
                    startY = y0
                    endY = app.rectangles[destination].y
                    midX = endX
                    midY = startY

        else:
            #West
            if y0 > y1:
                #NW
                if yFirst == 1: #y changes first
                    startX = x0
                    endX = app.rectangles[destination].rightX
                    startY = app.rectangles[room].y
                    endY = y1
                    midX = startX
                    midY = endY
                else:
                    startX = app.rectangles[room].x
                    endX = x1
                    startY = y0
                    endY = app.rectangles[destination].bottomY
                    midX = endX
                    midY = startY
            else:
                #SW
                if yFirst == 1: #y changes first
                    startX = x0
                    endX = app.rectangles[destination].rightX
                    startY = app.rectangles[room].bottomY
                    endY = y1
                    midX = startX
                    midY = endY
                else:
                    startX = app.rectangles[room].x
                    endX = x1
                    startY = y0
                    endY = app.rectangles[destination].y
                    midX = endX
                    midY = startY

    if not twoLines:
        return (startX, startY, endX, endY)
    else:
        return (startX, startY, midX, midY, endX, endY)





def keyPressed(app, event):
    if (event.key == "r"):
        appStarted(app)
    if (event.key == "g"):
        app.showGraph = not app.showGraph
    if (event.key == "c"):
        app.showCorridors = not app.showCorridors
    if (event.key == "n"):
        app.showRoomNumber = not app.showRoomNumber

#each mousepress restarts app
def mousePressed(app, event):
    pass

def timerFired(app):
    pass

################################################################################
# Draw Functions
################################################################################
#draws the room from the list of rectangles
def drawRoom(app, canvas):
    roomIndex = 0
    for rectangle in app.rectangles:
        x0 = rectangle.x
        y0 = rectangle.y
        x1 = x0 + rectangle.width
        y1 = y0 + rectangle.height
        canvas.create_rectangle(x0, y0, x1, y1)
        if app.showRoomNumber == True:
            canvas.create_text(x0 + rectangle.width/2,  y0 + rectangle.height/2, 
                            text = str(roomIndex))
        roomIndex += 1

#colors entrance green and exit red
def highlightStartAndEnd(app, canvas):
    (x0, y0, x1, y1, x2, y2, x3, y3) = getStartAndEnd(app)
    canvas.create_rectangle(x0, y0, x1, y1, fill = "green") 
    canvas.create_rectangle(x2, y2, x3, y3, fill = "red") 

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
    
def drawCorridors(app, canvas):
    for line in app.corridorOutline:
        if len(line) == 4:
            (x0, y0, x1, y1) = line
            canvas.create_line(x0, y0, x1, y1)
        else:
            (x0, y0, x1, y1, x2, y2) = line
            canvas.create_line(x0, y0, x1, y1)
            canvas.create_line(x1, y1, x2, y2)
    


def redrawAll(app, canvas):
    highlightStartAndEnd(app, canvas)
    drawRoom(app, canvas)
    if app.showGraph:
        drawConnections(app, canvas)
    if app.showCorridors:
        drawCorridors(app, canvas)
    
    

runApp(width = 1920, height = 1080)

