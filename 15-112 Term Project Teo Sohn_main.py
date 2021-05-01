#tp0
#name: Teo Sohn
#andrewid: tsohn
from cmu_112_graphics import *
import time
import math
import random

def almostEqual(d1, d2, epsilon= 1):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

def distance(x0, y0, x1, y1):
    return math.sqrt((y1-y0)**2 + (x1-x0)**2)

def appStarted(app):
    app.time = time.time()
    app.playerX = app.width // 2
    app.playerY = app.height // 2
    app.playerMoveSpeed = 10
    app.playerProjectileSpeed = 15
    app.playerDexterity = 35
    app.playerHealth = 100
    app.playerCurrentHealth = 100
    app.playerDefense = 5
    app.playerAttack = 10
    app.playerFireRate = 0
    app.playerFiring = False
    app.playerTargetX = 0
    app.playerTargetY = 0
    app.hitWindow = 30
    app.timerDelay = 20
    app.playerdCol = 0
    app.playerdRow = 0
    app.monsters = []
    app.monsterProjectileSpeed = 10
    app.projectiles = []
    app.scrollX = 0
    app.scrollY = 0
    spawnMonsters(app)

def keyPressed(app, event):
    if (event.key == "w"):
        app.playerdRow = -1
    if (event.key == "a"):
        app.playerdCol = -1
    if (event.key == "s"):
        app.playerdRow = 1
    if (event.key == "d"):
        app.playerdCol = 1
    if (event.key == "p"):
        x = random.randint(100, 600)
        y = random.randint(100, 600)

        app.monsters.append(Monster(app, x, y, 100, 0, 3, 10, 3))

def keyReleased(app, event):
    if (event.key == "w"):
        app.playerdRow = 0
    if (event.key == "a"):
        app.playerdCol = 0
    if (event.key == "s"):
        app.playerdRow = 0
    if (event.key == "d"):
        app.playerdCol = 0

class Monster(object):
    def __init__(self, app, x, y, health, defense, moveSpeed, attack, dexterity):
        self.noScrollX = x
        self.noScrollY = y
        self.x = x
        self.y = y
        self.health = health
        self.currentHealth = health 
        self.defense = defense
        self.moveSpeed = moveSpeed
        self.attack = attack
        self.fireRate = 1.5 + 6.5*(dexterity / 50)

    def updatePos(self, scrollX, scrollY):
        self.x = self.noScrollX + scrollX
        self.y = self.noScrollY + scrollY

    def takeDamage(self, app, n):
        damageTaken = n-self.defense
        if damageTaken > 0:
            self.currentHealth -= damageTaken
        else:
            pass
    
    def attackPlayer(self, app, dx, dy):
        self.x += self.moveSpeed * dx
        self.y += self.moveSpeed * dy


    



class Projectile(object):

    def __init__(self, app, source, sourceX, sourceY, targetX, targetY, speed):
        self.source = source
        self.speed = speed
        self.x = sourceX
        self.y = sourceY
        self.initialScrollX = app.scrollX
        self.initialScrollY = app.scrollY
        #x direction
        self.dx = (targetX - self.x) / distance(self.x, self.y, 
                                                    targetX, targetY)
        #y direction
        self.dy = (targetY - self.y) / distance(self.x, self.y, 
                                                    targetX, targetY)   
    
    def updatePos(self, scrollX, scrollY):
        self.x = self.x + (scrollX - self.initialScrollX)
        self.y = self.y + (scrollY - self.initialScrollY)
                                                    
#adds monsters to list
def spawnMonsters(app):
    app.monsters.append(Monster(app, 500, 400, 100, 0, 3, 10, 3))

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
        currentProjectile = Projectile(app, "monster", sourceX, sourceX, 
                                            app.playerX, app.playerX,  
                                                    app.monsterProjectileSpeed)
    app.projectiles.append(currentProjectile)

#checks if projectile hit a player or monster
def checkCollision(app):
    for projectile in app.projectiles:
        if (projectile.source == "player"):
            for monster in app.monsters:
                #hitbox of projectile
                xRange = monster.x - app.hitWindow < projectile.x < monster.x + app.hitWindow
                yRange = monster.y - app.hitWindow < projectile.y < monster.y + app.hitWindow
                if xRange and yRange:
                    monster.takeDamage(app, app.playerAttack)
                    app.projectiles.remove(projectile)
                    checkDeaths(app)

#checks if player or any monsters are dead
def checkDeaths(app):
    for monster in app.monsters:
        if (monster.currentHealth <= 0):
            app.monsters.remove(monster)

def scrollObjects(app):
    for monster in app.monsters:
        monster.updatePos(app.scrollX, app.scrollY)
    # for projectile in app.projectiles:
    #     projectile.updatePos(app.scrollX, app.scrollY)


def mousePressed(app, event):
    app.playerTargetX = event.x
    app.playerTargetY= event.y
    app.playerFiring = True
    
def mouseDragged(app, event):
    app.playerTargetX = event.x
    app.playerTargetY= event.y

def mouseReleased(app, event):
    app.playerTargetX = event.x
    app.playerTargetY= event.y
    app.playerFiring = False


#moves player and projectiles
def timerFired(app):
    #scrolls everything relative to player
    app.scrollX -= app.playerdCol * app.playerMoveSpeed
    app.scrollY -= app.playerdRow * app.playerMoveSpeed
    scrollObjects(app)
    #calculate player fire rate
    app.playerFireRate = 1.5 + 6.5*(app.playerDexterity / 50)
    fireCooldown = time.time() - app.time
    playerAttackPeriod = 1 / app.playerFireRate
    if app.playerFiring and (fireCooldown > playerAttackPeriod):
        shootProjectile(app, app.playerTargetX, app.playerTargetY, "player")
        app.time = time.time()


    #move monsters when close to player
    for monster in app.monsters:
        r = distance(monster.x, monster.y, app.playerX, app.playerY)
        if r < 600 and r != 0:
            dx = (app.playerX - monster.x) / r
            dy = (app.playerY - monster.y) / r
            monster.attackPlayer(app, dx, dy)

    if (app.projectiles != []):
        for projectile in app.projectiles:
            projectile.x += (projectile.dx * projectile.speed)
            projectile.y += (projectile.dy * projectile.speed)
            if ((projectile.x < 0 or projectile.x > app.width) or 
                    (projectile.y < 0 or projectile.y > app.height)):
                app.projectiles.remove(projectile)

    
    checkCollision(app)
    

    


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

def drawMonsters(app, canvas):
    r = 25
    for monster in app.monsters:
        cx = monster.x
        cy = monster.y
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="red")
        
def drawHealth(app, canvas):
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



def redrawAll(app, canvas):
    drawLevel(app, canvas)
    drawPlayer(app, canvas)
    drawProjectiles(app, canvas)
    drawMonsters(app, canvas)
    drawHealth(app, canvas)
    

runApp(width = 1280, height = 720)
