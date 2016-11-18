from hlt import *
from networking import *
import random
import math

myID, gameMap = getInit()
sendInit("aranair")

xs = { 1: 0, 2: 1, 3: 0, 4: -1 }
ys = { 1: -1, 2: 0, 3: 1, 4: 0 }
state = [[-1] * gameMap.height] * gameMap.width

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
            count += math.ceil(moveCount / 50)
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

def findBestRatio(gameMap, x, y):
    minRatio = 300.0
    direction = False
    for d in CARDINALS:
        newSite = gameMap.getSite(Location(x, y), d)
        # new site is weaker
        if newSite.production == 0:
            ratio = 300
        else:
            ratio = float(newSite.strength) / float(newSite.production)

        if newSite.owner != myID and newSite.strength < gameMap.getSite(Location(x, y)).strength and ratio < minRatio:
            minRatio = ratio
            direction = d

    return direction;

def findBestProduction(gameMap, x, y):
    bestProduction = 999.0
    direction = False
    for d in CARDINALS:
        newSite = gameMap.getSite(Location(x, y), d)
        if newSite.owner != myID and newSite.strength < gameMap.getSite(Location(x, y)).strength and newSite.production > bestProduction:
            bestProduction = product
            direction = d

    return direction;

def findBest(gameMap, x, y):
    global state
    currentSite = gameMap.getSite(Location(x, y))

    surroundings = [
        findBestRecursive(gameMap, x, y, 1, 4), # -> (1, 1) -> (1, 0)
        findBestRecursive(gameMap, x, y, 2, 4),
        findBestRecursive(gameMap, x, y, 3, 4),
        findBestRecursive(gameMap, x, y, 4, 4)
    ]

    f = open('workfile', 'a')
    for s in surroundings:
        for item in s:
          f.write("%s\n" % item)
        f.write("-\n")

    bestSquare = min(surroundings, key=lambda x: x[0])
    bestRatio = bestSquare[0]
    bestCost = bestSquare[1]
    bestDirection = bestSquare[2]
    bestRemaining = bestCost - currentSite.strength
    isFriendly = bestSquare[4] == 'friendly'

    # ratio=4.5, cost=12
    f.write("at (%s, %s)- best(r, c, def, d): %s, %s, %s, %s\n" % (x, y, bestRatio, bestCost, bestRemaining, bestDirection))
    
    if bestCost > 0 and isFriendly and bestRemaining < 0 and bestRatio != 999.0:
        f.write("0000000000\n")
        f.write("----------\n")
        f.close()
        return bestSquare[3] # go to friendly to help
    if bestCost < 0 and isFriendly:
        # Friendly can already handle it, stay
        f.write("111111111111\n")
        f.write("----------\n")
        f.close()
        return False
    elif bestRemaining < 0 and bestRatio != 999.0 and not isFriendly:
        # Enemy square
        f.write("22222222222\n")
        f.write("----------\n")
        f.close()
        return bestDirection
    else:
        f.write("333333333\n")
        f.write("----------\n")
        f.close()
        return False
    # lowest = 999.0
    # for d in CARDINALS:
    #     dVal = findBestRecursive(gameMap, x, y, d, 2)
    #     if dVal < lowest:
    #         lowest = d
    #         direction = d

    # return direction;

def findBestRecursive(gameMap, x, y, d, count):
    #---- Base cases
    newX = (x + xs[d]) % gameMap.width
    newY = (y + ys[d]) % gameMap.height
    currentSite = gameMap.getSite(Location(newX, newY))

    if count == 0 and currentSite.owner == myID: 
        # No path within 2/3 steps
        return [999.0, -1, -1]

    if currentSite.owner != myID:
        if currentSite.production == 0:
            ratio = 999.0
        else:
            ratio = float(currentSite.strength) / float(currentSite.production)

        return [ratio, currentSite.strength, d, d, 'enemy']
    #----

    surroundings = []

    possibleDirections = [1, 2, 3, 4]
    reverseDir = [3, 4, 1, 2]
    possibleDirections.remove(reverseDir[d-1]) # remove opposite direction where it came from
    for possibleDirection in possibleDirections:
        surroundings.append(findBestRecursive(gameMap, newX, newY, possibleDirection, count-1))

    # 30 | 70 | -100-
    # Example: (best, 100, 2) -> (best, 30, 2) -> (best, 0, 2)

    bestSquare = min(surroundings, key=lambda x: x[0])
    bestRatio = bestSquare[0]
    bestCost = bestSquare[1]
    bestDirection = bestSquare[2]
    bestRemaining = bestCost - currentSite.strength

    # d == original direction
    return [bestRatio, bestRemaining, bestDirection, d, 'friendly']

def findMostSurroundedKill(gameMap, x, y):
    directions = { 1: 0, 2: 0, 3: 0, 4: 0 }
    for d in CARDINALS:
        newSite = gameMap.getSite(Location(x, y), d)
        # new site is weaker
        if newSite.owner != myID and newSite.strength < gameMap.getSite(Location(x, y)).strength:
            possibleDirections = [1, 2, 3, 4]
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
            currentSite = gameMap.getSite(Location(x, y))

            if currentSite.owner == myID:
                movedPiece = False

                # Find most productive slot
                newDirection = findBest(gameMap, x, y)
                if newDirection:
                    moves.append(Move(Location(x, y), newDirection))
                    movedPiece = True
                else:
                    movedPiece = True
                    moves.append(Move(Location(x, y), STILL))

                # # Stay if not strong enough
                # minProdMultiplication = 7 - (float(moveCount)/50)
                # if not movedPiece and currentSite.strength < currentSite.production * minProdMultiplication:
                #     moves.append(Move(Location(x, y), STILL))
                #     movedPiece = True

                # if not movedPiece:
                #     if moveCount > 40:
                #         d = findNearestBorderDirection(gameMap, x, y, moveCount)
                #     else:
                #         d = findAnyEmpty(gameMap, x, y)

                #     if d:
                #         moves.append(Move(Location(x, y), d))
                #         movedPiece = True

                # if not movedPiece:
                #     moves.append(Move(Location(x, y), random.choice([1, 2, 3, 4])))
                #     movedPiece = True


    moveCount += 1
    sendFrame(moves)
