#tp0
#name: Teo Sohn
#andrewid: tsohn
from cmu_112_graphics import *
import time
import math

def almostEqual(d1, d2, epsilon= 1):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

def distance(x0, y0, x1, y1):
    return math.sqrt((y1-y0)**2 + (x1-x0)**2)

def appStarted(app):
    app.playerX = app.width // 2
    app.playerY = app.height // 2
    app.playerMoveSpeed = 10
    app.playerProjectileSpeed = 10
    app.timerDelay = 20
    app.playerdCol = 0
    app.playerdRow = 0
    app.projectiles = []
    app.scrollX = 0
    app.scrollY = 0

def keyPressed(app, event):
    if (event.key == "w"):
        app.playerdRow = -1
    if (event.key == "a"):
        app.playerdCol = -1
    if (event.key == "s"):
        app.playerdRow = 1
    if (event.key == "d"):
        app.playerdCol = 1

def keyReleased(app, event):
    if (event.key == "w"):
        app.playerdRow = 0
    if (event.key == "a"):
        app.playerdCol = 0
    if (event.key == "s"):
        app.playerdRow = 0
    if (event.key == "d"):
        app.playerdCol = 0


class Projectile(object):

    def __init__(self, sourceX, sourceY, targetX, targetY, speed):
        self.speed = speed
        self.x = sourceX
        self.y = sourceY
        #x direction
        self.dx = (targetX - self.x) / distance(self.x, self.y, 
                                                    targetX, targetY)
        #y direction
        self.dy = (targetY - self.y) / distance(self.x, self.y, 
                                                    targetX, targetY)    

#creates projectile for enemy or player
def shootProjectile(app, x, y, source):
    if (source == "player"):
        sourceX = app.playerX
        sourceY = app.playerY
    currentProjectile = Projectile(sourceX, sourceY, x, y, 
                                                    app.playerProjectileSpeed)
    app.projectiles.append(currentProjectile)
    

def mousePressed(app, event):
    shootProjectile(app, event.x, event.y, "player")


#moves player and projectiles
def timerFired(app):
    #scrolls everything relative to player
    app.scrollX -= app.playerdCol * app.playerMoveSpeed
    app.scrollY -= app.playerdRow * app.playerMoveSpeed

    if (app.projectiles != []):
        for projectile in app.projectiles:
            projectile.x += (projectile.dx * projectile.speed)
            projectile.y += (projectile.dy * projectile.speed)
            if ((projectile.x < 0 or projectile.x > app.width) or 
                    (projectile.y < 0 or projectile.y > app.height)):
                app.projectiles.remove(projectile)


def drawPlayer(app, canvas):
    r = 25
    cx = app.playerX
    cy = app.playerY
    canvas.create_oval(cx+r, cy+r, cx-r, cy-r, fill="black")
    canvas.create_text(cx, cy - 2*r, text="Player")
    
def drawProjectiles(app, canvas):
    r = 5
    for projectile in app.projectiles:
        cx = projectile.x
        cy = projectile.y
        canvas.create_oval(cx+r, cy+r, cx-r, cy-r, fill="red")

def drawLevel(app, canvas):
    #temporary code
    x0 = app.scrollX
    y0 = app.scrollY
    x1 = x0 + 60
    y1 = y0 + 70
    canvas.create_rectangle(x0, y0, x1, y1, fill="green")
    #would get the room information from _randomroom.py and draw it




def redrawAll(app, canvas):
    drawLevel(app, canvas)
    drawPlayer(app, canvas)
    drawProjectiles(app, canvas)
    

runApp(width = 1280, height = 720)

