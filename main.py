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

#readFile and writeFile from 
# https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

#reads the highscores files and returns a sorted list of the highscores
def readAndSortHighscores():
    text = readFile("highscores.txt")
    result = []
    currentPlayer = "Player"
    currentScore = 0
    for line in text.splitlines():
        if line.strip() != "":
            for word in line.split(" "):
                if word.isalpha():
                    currentPlayer = word
                else:
                    currentScore = int(word)
            result.append((currentScore, currentPlayer))
    return sorted(result)

################################################################################
# Actual Functions
################################################################################
# using modes from 
#https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#usingModes
################################################################################
# Menu Mode
################################################################################
# app starts in this mode
def menuMode_mousePressed(app, event):
    xBounds = (app.width / 2 - 50) < event.x < (app.width / 2 + 50)
    gameStartYBounds = (app.height / 2 - 20) < event.y < (app.height / 2 + 20)
    optionsYBounds = (app.height / 2 + 40) < event.y < (app.height / 2 + 80)
    highscoreYBounds = (app.height / 2 + 100) < event.y < (app.height / 2 + 140)
    nameChangeXBounds = (0 < event.x < 300)
    nameChangeYBounds = (0 < event.y < 100)

    #Play
    if (xBounds and gameStartYBounds):
        app.mode = "gameMode"
        startGame(app)

    #Options
    if (xBounds and optionsYBounds):
        app.mode = "optionsMode"

    #Highscores
    if (xBounds and highscoreYBounds):
        app.mode = "highscoreMode"

    #Change Name
    if (nameChangeXBounds and nameChangeYBounds):
        currentInput = app.getUserInput("Please Enter Your Name")
        if (currentInput == None or currentInput.strip() == ""):
            app.message = "Please Enter A Valid Name"
        else:
            app.playerName = currentInput
    

def menuMode_redrawAll(app, canvas):
    canvas.create_text(app.width / 2, 200, text = "Infinite Dungeon Crawler",
                                font = "Arial 30 bold")
    #Play
    canvas.create_rectangle(app.width / 2 - 50, app.height / 2 - 20, 
                            app.width / 2 + 50, app.height / 2 + 20)
    canvas.create_text(app.width / 2, app.height / 2, text="Play", font = "arial 9 bold")
    #Options
    canvas.create_rectangle(app.width / 2 - 50, app.height / 2 + 40, 
                            app.width / 2 + 50, app.height / 2 + 80 )
    canvas.create_text(app.width / 2, app.height / 2 + 60, text="Options", font = "arial 9 bold")
    #Highscores
    canvas.create_rectangle(app.width / 2 - 50, app.height / 2 + 100, 
                            app.width / 2 + 50, app.height / 2 + 140 )
    canvas.create_text(app.width / 2, app.height / 2 + 120, text="Highscores", font = "arial 9 bold")
    #Player name
    canvas.create_rectangle(0, 0, 300, 100)
    canvas.create_text(150, 30, text = f"Current Player: {app.playerName}", 
                        font = "arial 11 bold")
    canvas.create_text(150, 60, text = "click to change name", 
                        font = "arial 10 bold")

################################################################################
# Options Mode
################################################################################

def optionsMode_mousePressed(app, event):
    backXBounds = 0 < event.x < 80
    backYBounds = 0 < event.y < 40

    diffXBounds = app.width / 2 - 100 < event.x < app.width / 2 + 100
    easyY = 250 < event.y < 300
    mediumY = 325 < event.y < 375
    hardY = 400 < event.y < 450

    if (backXBounds and backYBounds):
        app.mode = 'menuMode'

    if (diffXBounds and easyY):
        app.difficulty = 0
    if (diffXBounds and mediumY):
        app.difficulty = 1
    if (diffXBounds and hardY):
        app.difficulty = 2

