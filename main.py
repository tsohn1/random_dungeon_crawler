#name: Teo Sohn
#andrewid: tsohn

from cmu_112_graphics import *
from randomdungeon import *
import time
import math
import random

################################################################################
# helper functions
################################################################################

def almostEqual(d1, d2, epsilon= 1):
    # from https://www.cs.cmu.edu/~112/notes/notes-data-and-operations.html#FloatingPointApprox
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

def distance(x0, y0, x1, y1):
    return math.sqrt((y1-y0)**2 + (x1-x0)**2)

################################################################################
# Actual Functions
################################################################################

################################################################################
# Menu Mode
################################################################################
# app starts in this mode
def menuMode_mousePressed(app, event):
    xBounds = (app.width / 2 - 50) < event.x < (app.width / 2 + 50)
    yBounds = (app.height / 2 - 20) < event.y < (app.height / 2 + 20)
    if (xBounds and yBounds):
        app.mode = 'gameMode'

def menuMode_redrawAll(app, canvas):
    canvas.create_text(app.width / 2, 200, text = "Infinite Dungeon Crawler",
                                font = "Arial 30 bold")

    canvas.create_rectangle(app.width / 2 - 50, app.height / 2 - 20, 
                            app.width / 2 + 50, app.height / 2 + 20)
    canvas.create_text(app.width / 2, app.height / 2, text="Play")

################################################################################
# Main App
################################################################################
# using modes from 
#https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#usingModes


def appStarted(app):
    app.mode = "menuMode"
    createLevel(app)
    app.time = time.time()
    app.hitWindow = 30 #player and enemy hitbox
    app.timerDelay = 20
    app.paused = False
    app.isChoosing = False
    app.showChoice = True
    app.currentChoices = list(app.graph[app.currentRoom])
    app.gameOver = False
    app.playerLost = False
    loadPlayerStats(app)
    loadMonsterStats(app)
    app.projectiles = []
    app.scrollX = 0
    app.scrollY = 0
    app.playerNoScrollX = app.playerX - app.scrollX
    app.playerNoScrollY = app.playerY - app.scrollY
    spawnMonsters(app)

def loadPlayerStats(app):
    app.playerX = app.width // 2
    app.playerY = app.height // 2
    app.playerMoveSpeed = 10
    app.playerProjectileSpeed = 15
    app.playerDexterity = 35 # related to fire rate
    app.playerHealth = 100
    app.playerCurrentHealth = 100
    app.playerDefense = 5
    app.playerAttack = 10
    app.playerFireRate = 0
    app.playerFiring = False
    app.playerTargetX = 0
    app.playerTargetY = 0
    app.playerdCol = 0
    app.playerdRow = 0

def loadMonsterStats(app):
    app.monsters = []
    app.monsterProjectileSpeed = 10
    app.monsterDefaultAttack = 10


class Monster(object):
    def __init__(self, app, x, y, health, defense, moveSpeed, attack, dexterity):
        #initialize position and scroll so it could be scrolled with rest
        self.noScrollX = x - app.scrollX
        self.noScrollY = y - app.scrollX
        self.x = x
        self.y = y
        self.health = health
        self.currentHealth = health 
        self.defense = defense
        self.moveSpeed = moveSpeed
        self.attack = attack
        #fire rate formula from https://www.realmeye.com/wiki/character-stats
        self.fireRate = 1.5 + 6.5*(dexterity / 50)
        self.attackPeriod = 1 / self.fireRate
        self.fireCooldown = time.time()

    def updatePos(self, scrollX, scrollY):
        #update pos with scroll
        self.x = self.noScrollX + scrollX
        self.y = self.noScrollY + scrollY
        

    def takeDamage(self, app, n):
        damageTaken = n-self.defense
        if damageTaken > 0:
            self.currentHealth -= damageTaken
        else:
            pass
    
    def attackPlayer(self, app, dx, dy):
        #calculations done with absolute position
        self.noScrollX += self.moveSpeed * dx
        self.noScrollY += self.moveSpeed * dy
        if (time.time() - self.fireCooldown) > self.attackPeriod:
            shootProjectile(app, self.x, self.y, "monster")
            self.fireCooldown = time.time()

