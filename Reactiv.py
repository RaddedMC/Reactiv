# RaddedMC's Project Reactiv -- grabs a colour from a video capture device and cleanly 'reacts' to it with the change of a single colour

# User adjustable variables
cameraNumber = 1
shrinkFactor = 10
outputFile = "frame.jpg"
fadeIntervals = 10

import multiprocessing
from termcolor import cprint

# Important non-adjustable variables
lastColour = None
cap = None

# --- Core funcs --- #2

# Runs in the background and grabs data
def BGProcess(frame, lastColour, fadeIntervals, send_end):
    from termcolor import cprint
    cprint("Importing colorgram...", "blue")
    import colorgram
    cprint("Importing capture software...", "blue")
    import cv2
    cprint("Importing system libraries...", "blue")
    import os, copy

    # Uses Colorgram to get a colour from a frame
    def GetColourFromImage(image):
        cv2.imwrite(outputFile, image)
        color = colorgram.extract(outputFile, 1)[0].rgb
        os.remove(outputFile)
        return color

    # Generates a colour in between colour1 and colour2
    # Inspiration from https://graphicdesign.stackexchange.com/questions/83866/generating-a-series-of-colors-between-two-colors/83869
    def InterpolateColour(colour1, colour2, factor):
        if type(colour1) != list:
            tempVar = []
            tempVar.append(colour1[0])
            tempVar.append(colour1[1])
            tempVar.append(colour1[2])
            colour1 = tempVar
        if type(colour2) != list:
            tempVar = []
            tempVar.append(colour2[0])
            tempVar.append(colour2[1])
            tempVar.append(colour2[2])
            colour2 = tempVar
        result = copy.copy(colour1)
        for i, value in enumerate(colour1):
            result[i] = round(colour1[i] + factor * (colour2[i] - colour1[i]))
        return result

    # Get next colour
    cprint("Getting colour...", "blue")
    nextColour = GetColourFromImage(frame)
    cprint("The next colour is " + str(nextColour) + "!", "blue")

    # Get fade range if this isn't the first colour generated
    colours = []
    for i in range(fadeIntervals):
        if (lastColour != None):
            colours.append(InterpolateColour(lastColour, nextColour, i/fadeIntervals))
        else:
            colours.append(nextColour)
    send_end.send((colours, nextColour))

# Runs in the foreground and set the colour of the light strip
def FGProcess(colours):
    import os
    from termcolor import cprint
    cprint("Importing system libraries...", "green")

    # Modifiable! Sends a colour to the recipient device
    def SendColour(colour):
        cprint("Sending Colour " + str(colour), "green")
        os.system('./../home/dietpi/Mipow-Playbulb-BTL201/mipow.exp "PLAYBULB comet" --color 0 '+ str(colour[0]) + ' '+ str(colour[1]) + ' ' + str(colour[2]))
        import time
        cprint(os.getpid(), "green")

    for colour in colours:
        SendColour(colour)

fgProcess = None
# Main loop
def Loop():

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

    while True:
        print("\nMain is grabbing frame from camera...")
        frame = GrabFrame()
        print("\nStarting background process...")
        recv_end, send_end = multiprocessing.Pipe(False)
        global lastColour
        bgProcess = Process(target = BGProcess, args=(frame, lastColour, fadeIntervals, send_end))
        bgProcess.start()

        print("~~Main is waiting for background process to finish~~")
        bgProcess.join()
        print("~~BGProcess finished! Starting FG...~~")
        nextFadeRange, lastColour = recv_end.recv()

        global fgProcess
        if fgProcess != None:
            printed = False
            while fgProcess.is_alive():
                if not printed:
                    print("~~FG is still running...~~")
                    printed = True
            print("~~FG is finished!~~")
        else:
            cprint("First run!", "red")

        print("\nStarting foreground process...")
        fgProcess = Process(target = FGProcess, args=(nextFadeRange,))
        fgProcess.start()
        print("Looping!!")


# Start
def Start():
    try:
        print("Opening camera...")
        global cap
        cap = cv2.VideoCapture(cameraNumber)

        Loop()

    except KeyboardInterrupt:
        print("Exiting!...")

if __name__ == "__main__":
    print("Starting Reactiv...")
    print("Importing multiprocessing...")
    from multiprocessing import Process
    print("Importing capture software...")
    import cv2
    Start()

# Background Process:
#   Grab Frame
#   Get NextColour
#   Generate Fade Range and set to next FadeRange
#   Set NextColour to LastColour

# Foreground Process:
#   Set next FadeRange to active FadeRange
#   Empty next FadeRange

# Control:
#   Start A process and wait for output
#   When A process is done, check if B process is also done
#   If so,
#       Start B Process
#   If not,
#       Wait, then start B process