def optionsMode_redrawAll(app, canvas):

    easyColor = "white"
    mediumColor = "white"
    hardColor = "white"

    if app.difficulty == 0:
        easyColor = "light green"
    elif app.difficulty == 1:
        mediumColor = "gold"
    elif app.difficulty == 2:
        hardColor = "tomato"


    canvas.create_text(app.width / 2, 100, text = "Options",
                                font = "Arial 30 bold")
    #back button
    canvas.create_rectangle(0, 0, 80, 40)
    canvas.create_text(40, 20, text="Back")
    canvas.create_text(app.width / 2, 200, text = "Choose Difficulty", 
                        font = "Arial 20 bold")
    canvas.create_rectangle(app.width / 2 - 100, 250,
                        app.width / 2 + 100, 300, fill = easyColor)
    canvas.create_text(app.width / 2, 275, text = "Easy", 
                        font = "Arial 15 bold")

    canvas.create_rectangle(app.width / 2 - 100, 325,
                        app.width / 2 + 100, 375, fill = mediumColor)
    canvas.create_text(app.width / 2, 350, text = "Medium", 
                        font = "Arial 15 bold")

    canvas.create_rectangle(app.width / 2 - 100, 400,
                        app.width / 2 + 100, 450, fill = hardColor)
    canvas.create_text(app.width / 2, 425, text = "Hard", 
                        font = "Arial 15 bold")


################################################################################
# Highscore Mode
################################################################################
def highscoreMode_mousePressed(app, event):
    backXBounds = 0 < event.x < 80
    backYBounds = 0 < event.y < 40
    resetXBounds = app.width - 80 < event.x < app.width
    resetYBounds = app.height - 40 < event.y < app.height

    if (backXBounds and backYBounds):
        app.mode = "menuMode"

    if (resetXBounds and resetYBounds):
        writeFile("highscores.txt", "")
        app.highscores = readAndSortHighscores()




def highscoreMode_drawHighscores(app, canvas):
    if (app.highscores == []):
        canvas.create_text(app.width / 2, 200, text = "No scores submitted yet")
    for i in range(len(app.highscores)-1, -1, -1):
        rank = len(app.highscores) - i
        currentName = app.highscores[i][1]
        currentScore = app.highscores[i][0]
        canvas.create_text(app.width / 2, (100 + rank*15), text = f"{rank}. {currentName}  {currentScore}")
        


def highscoreMode_redrawAll(app, canvas):

    canvas.create_text(app.width / 2, 50, text = "Highscores",
                                font = "Arial 30 bold")
    #back button
    canvas.create_rectangle(0, 0, 80, 40)
    canvas.create_text(40, 20, text="Back")

    #highscores
    highscoreMode_drawHighscores(app, canvas)
    
    #reset button
    canvas.create_rectangle(app.width - 80, app.height - 40, app.width, app.height)
    canvas.create_text(app.width - 40, app.height - 20, text="Reset Scores")
    




################################################################################
# Main App
################################################################################



def appStarted(app):
    app.mode = "menuMode"
    app.playerName = "guest"
    app.highscores = readAndSortHighscores()
    app.difficulty = 0
    app.score = 0
    app.depth = 0
    startGame(app)


def startGame(app):
    app.scoreMultiplier = ((app.difficulty + 1) + app.depth / 10)
    createLevel(app)
    app.time = time.time()
    app.skillTime = time.time()
    app.hitWindow = 30 #player and enemy hitbox
    app.timerDelay = 20
    app.paused = False
    app.isChoosing = False
    app.pressedEsc = False
    app.showChoice = True
    app.currentChoices = list(app.graph[app.currentRoom])
    app.gameOver = False
    app.playerLost = False
    app.playerCanUseSkill = True
    app.playerUsingSkill = False
    app.skillDisplayCooldown = 0
    loadPlayerStats(app)
    loadMonsterStats(app)
    app.projectiles = []
    app.scrollX = 0
    app.scrollY = 0
    app.playerNoScrollX = app.playerX - app.scrollX
    app.playerNoScrollY = app.playerY - app.scrollY
    spawnMonsters(app)
    app.playerVisited = {app.entrance}

def loadPlayerStats(app):
    app.playerX = app.width // 2
    app.playerY = app.height // 2
    app.playerMoveSpeed = 10
    app.playerProjectileSpeed = 15
    app.playerDexterity = 35 # related to fire rate
    if app.depth == 0:
        app.playerHealth = 100 - (app.difficulty * 15)
        app.playerCurrentHealth = 100 - (app.difficulty * 15)
    app.playerDefense = 5
    app.playerAttack = 20
    app.playerFireRate = 0
    app.playerFiring = False
    app.playerTargetX = 0
    app.playerTargetY = 0
    app.playerdCol = 0
    app.playerdRow = 0

