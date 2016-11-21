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

def findNearestBorderDirection(gameMap, x, y):
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
            count += math.ceil(frameCount / 50)
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
    # f = open('workfile', 'a')
    # f.write("FIND BEST: (%s, %s)\n" % (x, y))
    global state

    # cached = state[x][y]
    # if type(cached) is not int:
    #     # cached
    #     bestRatio, bestCost, bestDirection = cached[:3]
    #     bestRemaining = bestCost - currentSite.strength 
    #     isFriendly = cached[3] == 'friendly'

    #     if bestCost < 0 and isFriendly: # friendly tile and the tile already has a target
    #         continue

    #     if isFriendly: # Friendly
    #         if bestCost > 0 and bestRemaining < 0: # Friendly can't handle, but with you, it can
    #             chosen = move
    #     else: # Enemy
    #         if bestRemaining < 0: # You can handle
    #             chosen = move

    #     if chosen:
    #         break
    #     # f.write("READING FROM CACHE FOR: (%s, %s)\n" % (x, y))
    #     # f = open('workfile', 'a')
    #     # for s in state[x][y]:
    #     #     f.write("L101: %s\n" % s)
    #     # f.close()
    #     return state[x][y]
    
    # f.write("CALCULATING FOR: (%s, %s)\n" % (x, y))

    depth = 5
    currentSite = gameMap.getSite(Location(x, y))

    surroundings = [
        findBestRecursive(gameMap, x, y, 1, depth), # -> (1, 1) -> (1, 0)
        findBestRecursive(gameMap, x, y, 2, depth),
        findBestRecursive(gameMap, x, y, 3, depth),
        findBestRecursive(gameMap, x, y, 4, depth)
    ]

    # for s in surroundings:
    #     for item in s:
    #       f.write("%s\n" % item)
    #     f.write("-\n")
    # f.close()

    surroundings.sort(key=lambda x: x[0])
    chosen = False
    for move in surroundings:
        bestRatio, bestCost, bestDirection = move[:3]
        bestRemaining = bestCost - currentSite.strength 
        isFriendly = move[3] == 'friendly'

        if bestCost < 0 and isFriendly: # friendly tile and the tile already has a target
            continue

        if isFriendly: # Friendly
            if bestCost > 0 and bestRemaining < 0: # Friendly can't handle, but with you, it can
                chosen = move
        else: # Enemy
            if bestRemaining < 0: # You can handle
                chosen = move

        if chosen:
            break

    if chosen:
        state[x][y] = chosen
        # f = open('workfile', 'a')
        # for s in state[x][y]:
        #     f.write("line151: : %s\n" % s)
        # f.close()
        return chosen

