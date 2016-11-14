from hlt import *
from networking import *

myID, gameMap = getInit()
sendInit("aranair")

xs = { 1: 0, 2: 1, 3: 0, 4: -1 }
ys = { 1: -1, 2: 0, 3: 1, 4: 0 }

def findNearestBorderDirection(gameMap, x, y):
    currentStr = gameMap.getSite(Location(x, y)).strength
    # f = open('workfile', 'a')
    directions = {}
    # f.write("current: (" + str(x) + ", " + str(y) + ")\n")
    for d in CARDINALS:
        newSite = gameMap.getSite(Location(x, y), d)
        count = 1
        incrementalRound = 1
        while newSite.owner == myID and count < 15:
            if newSite.strength + currentStr > 200:
                count = 999
                break

            count += (incrementalRound * 2 * count)
            incrementalRound += 1
            newX = (x + (xs[d] * count)) % gameMap.width
            newY = (y + (ys[d] * count)) % gameMap.height
            # f.write(str(d) + ":(" + str(newX) + ", " + str(newY) + ")\n")
            if gameMap.inBounds(Location(newX, newY)):
                newSite = gameMap.getSite(Location(newX, newY))
            else:
                # f.write("out of bounds\n")
                break

        directions[d] = count

    minElement = min(directions.items(), key=lambda x: x[1])
    if minElement[1] > 8:
        return random.choice([1,2,3,4])
    else:
        return minElement[0]
    # f.write("--------\n")
    # f.close()

def findGreatestProductionDirection(gameMap, x, y):
    maxProduction = 0
    direction = False
    for d in CARDINALS:
        newSite = gameMap.getSite(Location(x, y), d)
        # new site is weaker
        if newSite.owner != myID and newSite.strength < gameMap.getSite(Location(x, y)).strength and newSite.production > maxProduction:
            maxProduction = newSite.production
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

                newDirection = findGreatestProductionDirection(gameMap, x, y)
                if newDirection:
                    moves.append(Move(Location(x, y), newDirection))
                    movedPiece = True
                    break

                # minProdMultiplication = 10 - (math.pow(1000, float(moveCount)/1000))
                minProdMultiplication = 7 - (float(moveCount)/50)
                if not movedPiece and gameMap.getSite(Location(x, y)).strength < gameMap.getSite(Location(x, y)).production * minProdMultiplication:
                    moves.append(Move(Location(x, y), STILL))
                    movedPiece = True

                # Move to border instead of randomly
                if not movedPiece:
                    # moves.append(Move(Location(x, y), NORTH if bool(int(random.random() * 2)) else WEST))
                    # moves.append(Move(Location(x, y), random.choice([1,2,3,4])))
                    moves.append(Move(Location(x, y), findNearestBorderDirection(gameMap, x, y)))
                    movedPiece = True

                moveCount += 1

    sendFrame(moves)
