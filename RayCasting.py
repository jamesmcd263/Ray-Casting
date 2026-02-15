import math
import pygame
import sys

class World:   #over arching class that handles the World
    def __init__(self):
        self.press = [False, False, False, False, False, False]   #W,A,S,D,Space,Shift,Left,Right
        
        self.tiles = [0]
        self.worldType = 0
        self.generate(10, 10)

        self.player = Player(len(self.tiles)*50, len(self.tiles[0])*50, 0.0)
    
    def generate(self, X, Y):   # tile types: 0=air 1=solidBlack 2=solidColor
        if self.worldType == 0:
            self.tiles = [[0] * Y for i in range(X)]
            self.tiles[2][2] = 2
            self.tiles[2][3] = 2
            self.tiles[2][4] = 2
            self.tiles[2][5] = 2
            self.tiles[7][5] = 1
    
    def update(self, screen):
        self.player.update(screen, self.press, self.tiles)

class Player: # main character, handles rendering
    def __init__(self, xPos, yPos, angle):
        self.xPos = xPos
        self.yPos = yPos
        self.xVel = 0.0
        self.yVel = 0.0
        self.angle = angle
        self.angleVel = 0.0
        self.angleNum = 0
        self.target = None
        self.targetOffset = 0

    def arrowKey(self, left, press):
        if self.angleNum != None:
            if left:
                self.angleNum -= 1
            else:
                self.angleNum += 1
            self.angleNum %= 8
    
    def angleBetween(self, xPos, yPos):
        ang = math.atan2(yPos - self.yPos, xPos - self.xPos)*50
        if ang < 0:
            ang += math.pi*100
        return ang
    
    def printAngle(self, fov, ang):
        if (self.angle + (fov/2))%(math.pi*100) != self.angle + (fov/2) and (self.angle + (fov/2))%(math.pi*100) > ang:
            return ((self.angle + (fov/2))%(math.pi*100)) - ang
        elif (self.angle - (fov/2))%(math.pi*100) != self.angle - (fov/2) and (self.angle - (fov/2))%(math.pi*100) < ang:
            return fov - (ang - ((self.angle - (fov/2))%(math.pi*100)))
        elif ang < self.angle + (fov/2) and ang > self.angle - (fov/2):
            return self.angle + (fov/2) - ang
        return None

    def render(self, screen, tile, a, rays, dist, toRender): #midScreen = 400, distScale = 0.005, objectScale = 48000, 255/distScale = 51000, objScale*2 = 96000
        if tile == 1:
            toRender.append([dist, [(90/((dist+200)*0.005),90/((dist+200)*0.005),90/((dist+200)*0.005)), (a*(1600/rays), 400 - (48000/dist), 1600/rays, 96000/dist)]])
        elif tile == 2:
            toRender.append([dist, [(255/((dist+200)*0.005),0,160), (a*(1600/rays), 400 - (48000/dist), 1600/rays, 96000/dist)]])
            
    def update(self, screen, press, tiles):
        toRender = []
        
        #position controls, velsa
        yWalk = 0.0
        xWalk = 0.0
        maxSpeed = 2.0 #max speed of the player
        if press[0] and not(press[2]):
            yWalk += math.sin(self.angle/50)
            xWalk += math.cos(self.angle/50)
        elif press[2] and not(press[0]):
            yWalk -= math.sin(self.angle/50)
            xWalk -= math.cos(self.angle/50)

        if press[1] and not(press[3]):
            yWalk -= math.cos(self.angle/50)
            xWalk += math.sin(self.angle/50)
        elif press[3] and not(press[1]):
            yWalk += math.cos(self.angle/50)
            xWalk -= math.sin(self.angle/50)

        if math.fabs(yWalk*maxSpeed) > math.fabs(self.yVel):
            self.yVel += yWalk
        if math.fabs(xWalk*maxSpeed) > math.fabs(self.xVel):
            self.xVel += xWalk
        
        if self.xPos + self.xVel < 0 or self.xPos + self.xVel >= (len(tiles)*100) or tiles[int((self.xPos + self.xVel)//100)][int((self.yPos)//100)] != 0:
            self.xVel = 0
        if self.yPos + self.yVel < 0 or self.yPos + self.yVel >= (len(tiles[0])*100) or tiles[int((self.xPos)//100)][int((self.yPos + self.yVel)//100)] != 0:
            self.yVel = 0
        elif tiles[int((self.xPos + self.xVel)/100)][int((self.yPos + self.yVel)/100)] != 0:
            self.xVel = 0
            self.yVel = 0
        
        self.xPos += self.xVel
        self.yPos += self.yVel
        self.xVel *= 0.75
        self.yVel *= 0.75
        
        #angle controls & vel
        if self.angleNum == None:
            self.angleNum = self.angle // (12.5*math.pi)
            self.target = None
        self.angleVel = ((self.angleNum * math.pi * 12.5) - self.angle)/(math.pi * 2)
        if (self.angleNum * math.pi * 12.5) - self.angle > math.pi * 50:
            self.angleVel -= 50
        elif (self.angleNum * math.pi * 12.5) - self.angle < -math.pi * 50:
            self.angleVel += 50
        
        self.angle += self.angleVel
        self.angleVel *= 0.8
        self.angle = self.angle%(100*math.pi)
        
        #wall render calcs
        rays = 1600     #number of rays, must be clean divisor of 1600
        fov = 70        #fov of the player, a portion from 0-(pi*100)
        
        #minimizes the calculation within the for loop
        angPreCalc = self.angle - (fov / 2.0)
        tileLenX = len(tiles)
        tileLenY = len(tiles[0])

        for a in range(rays):
            x = math.cos((angPreCalc + (a * fov / rays)) / 50) / 100
            y = math.sin((angPreCalc + (a * fov / rays)) / 50) / 100
            
            rayX = (self.xPos / 100) + x
            rayY = (self.yPos / 100) + y
            dist = 1
            
            rendered = False

            while rayX < (tileLenX) and rayX >= 0 and rayY < (tileLenY) and rayY >= 0 and not(rendered):
                if tiles[math.floor(rayX)][math.floor(rayY)] != 0:
                    self.render(screen, tiles[math.floor(rayX)][math.floor(rayY)], a, rays, dist, toRender)
                    rendered = True
                else:
                    if x == 0:
                        numJumps = math.inf
                    elif x > 0:
                        numJumps = (math.ceil(rayX) - rayX) / x
                    else:
                        numJumps = (math.floor(rayX) - rayX) / x
                        
                    if y == 0:
                        yNumJumps = math.inf
                    elif y > 0:
                        yNumJumps = (math.ceil(rayY) - rayY) / y
                    else:
                        yNumJumps = (math.floor(rayY) - rayY) / y
                    
                    if yNumJumps < numJumps:
                        numJumps = yNumJumps
                    numJumps += 0.001
                    rayX += x * numJumps
                    rayY += y * numJumps
                    dist += numJumps
            if not(rendered):
                self.render(screen, 1, a, rays, dist, toRender)
        
        #render
        
        for i in toRender:
            pygame.draw.rect(screen, *i[1])
        
        #crosshair
        pygame.draw.rect(screen, (255,255,255), (780,399,40,2))
        pygame.draw.rect(screen, (255,255,255), (799,380,2,40))
                
sys.setrecursionlimit(10000)

pygame.init()

screen = pygame.display.set_mode((1600,800))

pygame.display.set_caption("Ray Casting")

world = World()

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                world.press[0] = True
            if event.key == pygame.K_a:
                world.press[1] = True
            if event.key == pygame.K_s:
                world.press[2] = True
            if event.key == pygame.K_d:
                world.press[3] = True
            if event.key == pygame.K_RIGHT:
                world.player.arrowKey(False, world.press)
                world.press[4] = True
            if event.key == pygame.K_LEFT:
                world.player.arrowKey(True, world.press)
                world.press[5] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                world.press[0] = False
            if event.key == pygame.K_a:
                world.press[1] = False
            if event.key == pygame.K_s:
                world.press[2] = False
            if event.key == pygame.K_d:
                world.press[3] = False
            if event.key == pygame.K_RIGHT:
                world.press[4] = False
            if event.key == pygame.K_LEFT:
                world.press[5] = False
    screen.fill((50, 0, 50))
    world.update(screen)
    pygame.display.update()
    clock.tick(60)
    pygame.display.set_caption("Ray Casting   FPS: " + str(clock.get_fps() * 100 // 1 / 100))
pygame.quit()