class Projectile(object):

    def __init__(self, app, source, sourceX, sourceY, targetX, targetY, speed):
        self.source = source
        self.speed = speed
        #initialize position and scroll so it could be scrolled with rest
        self.noScrollX = sourceX - app.scrollX
        self.noScrollY = sourceY - app.scrollY
        self.x = sourceX
        self.y = sourceY
        self.targetNoScrollX = targetX - app.scrollX
        self.targetNoScrollY = targetY - app.scrollY
        self.targetX = targetX
        self.targetY = targetY
        #x direction
        r = distance(self.noScrollX, self.noScrollY, 
                        self.targetNoScrollX, self.targetNoScrollY)
        self.dx = (self.targetNoScrollX - self.noScrollX) / r
        #y direction
        self.dy = (self.targetNoScrollY - self.noScrollY) / r
    
    def updatePos(self, scrollX, scrollY):
        self.x = self.noScrollX + scrollX
        self.y = self.noScrollY + scrollY
        self.targetX = self.targetNoScrollX + scrollX
        self.targetY = self.targetNoScrollY + scrollY
        #update directions as well

    def destroy(self, app):
        app.projectiles.remove(self)
                                                    
#adds monsters to list, called every level
def spawnMonsters(app):
    app.monsters = []
    monsterNumber = random.randint(4, 7)
    for i in range(monsterNumber):
        xPos = random.randint(app.x0, app.x1)
        yPos = random.randint(app.y0, app.y1)
        app.monsters.append(Monster(app, xPos, yPos, 100, 0, 5, 10, 3))

#creates projectile for enemy or player
def shootProjectile(app, x, y, source):
    if (source == "player"):
        sourceX = app.playerX
        sourceY = app.playerY
        currentProjectile = Projectile(app, "player", sourceX, sourceY, x, y, 
                                                    app.playerProjectileSpeed)
    elif (source == "monster"):
        sourceX = x
        sourceY = y
        currentProjectile = Projectile(app, "monster", sourceX, sourceY, 
                                            app.playerX, app.playerY,  
                                                    app.monsterProjectileSpeed)
    app.projectiles.append(currentProjectile)

#checks if projectile hit a player, monster, or wall
def checkProjCollision(app):
    for projectile in app.projectiles:
        if (projectile.source == "player"):
            for monster in app.monsters:
                #hitbox of projectile
                xRange = monster.x - app.hitWindow < projectile.x < monster.x + app.hitWindow
                yRange = monster.y - app.hitWindow < projectile.y < monster.y + app.hitWindow
                if xRange and yRange:
                    monster.takeDamage(app, app.playerAttack)
                    if projectile in app.projectiles:
                        app.projectiles.remove(projectile)
                    checkDeaths(app)
        elif (projectile.source == "monster"):
            damage = app.monsterDefaultAttack
            #hitbox of projectile
            xRange = app.playerX - app.hitWindow < projectile.x < app.playerX + app.hitWindow
            yRange = app.playerY - app.hitWindow < projectile.y < app.playerY + app.hitWindow
            if xRange and yRange:
                playerTakeDamage(app, damage)
                if projectile in app.projectiles:
                    app.projectiles.remove(projectile)
                checkDeaths(app)
    
    #destroy when colliding with wall
    for projectile in app.projectiles:
        x0 = projectile.noScrollX
        y0 = projectile.noScrollY
        if (x0 < app.x0): 
            projectile.destroy(app)
        if (x0 > app.x1):
            projectile.destroy(app)
        if (y0 < app.y0):
            projectile.destroy(app)
        if (y0 > app.y1):
            projectile.destroy(app)



