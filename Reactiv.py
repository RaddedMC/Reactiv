# RaddedMC's Reactiv
print("Importing...")
import cv2, colorgram, os
cap = cv2.VideoCapture(0)
print("Capture device opened!")
while True:
    print("Reading frame...")
    frame = cap.read()[1]
    frame = cv2.resize(frame, (64, 48))
    print("Writing frame...")
    cv2.imwrite("frame.jpg", frame)
    print("Extracting color from frame...")
    colorg = colorgram.extract("frame.jpg", 1)
    color = [colorg[0].rgb.r, colorg[0].rgb.g, colorg[0].rgb.b]
    print("Average color"+str(color))

    os.system('./../home/dietpi/Mipow-Playbulb-BTL201/mipow.exp "PLAYBULB comet" --color 0 '+ str(color[0]) + ' '+ str(color[1]) + ' ' + str(color[2]))
    print("Color sent!")