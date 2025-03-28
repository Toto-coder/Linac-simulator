from random import randint
from math import *
import time
from numpy import *

global rowsNumber, idElectrons, forcesChecks, idCircumference, totalCharge

rowsNumber = 150
idElectrons = 0
idCircumference = -1

particles = {}
electrons = []
circumferenceCharges = []

relativeDielectricCostant = 1
absoluteDielctricCostant = 8.854 * (10**-12) * relativeDielectricCostant

forces = {}
forcesChecks = 0

totalCharge = - (1.3*10**-7)

def circumference(particles):

    circumferenceValue = 0

    for index in particles:

        row = particles[index]

        if row == particles[1]:

            circumferenceValue += 4

        else:

            circumferenceValue += 2

    return circumferenceValue

def chargeCircumference():

    global particles, idCircumference, circumferenceCharges, totalCharge

    circumferenceLength = circumference(particles) - 4

    charge = totalCharge / circumferenceLength
    
    for index in particles:

        row = particles[index]

        idCircumference += 2

        for rowIndex, particle in enumerate(row):

            if particle == "X":

                charge1 = {"id": idCircumference, "charge": charge, "x": rowIndex, "y": index * 2}
                charge2 = {"id": idCircumference + 1, "charge": charge, "x": len(row) - 1 - rowIndex, "y": index * 2}

                particles[index][rowIndex] = f"c-{idCircumference}"
                particles[index][len(row) - 1 - rowIndex] = f"c-{idCircumference + 1}"

                circumferenceCharges.append(charge1)
                circumferenceCharges.append(charge2)

                break

def checkMovement(interval):

    global rowsNumber

    removeList = []

    for index, electron in enumerate(electrons):

        initialSpeed = electron["speed"]
        speedAngle = electron["angleSpeed"]
        acceleration = electron["acceleration"]
        accelerationAngle = electron["angleAcceleration"]

        accelerationX = acceleration * cos(accelerationAngle)
        accelerationY = (acceleration * sin(accelerationAngle)) * (-1)

        initialSpeedX = initialSpeed * cos(speedAngle)
        initialSpeedY = (initialSpeed * sin(speedAngle))

        finalSpeedX = initialSpeedX + (accelerationX * interval)
        finalSpeedY = initialSpeedY + (accelerationY * interval)

        distanceX = (initialSpeedX * interval) + (0.5 * accelerationX * (interval ** 2))
        distanceY = (initialSpeedY * interval) + (0.5 * accelerationY * (interval ** 2))

        finalSpeedAngle = arctan(abs(finalSpeedY) / abs(finalSpeedX))

        if finalSpeedX > 0 and finalSpeedY < 0 :

            finalSpeedAngle = (pi * 2) - finalSpeedAngle

        elif finalSpeedX < 0 and finalSpeedY > 0:

            finalSpeedAngle = pi - finalSpeedAngle

        elif finalSpeedX < 0 and finalSpeedY < 0:

            finalSpeedAngle = pi + finalSpeedAngle

        distanceX = int(distanceX.round(decimals=0))
        distanceY = int(distanceY.round(decimals=0))

        particles[int(electron["y"] / 2)][electron["x"]] = f"X"

        electron["x"] = electron["x"] + distanceX
        electron["y"] = electron["y"] + distanceY

        electron["angleSpeed"] = finalSpeedAngle
        electron["speed"] = sqrt((finalSpeedX ** 2) + (finalSpeedY ** 2))

        try:

            if particles[int(electron["y"] / 2)][electron["x"]] != "X" and "e-" not in particles[int(electron["y"] / 2)][electron["x"]]:

                removeList.append(index)

                continue

        except:

            removeList.append(index)

            continue

        particles[int(electron["y"] / 2)][electron["x"]] = f"e-{electron['id']}"

        electrons[index] = electron

    removeList.sort()
    removeList.reverse()

    for index in removeList:

        electron = electrons[index]

        for force in forces:

            if force.endswith(f"-{electron['id']}") or force.startswith(f"{electron['id']}-"):

                forces[force]["force-x"] = 0
                forces[force]["force-y"] = 0

        electrons.pop(index)

