from hlt import *
from networking import *
import random
import math

myID, gameMap = getInit()
sendInit("aranair")

xs = { 1: 0, 2: 1, 3: 0, 4: -1 }
ys = { 1: -1, 2: 0, 3: 1, 4: 0 }

def shuff(arr):
    random.shuffle(arr)
    return arr

def findNearestBorderDirection(gameMap, x, y, moveCount):
    # f = open('workfile', 'a')
    # f.write("current: (" + str(x) + ", " + str(y) + ")\n")

    directions = {}
    currentStr = gameMap.getSite(Location(x, y)).strength

    if currentStr > 200:
        maxCount = 15
    elif currentStr > 100:
        maxCount = 10
    else:
        maxCount = 3

    for d in shuff([1, 2, 3, 4]):
        newSite = gameMap.getSite(Location(x, y), d)
        count = 1
        while newSite.owner == myID and count < maxCount:
            if currentStr < 255 and newSite.strength + currentStr > 200: 
                count = 999
                break
            # 2, 4, 8, 16
            # count += (incrementalRound * 2 * count)
            # incrementalRound *= 2
            if moveCount > 200:
                count += 4
            elif moveCount > 100:
                count += 3
            elif moveCount > 50:
                count += 2
            else:
                count += 1
            newX = (x + (xs[d] * count)) % gameMap.width
            newY = (y + (ys[d] * count)) % gameMap.height
            # f.write(str(d) + ":(" + str(newX) + ", " + str(newY) + ")\n")
            # if gameMap.inBounds(Location(newX, newY)):
            newSite = gameMap.getSite(Location(newX, newY))
            # else:
            #     break

        directions[d] = count

    minElement = min(directions.items(), key=lambda x: x[1])
    if minElement[1] >= 5 and currentStr < 250:
        # f.write("random\n")
        value = random.choice([1, 2, 3, 4])
    else:
        # f.write("str: " +  str(currentStr) + ", " + str(minElement[0]) + "\n")
        value = minElement[0]

    # f.write("--------\n")
    return value
    # f.close()

def findGreatestProductionDirectionKillable(gameMap, x, y):
    maxProduction = 0
    direction = False
    for d in CARDINALS:
        newSite = gameMap.getSite(Location(x, y), d)
        # new site is weaker
        if newSite.owner != myID and newSite.strength < gameMap.getSite(Location(x, y)).strength and newSite.production > maxProduction:
            maxProduction = newSite.production
            direction = d

    return direction;

def findMostSurroundedKill(gameMap, x, y):
    directions = { 1: 0, 2: 0, 3: 0, 4: 0 }
    for d in CARDINALS:
        newSite = gameMap.getSite(Location(x, y), d)
        # new site is weaker
        if newSite.owner != myID and newSite.strength < gameMap.getSite(Location(x, y)).strength:
            possibleDirections = CARDINALS
            possibleDirections.remove(d)
            count = 0
            for d2 in possibleDirections:
                if newSite.owner != myID:
                    count += 1 

            directions[d] += count

    maxElement = max(directions.items(), key=lambda x: x[1])
    if maxElement[1] == 0:
        return False
    else:
        return maxElement[0]

def findAnyEmpty(gameMap, x, y):
    direction = False
    for d in CARDINALS:
        newSite = gameMap.getSite(Location(x, y), d)
        if newSite.owner == myID and newSite.strength + gameMap.getSite(Location(x, y)).strength < 255:
            direction = d

    return direction;


while True:
    moves = []
    gameMap = getFrame()
    moveCount = 0
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            if gameMap.getSite(Location(x, y)).owner == myID:
                movedPiece = False

                # Find most productive slot
                newDirection = findGreatestProductionDirectionKillable(gameMap, x, y)
                if newDirection:
                    moves.append(Move(Location(x, y), newDirection))
                    movedPiece = True
                    break

                # Stay if not strong enough
                minProdMultiplication = 7 - (float(moveCount)/50)
                if not movedPiece and gameMap.getSite(Location(x, y)).strength < gameMap.getSite(Location(x, y)).production * minProdMultiplication:
                    moves.append(Move(Location(x, y), STILL))
                    movedPiece = True

                # Move to border instead of randomly
                if not movedPiece:
                    d = findNearestBorderDirection(gameMap, x, y, moveCount)
                    if d:
                        moves.append(Move(Location(x, y), d))
                        movedPiece = True

                if not movedPiece:
                    d = findAnyEmpty(gameMap, x, y)
                    if d:
                        moves.append(Move(Location(x, y), d))
                        movedPiece = True

                if not movedPiece:
                    moves.append(Move(Location(x, y), random.choice([1, 2, 3, 4])))
                    movedPiece = True

                moveCount += 1

    sendFrame(moves)