def findBestRecursive(gameMap, x, y, d, count):
    global state

    # 10 -> 20 -> 5 (3)
    # at 10, 
        # goes to 20
        # goes to 5, returns (r, 5, 3) to 20 --> remembers [r, 5, 3, 'enemy']
        # bestRemaining < 0, enemy -> move(3) --> remembers [r, -15, 3, 'enemy']
        # goes back to 10 with [r, -15, 3] (don't move, choose another)

    # at 20,
        # cached [r, -15, 3, 'enemy'] -> 
    #---- Base cases
    newX = (x + xs[d]) % gameMap.width
    newY = (y + ys[d]) % gameMap.height

    cached = state[newX][newY]
    currentSite = gameMap.getSite(Location(newX, newY))

    cachedResp = False
    if type(cached) is not int:
        bestRatio, bestCost, bestDirection = cached[:3]
        bestRemaining = bestCost - currentSite.strength 
        isFriendly = cached[3] == 'friendly'

        if bestCost < 0 and isFriendly: # friendly tile and the tile already has a target
            cachedResp = False

        if isFriendly: # Friendly
            if bestCost > 0 and bestRemaining < 0: # Friendly can't handle, but with you, it can
                cachedResp = cached
        else: # Enemy
            if bestRemaining < 0: # You can handle
                cachedResp = cached

        if cachedResp:
            return cached
        # f.write("READING FROM CACHE FOR: (%s, %s)\n" % (x, y))
        # f = open('workfile', 'a')
        # for s in state[x][y]:
        #     f.write("L101: %s\n" % s)
        # f.close()

    if currentSite.owner == myID:
        if count == 0:
            return [999.0, -1, -1, 'friendly']
    else:
        if currentSite.production == 0:
            ratio = 999.0
        else:
            ratio = float(currentSite.strength) / float(currentSite.production)

        state[newX][newY] = [ratio, currentSite.strength, d, 'enemy']

        return state[newX][newY]
    #----

    surroundings = []
    possibleDirections = [1, 2, 3, 4]
    reverseDir = [3, 4, 1, 2]
    possibleDirections.remove(reverseDir[d-1]) # remove opposite direction where it came from

    for pd in possibleDirections:
        surroundings.append(findBestRecursive(gameMap, newX, newY, pd, count-1))

    surroundings.sort(key=lambda x: x[0])
    chosen = False
    for move in surroundings:
        bestRatio, bestCost, bestDirection = move[:3]
        isFriendly = move[3] == 'friendly'
        bestRemaining = bestCost - currentSite.strength

        # Friendly tile and the tile already has a target
        if bestCost < 0 and isFriendly:
            continue

        if bestRatio == 999.0:
            continue

        if isFriendly:
            if bestCost > 0 and bestRemaining < -1: # Friendly can't handle, but with you, it can
                chosen = move
        elif bestRemaining < -1: # You can handle
            chosen = move

        if chosen:
            break

    if chosen:
        state[newX][newY] = [chosen[0], chosen[1] - currentSite.strength, d, chosen[3]]
    else:
        state[newX][newY] = [999.0, -1, -1, 'friendly']


    # f = open('workfile', 'a')
    # for s in state[newX][newY]:
    #     f.write("L219: %s\n" % s)
    # f.close()
    return state[newX][newY]

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


frameCount = 0

########## NOTE NOTE NOTE NOTE NOTE NOTE
# JUST REMEMBER THE PROPERTIES AND NOT THE DECISION

while True:
    global state
    moves = []
    gameMap = getFrame()
    state = [[-1] * gameMap.height] * gameMap.width

    for y in range(gameMap.height):
        for x in range(gameMap.width):
            currentSite = gameMap.getSite(Location(x, y))

            if currentSite.owner == myID:
                movedPiece = False

                if frameCount < 200:
                    # Find most productive slot
                    move = findBest(gameMap, x, y)
                    if move and move[0] != 999.0:
                        newDirection = move[2]
                        moves.append(Move(Location(x, y), newDirection))
                        movedPiece = True
                    elif frameCount < 50:
                        movedPiece = True
                        moves.append(Move(Location(x, y), STILL))
                    else:
                        minProdMultiplication = 7 - (float(frameCount)/50)
                        if currentSite.strength < currentSite.production * minProdMultiplication:
                            moves.append(Move(Location(x, y), STILL))
                            movedPiece = True
                        else:
                            moves.append(Move(Location(x, y), random.choice([1, 2, 3, 4])))
                            movedPiece = True

                    # elif frameCount < 100:
                        # movedPiece = True
                        # moves.append(Move(Location(x, y), STILL))
                    # else:
                    #     moves.append(Move(Location(x, y), random.choice([1, 2, 3, 4])))
                    #     movedPiece = True
                else:
                    minProdMultiplication = 7 - (float(frameCount)/50)
                    if not movedPiece and currentSite.strength < currentSite.production * minProdMultiplication:
                        moves.append(Move(Location(x, y), STILL))
                        movedPiece = True

                    if not movedPiece:
                        d = findNearestBorderDirection(gameMap, x, y)
                        moves.append(Move(Location(x, y), d))
                        movedPiece = True

                    if not movedPiece:
                        moves.append(Move(Location(x, y), random.choice([1, 2, 3, 4])))
                        movedPiece = True

    frameCount += 1
    sendFrame(moves)