def checkForces():

    global forcesChecks

    forcesChecks += 1

    for firstElectron in electrons:

        firstCharge = firstElectron["charge"]

        for secondElectron in electrons:

            if firstElectron == secondElectron:

                continue

            try:

                if forces[f"{secondElectron['id']}-{firstElectron['id']}"]["check"] == forcesChecks:

                    continue

            except:

                pass

            try:

                forces.pop(f"{secondElectron['id']}-{firstElectron['id']}")

            except:

                pass

            secondCharge = secondElectron["charge"]

            xDistance = abs(firstElectron["x"] - secondElectron["x"])
            yDistance = abs(firstElectron["y"] - secondElectron["y"])

            distanceSquared = xDistance ** 2 + yDistance ** 2

            try: 

                angleRadians = arctan(yDistance / xDistance)

            except:

                angleRadians = pi / 2

            coulombForce = abs(firstCharge * secondCharge) / (4 * distanceSquared * pi * absoluteDielctricCostant)

            coulombForceX = coulombForce * cos(angleRadians)
            coulombForceY = coulombForce * sin(angleRadians)

            forces[f"{firstElectron['id']}-{secondElectron['id']}"] = {"x": xDistance, "y": yDistance, f"x-{firstElectron['id']}": firstElectron["x"] > secondElectron["x"], f"y-{firstElectron['id']}": firstElectron["y"] > secondElectron["y"], f"x-{secondElectron['id']}": secondElectron["x"] > firstElectron["x"], f"y-{secondElectron['id']}": secondElectron["y"] > firstElectron["y"], "repel": (firstCharge * secondCharge) > 0, "force-x": coulombForceX, "force-y": coulombForceY, "angle": angleRadians, "check": forcesChecks}

    for charge in circumferenceCharges:

        for electron in electrons:

            try:

                forces.pop(f"c-{charge['id']}-{electron['id']}")

            except:

                pass

            circumferenceCharge = charge["charge"]
            electronCharge = electron["charge"]

            xDistance = abs(electron["x"] - charge["x"])
            yDistance = abs(electron["y"] - charge["y"])

            distanceSquared = xDistance ** 2 + yDistance ** 2

            try: 

                angleRadians = arctan(yDistance / xDistance)

            except:

                angleRadians = pi / 2

            try:

                coulombForce = abs(circumferenceCharge * electronCharge) / (4 * distanceSquared * pi * absoluteDielctricCostant)

            except:

                coulombForce = 0    

            coulombForceX = coulombForce * cos(angleRadians)
            coulombForceY = coulombForce * sin(angleRadians)

            forces[f"c-{charge['id']}-{electron['id']}"] = {"x": xDistance, "y": yDistance, f"x-{electron['id']}": electron["x"] > charge["x"], f"y-{electron['id']}": electron["y"] > charge["y"], "repel": (electronCharge * circumferenceCharge) > 0, "force-x": coulombForceX, "force-y": coulombForceY, "angle": angleRadians, "check": forcesChecks}

    for index, electron in enumerate(electrons):

        electronMod = electron
        resultantX = 0
        resultantY = 0

        for force in forces:

            if force.endswith(f"-{electron['id']}") or force.startswith(f"{electron['id']}-"):

                if forces[force][f"x-{electron['id']}"]:

                    xForce = forces[force]["force-x"]

                else:

                    xForce = (forces[force]["force-x"]) * (-1)

                if forces[force][f"y-{electron['id']}"]:

                    yForce = (forces[force]["force-y"]) * (-1)

                else:

                    yForce = (forces[force]["force-y"])

                electronMod["x-force"][force] = xForce
                electronMod["y-force"][force] = yForce

                resultantX += xForce
                resultantY += yForce

        resultant = sqrt((resultantX ** 2) + (resultantY ** 2))
        acceleration = resultant / electronMod["mass"]

        angleRadians = arctan(abs(resultantY) / abs(resultantX))

        if resultantX > 0 and resultantY < 0 :

            angleRadians = (pi * 2) - angleRadians

        elif resultantX < 0 and resultantY > 0:

            angleRadians = pi - angleRadians

        elif resultantX < 0 and resultantY < 0:

            angleRadians = pi + angleRadians

        electronMod["angleAcceleration"] = angleRadians
        electronMod["acceleration"] = acceleration

        electrons[index] = electronMod

def createElectrons(rows):

    global idElectrons
    
    idElectrons += 1

    while True:

        minIntevral = int(rows) - int(rows / 10)
        maxInterval = int(rows) + int(rows / 10)

        x = randint(minIntevral, maxInterval)
        y = int(randint(minIntevral, maxInterval) / 2)

        if particles[y][x] == "X":

            break

    electron = {"charge": -1.6022*(10**-9), "x": x, "y": y * 2, "id": idElectrons, "x-force": {}, "y-force": {}, "acceleration": 0, "mass": 9.01938*(10**-31), "angleAcceleration": 0, "speed": 0, "angleSpeed": 0}

    particles[y][x] = f"e-{idElectrons}"

    electrons.append(electron)

def createRows(rows):

    global rowsNumber

    rows = int(rows)

    if rows % 2 != 1:

        rows -= 1

    rowsNumber = rows

    for integer in range(1, rows):

        index = integer
        integer = (rows / 2) - integer

        if integer < 0:

            integer = integer * (-1)

        integer = (rows / 2) - integer

        row = []

        for _ in range(0, int(((rowsNumber * 2 - (int(integer) * 4))) / 2)):

            row.append(" ")

        for _ in range(0, int(integer) * 4):

            row.append("X")

        for _ in range(0, int(((rowsNumber * 2 - (int(integer) * 4))) / 2)):

            row.append(" ")

        particles[index] = row

def displayParticlesPosition():

    for row in particles:

        print(f"{''.join(particles[row])}")

def mainLoop():

    createRows(rowsNumber)

    for _ in range(0,4):

        createElectrons(rowsNumber)

    chargeCircumference()

    displayParticlesPosition()

    timePassed = 0

    while True:

        time.sleep(.05)

        timePassed += 8*10 ** -12

        checkForces()
        checkMovement(8*10 ** -12)

        displayParticlesPosition()

        print(f"{timePassed} seconds have passed")

mainLoop()