#called if player gets hit by projectile
def playerTakeDamage(app, damage):
    damageTaken = damage - app.playerDefense
    if damageTaken > 0:
        app.playerCurrentHealth -= damageTaken
    else:
        pass

#checks if player or any monsters are dead
def checkDeaths(app):
    for monster in app.monsters:
        if (monster.currentHealth <= 0):
            app.monsters.remove(monster)
    if app.playerCurrentHealth <= 0:
        app.gameOver = True
        app.playerLost = True

#checks if player is in last room
def checkWin(app):
    if app.currentRoom == app.exit:
        app.gameOver = True
        app.playerLost = False

#checks if player is touching a wall or a portal
def checkCollision(app):
    x0 = app.playerNoScrollX
    y0 = app.playerNoScrollY
    (x1, y1) = app.currentPortal
    if (x0 < app.x0 + 25): 
        app.playerNoScrollX = app.x0 + 25
        app.scrollX = app.playerX - app.playerNoScrollX
    if (x0 > app.x1 - 25):
        app.playerNoScrollX = app.x1 - 25
        app.scrollX = app.playerX - app.playerNoScrollX
    if (y0 < app.y0 + 25):
        app.playerNoScrollY = app.y0 + 25
        app.scrollY = app.playerY - app.playerNoScrollY
    if (y0 > app.y1 - 25):
        app.playerNoScrollY = app.y1 - 25
        app.scrollY = app.playerY - app.playerNoScrollY
    portalDist = distance(x0, y0, x1, y1)
    if portalDist < 30:
        app.isChoosing = True
        app.paused = True

#scrolls all gameobjects other than player
def scrollObjects(app):
    for monster in app.monsters:
        monster.updatePos(app.scrollX, app.scrollY)
    for projectile in app.projectiles:
        projectile.updatePos(app.scrollX, app.scrollY)

#gets player choice of next room
def getChoice(app, x, y):
    x0 = app.width/2 - 400
    y0 = (app.height / 2) - 30
    x1 = app.width/2 + 400
    y1 = (app.height / 2) + 30
    for i in range(len(app.currentChoices)):
        currentchoice = app.currentChoices[i]
        boxWidth = (x1 - x0) / len(app.currentChoices)
        choiceX0 = x0 + (i * boxWidth)
        choiceY0 = y0
        choiceX1 = x0 + ((i + 1)* boxWidth)
        choiceY1 = y1
        if (choiceX0 < x < choiceX1) and (choiceY0 < y < choiceY1):
            return app.currentChoices[i]


################################################################################
# Game Mode
################################################################################
def gameMode_keyPressed(app, event):
    if (event.key == "m"): #map
        if app.isChoosing == False:
            app.paused = not app.paused
        app.showMap = not app.showMap
        app.showCurrentRoom = not app.showCurrentRoom
        app.showChoice = not app.showChoice
            

    if not app.paused or app.gameOver:
        if (event.key == "w"):
            app.playerdRow = -1
        if (event.key == "a"):
            app.playerdCol = -1
        if (event.key == "s"):
            app.playerdRow = 1
        if (event.key == "d"):
            app.playerdCol = 1
        
        #spawn a monster, for testing
        if (event.key == "p"):
            x = random.randint(100, 600)
            y = random.randint(100, 600)

            app.monsters.append(Monster(app, x, y, 100, 0, 3, 10, 3))

def gameMode_keyReleased(app, event):
    if not app.paused or app.gameOver:
        if (event.key == "w"):
            app.playerdRow = 0
        if (event.key == "a"):
            app.playerdCol = 0
        if (event.key == "s"):
            app.playerdRow = 0
        if (event.key == "d"):
            app.playerdCol = 0