def loadMonsterStats(app):
    app.monsters = []
    app.monsterProjectileSpeed = 10 + (2 * (app.difficulty + app.depth / 10))
    app.monsterDefaultAttack = 8 + (app.difficulty + app.depth / 10)


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
        if self in app.projectiles:
            app.projectiles.remove(self)
                                                    
#adds monsters to list, called every level
def spawnMonsters(app):
    app.monsters = []
    monsterNumber = random.randint(4, 7)
    for i in range(monsterNumber):
        xPos = random.randint(app.x0, app.x1)
        yPos = random.randint(app.y0, app.y1)
        monsterHealth = 100 + (50 * (app.difficulty + app.depth / 10))
        monsterDefense = 2 * (app.difficulty + app.depth / 10)
        monsterMovespeed = 5 + (app.difficulty + app.depth / 10)
        monsterAttack = app.monsterDefaultAttack
        monsterDexterity = 6 + ((app.difficulty + app.depth / 10) * 5)
        app.monsters.append(Monster(app, xPos, yPos, monsterHealth, monsterDefense, monsterMovespeed, monsterAttack, monsterDexterity))

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
    if not app.gameOver:
        for monster in app.monsters:
            if (monster.currentHealth <= 0):
                app.monsters.remove(monster)
                app.score += int(2 * (app.scoreMultiplier))
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
        if not app.isChoosing and not app.pressedEsc:
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

        #use skill
        if (event.key == "Space" and app.playerCanUseSkill):
            app.playerUsingSkill = True
            app.playerCanUseSkill = False
            app.skillDuration = time.time()
            app.skillTime = time.time()
        
        #spawn a monster, for testing
        if (event.key == "p"):
            x = random.randint(100, 600)
            y = random.randint(100, 600)

            app.monsters.append(Monster(app, x, y, 100, 0, 3, 10, 3))

        #teleport to a room before the exit, for testing
        if (event.key == "l"):
            nearExitRoom = list(app.graph[app.exit])[0]
            switchRoom(app, nearExitRoom)
            app.currentChoices = list(app.graph[app.currentRoom])
            checkWin(app)
            spawnMonsters(app)
            app.playerdRow = 0
            app.playerdCol = 0

        if (event.key == "Escape") and app.paused == False:
            app.paused = True
            app.pressedEsc = True
            app.showMap = False

def gameMode_keyReleased(app, event):
    if not (app.paused or app.gameOver):
        if (event.key == "w"):
            app.playerdRow = 0
        if (event.key == "a"):
            app.playerdCol = 0
        if (event.key == "s"):
            app.playerdRow = 0
        if (event.key == "d"):
            app.playerdCol = 0
    

def gameMode_mousePressed(app, event):
    if not (app.paused or app.gameOver):
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

    if app.paused and app.pressedEsc:
        continueX = app.width / 2 - 50 < event.x < app.width / 2 + 50
        continueY = 300 < event.y < 350
        menuX = app.width / 2 - 50 < event.x < app.width / 2 + 50
        menuY = 400 < event.y < 450

        if (continueX and continueY):
            app.paused = False
            app.pressedEsc = False
        
        if (menuX and menuY):
            appStarted(app)

    #player died
    if (app.gameOver == True and app.playerLost == True):
        if (((app.width / 2 - 50) < event.x < (app.width / 2 + 50)) and 
            (500 < event.y < 600)):
            currentScores = readFile("highscores.txt")
            currentScores += f"\n{app.playerName} {int(app.score)}"
            writeFile("highscores.txt", currentScores)
            app.highscores = readAndSortHighscores()
            appStarted(app)

    #player made it to the end    
    if (app.gameOver == True and app.playerLost == False): 
        continueXBounds = app.width / 2 + 50 < event.x < app.width / 2 + 150
        yBounds = 500 < event.y < 550
        menuXBounds = (app.width / 2 - 150) < event.x < (app.width / 2 - 50)

        #player pressed continue
        if continueXBounds and yBounds:
            app.depth += 1
            startGame(app)

        #player pressed main menu
        if menuXBounds and yBounds:
            currentScores = readFile("highscores.txt")
            currentScores += f"\n{app.playerName} {int(app.score)}"
            writeFile("highscores.txt", currentScores)
            app.highscores = readAndSortHighscores()
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
    if not app.paused and not app.gameOver:
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

        skillCooldown = time.time() - app.skillTime
        app.skillDisplayCooldown = 15 - skillCooldown
        #checks for player skill
        if (skillCooldown > 15):
            app.playerCanUseSkill = True
        
        
        if app.playerUsingSkill:
            
            app.playerMoveSpeed = 15
            app.playerProjectileSpeed = 20
            app.playerDexterity = 45 # related to fire rate
            app.playerDefense = 10
            app.playerAttack = 30

            if (time.time() - app.skillDuration > 3):
                app.skillDuration = time.time()
                app.playerMoveSpeed = 10
                app.playerProjectileSpeed = 15
                app.playerDexterity = 35 # related to fire rate
                app.playerDefense = 5
                app.playerAttack = 20
                app.playerUsingSkill = False
                app.playerCanUseSkill = False
                








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
# Draw Functions (gameMode)
################################################################################   


