# RaddedMC's Project Reactiv -- grabs a colour from a video capture device and cleanly 'reacts' to it with the change of a single colour

# User adjustable variables
cameraNumber = 1
shrinkFactor = 1
outputFile = "frame.jpg"

# Important non-adjustable variables
lastColour = None
lastTime = 0

# --- Core funcs --- #

# Grabs a frame from the chosen capture device
def GrabFrame():
    global shrinkFactor
    if shrinkFactor < 1:
        shrinkFactor = 1

    print("Reading frame...")
    frame = cap.read()[1]
    captureSize = frame.shape
    newSize = (round(captureSize[1]/shrinkFactor), round(captureSize[0]/shrinkFactor))
    print("Resizing to " + str(newSize[0]) + " x " + str(newSize[1]))
    frame = cv2.resize(frame, newSize)
    return frame

# Uses Colorgram to get a colour from a frame
def GetColourFromImage(image):
    cv2.imwrite(outputFile, image)
    color = colorgram.extract(outputFile, 1)[0].rgb
    os.remove(outputFile)
    return color

# Generates a colour in between colour1 and colour2
# Inspiration from https://graphicdesign.stackexchange.com/questions/83866/generating-a-series-of-colors-between-two-colors/83869
def InterpolateColour(colour1, colour2, factor):
    result = [False, False, False]
    for i, value in enumerate(colour1):
        result[i] = round(colour1[i] + factor * (colour2[i] - colour1[i]))
    return result

# Modifiable! Sends a colour to the recipient device
def SendColour(colour):
    print("Sending Colour " + str(colour))
    #os.system('./../home/dietpi/Mipow-Playbulb-BTL201/mipow.exp "PLAYBULB comet" --color 0 '+ str(color[0]) + ' '+ str(color[1]) + ' ' + str(color[2]))


# Main loop
def Loop():
    # Get frame & next colour
    print("Grabbing frame...")
    frame = GrabFrame()
    print("Getting colour...")
    nextColour = GetColourFromImage(frame)
    print("The next colour is " + str(nextColour) + "!")

    # Get fade range if this isn't the first colour generated
    global lastColour
    global lastTime
    if lastColour != None:
        colours = []
        for i in range(10):
            colours.append(InterpolateColour(lastColour, nextColour, i/10))

        # Display fade range
        for colour in colours:
            SendColour(colour)

    # If this is the first run:
    else:
        SendColour(nextColour)

    lastColour = copy.copy(nextColour)

    print("\n\n")

# Start
try:
    print("Starting...")
    
    print("Importing system libraries...")
    import os, copy, time
    print("Importing colorgram...")
    import colorgram
    print("Importing capture software...")
    import cv2

    print("Opening camera...")
    cap = cv2.VideoCapture(cameraNumber)

    while(True):
        Loop()

except KeyboardInterrupt:
    print("Exiting!...")