def gameMode_mousePressed(app, event):
    if not app.paused or app.gameOver:
        app.playerTargetX = event.x
        app.playerTargetY= event.y
        app.playerFiring = True
    if app.isChoosing and app.showChoice and (event.x and event.y) != None:
        choice = getChoice(app, event.x, event.y)
        if choice != None:
            switchRoom(app, choice)
            app.currentChoices = list(app.graph[app.currentRoom])
            checkWin(app)
            spawnMonsters(app)
            app.playerdRow = 0
            app.playerdCol = 0
    if app.gameOver:
        if (((app.width / 2 - 50) < event.x < (app.width / 2 + 50)) and 
            (500 < event.y < 600)):
            appStarted(app)

#shooting also works with dragging    
def gameMode_mouseDragged(app, event):
    if not app.paused or app.gameOver:
        app.playerTargetX = event.x
        app.playerTargetY= event.y

def gameMode_mouseReleased(app, event):
    if not app.paused or app.gameOver:
        app.playerTargetX = event.x
        app.playerTargetY= event.y
        app.playerFiring = False

#moves player and projectiles
def gameMode_timerFired(app):
    if not app.paused or app.gameOver:
        #scrolls everything relative to player
        app.scrollX -= app.playerdCol * app.playerMoveSpeed
        app.scrollY -= app.playerdRow * app.playerMoveSpeed
        app.playerNoScrollX = app.playerX - app.scrollX
        app.playerNoScrollY = app.playerY - app.scrollY
        scrollObjects(app)
        #calculate player fire rate, formula from 
        #https://www.realmeye.com/wiki/character-stats
        app.playerFireRate = 1.5 + 6.5*(app.playerDexterity / 50)
        fireCooldown = time.time() - app.time
        playerAttackPeriod = 1 / app.playerFireRate
        if app.playerFiring and (fireCooldown > playerAttackPeriod):
            shootProjectile(app, app.playerTargetX, app.playerTargetY, "player")
            app.time = time.time()


        #move monsters when close to player
        for monster in app.monsters:
            #do calculations in absolute coordinates
            r = distance(monster.noScrollX, monster.noScrollY, app.playerNoScrollX, app.playerNoScrollY)
            if r < 600 and r != 0:
                dx = (app.playerNoScrollX - monster.noScrollX) / r
                dy = (app.playerNoScrollY - monster.noScrollY) / r
                monster.attackPlayer(app, dx, dy)

        #moves projectiles in their directions
        if (app.projectiles != []):
            for projectile in app.projectiles:
                projectile.noScrollX += (projectile.dx * projectile.speed)
                projectile.noScrollY += (projectile.dy * projectile.speed)
                if (( projectile.x < 0 or  projectile.x > app.width) or 
                        (projectile.y < 0 or projectile.y > app.height)):
                    app.projectiles.remove(projectile)

        
        checkProjCollision(app)
        checkCollision(app)
    

################################################################################
# Draw Functions
################################################################################   


def gameMode_drawPlayer(app, canvas):
    if not app.paused:
        r = 25
        cx = app.playerX
        cy = app.playerY
        canvas.create_oval(cx+r, cy+r, cx-r, cy-r, fill="black")
        canvas.create_text(cx, cy - 2*r, text="Player")
    
def gameMode_drawProjectiles(app, canvas):
    if not app.paused:
        r = 5
        for projectile in app.projectiles:
            cx = projectile.x
            cy = projectile.y
            canvas.create_oval(cx+r, cy+r, cx-r, cy-r, fill="red")

def gameMode_drawLevel(app, canvas):
    canvas.create_rectangle(-app.width, -app.height, app.width * 10, app.height * 10, fill="grey")
    if app.showMap:
        drawRooms(app, canvas)
        drawConnections(app, canvas)
        highlightStartAndEnd(app, canvas)
        
    if app.showCurrentRoom:
        drawCurrentRoom(app, canvas)
        drawPortal(app, canvas)

def gameMode_drawMonsters(app, canvas):
    if not app.paused:
        r = 25
        for monster in app.monsters:
            cx = monster.x
            cy = monster.y
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="red")
        
