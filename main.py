# -*- coding: utf-8 -*-

#Módulos:
import pygame
import pygame.gfxdraw
import sys
from pygame.locals import *

pygame.init()
pygame.mixer.init()


class Player():

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 30
        self.LEFT = False
        self.RIGHT = False
        self.UP = False
        self.DOWN = False
        self.inFog = False
        self.timeInFogLeft = 5
        self.speed = 0.5

    def movement(self):
        if self.inFog:
            self.speed = 0.25
        else:
            self.speed = 1
        if (self.RIGHT) and (self.y < width - 60):
            self.x = self.x + self.speed
        if (self.LEFT) and (self.x > 0):
            self.x = self.x - self.speed
        if (self.UP) and (self.y > 0):
            self.y = self.y - self.speed
        if (self.DOWN) and (self.y < height - 60):
                self.y = self.y + self.speed

    def draw(self, surface, scale):
        pygame.draw.rect(surface, (0, 0, 255), (self.x*scale, self.y*scale, scale, scale))

    def drawInMinimap(self, surface, scale):
        pygame.draw.rect(surface, (0, 0, 255), (self.x*scale, self.y*scale, scale, scale))

    def place(self, cellmap, scale):
        placed = False
        while not placed:
            x = random.randint(0, len(cellmap) - 1)
            y = random.randint(len(cellmap[0]) - 5, len(cellmap[0]) - 1)
            if(not cellmap[x][y]):
                placed = True
        self.x = x
        self.y = y


def terminate():
    pygame.quit()
    sys.exit()

import random

chanceToStartAlive = 0.40


def initialiseMap(cellmap):
    for x in range(0, len(cellmap)):
        for y in range(0, len(cellmap[x])):
            if(random.random() < chanceToStartAlive):
                cellmap[x][y] = True
    return cellmap


def countAliveNeighbours(cellmap, x, y):
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            neighbour_x = x + i
            neighbour_y = y + j
            #If we're looking at the middle point
            if(i == 0 and j == 0):
                #Do nothing, we don't want to add ourselves in!
                pass
            #In case the index we're looking at is off the edge of the map
            elif(neighbour_x < 0 or neighbour_y < 0 or neighbour_x >= len(cellmap) or neighbour_y >= len(cellmap[0])):
                count += 1
            #Otherwise, a normal check of the neighbour
            elif(cellmap[neighbour_x][neighbour_y]):
                count += 1
    return count


def doSimulationStep(oldMap):
    deathLimit = 3
    birthLimit = 4
    newMap = [[False for x in range(len(oldMap[0]))] for y in range(len(oldMap))]
    #//Loop over each row and column of the map
    for x in range(0, len(oldMap)):
        for y in range(0, len(oldMap[x])):
            nbs = countAliveNeighbours(oldMap, x, y)
            #print(nbs)
            #//The new value is based on our simulation rules
            #//First, if a cell is alive but has too few neighbours, kill it.
            if(oldMap[x][y]):
                if(nbs < deathLimit):
                    newMap[x][y] = False
                    #print("Living cell killed")
                else:
                    newMap[x][y] = True
                    #print("Living cell mantained")
            #Otherwise, if the cell is dead now, check if it has the right number of neighbours to be 'born'
            else:
                if(nbs > birthLimit):
                    newMap[x][y] = True
                    #print("New living cell")
                else:
                    newMap[x][y] = False
                    #print("Dead cell mantained")
    return newMap


def generateMap(w, h, numberOfSteps):
    #//Create a new map
    cellmap = [[False for x in range(w)] for y in range(h)]
    #//Set up the map with random values
    cellmap = initialiseMap(cellmap)
    #//And now run the simulation for a set number of steps
    for i in range(0, numberOfSteps):
        cellmap = doSimulationStep(cellmap)
    return cellmap


def truncate(number):
    return int(str(number).split(".")[0])

#Inicializacion del juego:

infoObject = pygame.display.Info()
(width, height) = (infoObject.current_w, infoObject.current_h)

mapScaleFactor = 30
cellSize = 4
bigCellSize = mapScaleFactor

cellmap = generateMap(height / mapScaleFactor, width / mapScaleFactor, 8)

player = Player()
player.place(cellmap, mapScaleFactor)

#scalledmap = [[False for x in range(w*mapScaleFactor)] for y in range(h*mapScaleFactor)]

FPS = 32
fpsClock = pygame.time.Clock()
MAIN = True

screen = pygame.display.set_mode((width, height))

minimap = pygame.Surface((width / mapScaleFactor * cellSize, height / mapScaleFactor * cellSize)).convert_alpha()
minimap.set_alpha(100)

##################################################################

#Bucle del juego:
while MAIN:

    pygame.display.set_caption('Cellular map')
    if(cellmap[truncate(player.x)][truncate(player.y)] == True):
        player.inFog = True
    else:
        player.inFog = False

    player.movement()
    for x in range(len(cellmap)):
        for y in range(len(cellmap[x])):
            if cellmap[x][y]:
                pygame.draw.rect(screen, (30, 30, 30), (bigCellSize * x, bigCellSize * y, bigCellSize, bigCellSize))
            else:
                pygame.draw.rect(screen, (0, 255, 0), (bigCellSize * x, bigCellSize * y, bigCellSize, bigCellSize))

    player.draw(screen, bigCellSize)

    for x in range(len(cellmap)):
        for y in range(len(cellmap[x])):
            if cellmap[x][y]:
                pygame.gfxdraw.box(minimap, pygame.Rect(cellSize * x, cellSize * y, cellSize, cellSize), (30, 30, 30,127))
            else:
                pygame.gfxdraw.box(minimap, pygame.Rect(cellSize * x, cellSize * y, cellSize, cellSize), (0, 255, 0,127))

    player.drawInMinimap(minimap, cellSize)
    screen.blit(minimap, (0, 0))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            MAIN = False
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == K_RIGHT:
                player.RIGHT = True
            if event.key == K_LEFT:
                player.LEFT = True
            if event.key == K_UP:
                player.UP = True
            if event.key == K_DOWN:
                player.DOWN = True
        if event.type == pygame.KEYUP:
            if event.key == K_RIGHT:
                player.RIGHT = False
            if event.key == K_LEFT:
                player.LEFT = False
            if event.key == K_UP:
                player.UP = False
            if event.key == K_DOWN:
                player.DOWN = False
    pygame.display.update()
    pygame.display.flip()
    fpsClock.tick(FPS)