def gameMode_drawPlayer(app, canvas):
    if not app.paused:
        r = 25
        cx = app.playerX
        cy = app.playerY
        eyesR = 5
        eyesX1 = cx - r/2
        eyesX2 = cx + r/2
        eyesY = cy - 5 
        canvas.create_oval(cx+r, cy+r, cx-r, cy-r, fill="light green")
        canvas.create_oval(eyesX1 + eyesR, eyesY + eyesR,
                            eyesX1 - eyesR, eyesY - eyesR, fill = "black")
        canvas.create_oval(eyesX2 + eyesR, eyesY + eyesR,
                            eyesX2 - eyesR, eyesY - eyesR, fill = "black")
        canvas.create_text(cx, cy - 2*r, text="Player")
        if app.playerUsingSkill:
            canvas.create_text(cx, cy + 1.5*r, text="POWER UP!")
    
def gameMode_drawProjectiles(app, canvas):
    if not app.paused:
        r = 5
        for projectile in app.projectiles:
            cx = projectile.x
            cy = projectile.y
            if projectile.source == "player":
                projColor = "light green"
            elif projectile.source == "monster":
                projColor = "red"
            canvas.create_oval(cx+r, cy+r, cx-r, cy-r, fill=projColor)

def gameMode_drawLevel(app, canvas):
    canvas.create_rectangle(-app.width, -app.height, app.width * 10, app.height * 10, fill="grey")
    if app.showMap:
        drawRooms(app, canvas)
        drawConnections(app, canvas)
        highlightStartAndEnd(app, canvas)
    if not app.paused:   
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
            #teeth
            canvas.create_polygon(cx-8, cy+12, cx+8, cy+12, cx, cy+20, fill="black")
            canvas.create_polygon(cx-16, cy+12, cx, cy+12, cx-8, cy+20, fill="black")
            canvas.create_polygon(cx, cy+12, cx+16, cy+12, cx+8, cy+20, fill="black")
            #eyes
            canvas.create_polygon(cx-15, cy-15, cx, cy-15, cx-8, cy-5, fill="black")

            canvas.create_polygon(cx+15, cy-15, cx, cy-15, cx+8, cy-5, fill="black")

        
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
        canvas.create_text(app.playerX - 40 + healthBarLength/2, 
                            app.playerY - 40 + healthBarThickness/2, 
                            text = f"{int(app.playerCurrentHealth)}/{app.playerHealth}", font="arial 6")

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
        canvas.create_text(app.width /2 , app.height / 2 - 100, 
                            text=f"Current Room: Room {app.currentRoom}", font = "arial 13 bold")
        for i in range(len(app.currentChoices)):
            currentchoice = app.currentChoices[i]
            choiceColor = "yellow"
            choiceText = f"Room {currentchoice}"
            if currentchoice in app.playerVisited:
                choiceColor = "light green"
                choiceText = f"Room {currentchoice} (visited)"
            boxWidth = (x1 - x0) / len(app.currentChoices)
            choiceX0 = x0 + (i * boxWidth)
            choiceY0 = y0
            choiceX1 = x0 + ((i + 1)* boxWidth)
            choiceY1 = y1
            canvas.create_rectangle(choiceX0, choiceY0, choiceX1, choiceY1, fill = choiceColor)
            textX = (choiceX0 + choiceX1) / 2
            textY = (choiceY0 + choiceY1) / 2
            canvas.create_text(textX, textY, text = choiceText,  font = "arial 13 bold")