def gameMode_drawHealth(app, canvas):
    if not app.paused:
        healthBarLength = 80
        healthBarThickness = 10
        canvas.create_rectangle(app.playerX - 40, app.playerY - 40, 
                                app.playerX - 40 + healthBarLength, 
                                app.playerY - 40 + healthBarThickness)
        canvas.create_rectangle(app.playerX - 39, app.playerY - 39, 
                                app.playerX - 41 + healthBarLength * (app.playerCurrentHealth / app.playerHealth), 
                                app.playerY - 41 + healthBarThickness, fill="light green")

        for monster in app.monsters:
            x = monster.x
            y = monster.y
            canvas.create_rectangle(x - 40, y- 40, 
                                x - 40 + healthBarLength, 
                                y - 40 + healthBarThickness)
            canvas.create_rectangle(x - 39, y - 39, 
                                x - 41 + healthBarLength * (monster.currentHealth / monster.health), 
                                y - 41 + healthBarThickness, fill="light green")

#draw room choosing UI when stepping on portal
def gameMode_drawChoice(app, canvas):
    if app.isChoosing and app.showChoice:
        x0 = app.width/2 - 400
        y0 = (app.height / 2) - 30
        x1 = app.width/2 + 400
        y1 = (app.height / 2) + 30
        canvas.create_rectangle(x0, y0, x1, y0, fill="orange" )
        for i in range(len(app.currentChoices)):
            currentchoice = app.currentChoices[i]
            boxWidth = (x1 - x0) / len(app.currentChoices)
            choiceX0 = x0 + (i * boxWidth)
            choiceY0 = y0
            choiceX1 = x0 + ((i + 1)* boxWidth)
            choiceY1 = y1
            canvas.create_rectangle(choiceX0, choiceY0, choiceX1, choiceY1, fill = "yellow")
            textX = (choiceX0 + choiceX1) / 2
            textY = (choiceY0 + choiceY1) / 2
            canvas.create_text(textX, textY, text = f"Room {currentchoice}")

def gameMode_drawGameOver(app, canvas):
    x0 = app.width / 2 - 50
    x1 = app.width / 2 + 50
    y0 = 500
    y1 = 600
    canvas.create_text(app.width / 2, 100, text = "Game Over", font = "arial 30 bold")
    canvas.create_text(app.width / 2, 300, text = "You Died", font = "arial 30 bold")
    canvas.create_rectangle(x0, y0, x1, y1)
    canvas.create_text(app.width / 2, 550, text = "Main Menu", font = "arial 15 bold")

def gameMode_drawPlayerWin(app, canvas):
    x0 = app.width / 2 - 50
    x1 = app.width / 2 + 50
    y0 = 500
    y1 = 600
    canvas.create_text(app.width / 2, 100, text = "You Win!", font = "arial 30 bold")
    canvas.create_text(app.width / 2, 300, text = "You made it to the exit", font = "arial 30 bold")
    canvas.create_rectangle(x0, y0, x1, y1)
    canvas.create_text(app.width / 2, 550, text = "Main Menu", font = "arial 15 bold")

def gameMode_redrawAll(app, canvas):
    if not app.gameOver:
        gameMode_drawLevel(app, canvas)
        gameMode_drawPlayer(app, canvas)
        gameMode_drawProjectiles(app, canvas)
        gameMode_drawMonsters(app, canvas)
        gameMode_drawHealth(app, canvas)
        gameMode_drawChoice(app, canvas)
    if app.paused:
        canvas.create_text(app.width/2, 100, text = "paused", font = "arial 20 bold")
    if app.gameOver and app.playerLost:
        gameMode_drawGameOver(app, canvas)
    elif (app.gameOver == True) and (app.playerLost == False):
        gameMode_drawPlayerWin(app, canvas)
    

runApp(width = 1280, height = 720)

