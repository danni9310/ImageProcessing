import numpy as np
import cv2 
import os

#%% Folder location

participant = 'S1'
path = './' + participant + r'/Scanner/'
pathSave = './' + participant + r'/Areas/'
pathLetters = './' + participant + r'/Letters/'
pathTexts = './' + participant + r'/Texts/'

#%% In this part is posible to get only letters with background white

folders = os.listdir(pathSave)

for electrode in folders: 
    files = os.listdir(pathSave + electrode)
    print ('Electrode: ' + electrode)

    if not os.path.exists(pathLetters + electrode):
        os.makedirs(pathLetters + electrode)

    for imageName in files:
        print ('Processing: ' + imageName)
        image = cv2.imread(pathSave + electrode + '/' + imageName) 
        threshold = 150
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binaryImage = cv2.threshold(grayImage, threshold, 255, cv2.THRESH_BINARY)
        kernel = np.ones((2, 2), np.uint8)
        splitArea = cv2.dilate(~binaryImage, kernel, iterations=1)

        r,c = np.shape(grayImage)
        ext = np.zeros((r,c), np.dtype('uint8'))

        # Next line can change depending on cv2 version
        image, contour, _  = cv2.findContours(~splitArea, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #_, binaryImage = cv2.threshold(grayImage, threshold, 255, cv2.THRESH_BINARY)
        ext = cv2.drawContours(ext, contour, -1, 255, -1)

        imaIn = (splitArea*ext)
        imaInErode = cv2.erode(imaIn, kernel, iterations=2)
        
        # Save images only with letter
        if np.sum(imaIn) > 700:
            cv2.imwrite( pathLetters + electrode + '/' + imageName[:-4] + '.png', ~(imaInErode*255))

print('Completed processing')