def gameMode_drawGameOver(app, canvas):
    x0 = app.width / 2 - 50
    x1 = app.width / 2 + 50
    y0 = 500
    y1 = 600
    canvas.create_text(app.width / 2, 100, text = "Game Over!", font = "arial 50 bold")
    canvas.create_text(app.width / 2, 300, text = "You Died!", font = "arial 50 bold")
    canvas.create_rectangle(x0, y0, x1, y1)
    canvas.create_text(app.width / 2, 550, text = "Main Menu", font = "arial 13 bold")

def gameMode_drawPlayerWin(app, canvas):
    x0 = app.width / 2 - 150
    x1 = app.width / 2 - 50
    y0 = 500
    y1 = 550
    x2 = app.width / 2 + 50
    x3 = app.width / 2 + 150
    canvas.create_text(app.width / 2, 100, text = "You Win!", font = "arial 30 bold")
    canvas.create_text(app.width / 2, 300, text = "You made it to the exit", font = "arial 30 bold")
    canvas.create_rectangle(x0, y0, x1, y1)
    canvas.create_text(app.width / 2 - 100 , 525, text = "Main Menu", font = "arial 13 bold")
    canvas.create_rectangle(x2, y0, x3, y1)
    canvas.create_text(app.width / 2 + 100 , 525, text = "Continue", font = "arial 13 bold")

#draws what the player sees when they hit escape to pause
def gameMode_drawEscape(app, canvas):
    x0 = app.width / 2 - 50
    x1 = app.width / 2 + 50
    y0 = 300
    y1 = 350
    y2 = 400
    y3 = 450
    canvas.create_rectangle(x0, y0, x1, y1)
    canvas.create_text(app.width / 2, 325, text = "Continue", font = "arial 13 bold")
    canvas.create_rectangle(x0, y2, x1, y3)
    canvas.create_text(app.width / 2, 425, text = "Main Menu", font = "arial 13 bold")

#draws score, difficulty, skill message, etc.
def gameMode_drawMiscText(app, canvas):
    difficulty = ["Easy", "Medium", "Hard"]

    canvas.create_text(app.width - 100, 40, 
    text = f"Difficulty: {difficulty[app.difficulty]}" , font = "arial 13 bold")

    canvas.create_text(app.width - 100, 80, 
    text = f"Score: {app.score}", font = "arial 13 bold" )

    canvas.create_text(app.width - 100, 120, 
    text = f"Depth: {app.depth}", font = "arial 13 bold"  )

    if app.playerCanUseSkill:
        skillText = "press Space to use skill!"
    elif app.playerUsingSkill:
        skillText = "your movement speed, attack speed, defense, and attack is greatly increased."
    else:
        skillText = f"your skill will be avaliable in:{int(app.skillDisplayCooldown)}"
    
    canvas.create_text(app.width/2, app.height - 50, 
                    text = skillText, font = "arial 13 bold")

    


def gameMode_redrawAll(app, canvas):
    if not app.gameOver:
        gameMode_drawLevel(app, canvas)
        gameMode_drawPlayer(app, canvas)
        gameMode_drawProjectiles(app, canvas)
        gameMode_drawMonsters(app, canvas)
        gameMode_drawHealth(app, canvas)
        gameMode_drawChoice(app, canvas)
        gameMode_drawMiscText(app, canvas)
    if app.paused:
        canvas.create_text(app.width/2, 100, text = "paused", font = "arial 20 bold")

    if app.paused and app.pressedEsc:
        gameMode_drawEscape(app, canvas)
    if app.gameOver and app.playerLost:
        gameMode_drawGameOver(app, canvas)
    elif (app.gameOver == True) and (app.playerLost == False):
        gameMode_drawPlayerWin(app, canvas)
    

runApp(width = 1280, height = 720)

