import numpy as np
import cv2 
import os
import pandas as pd

#%% Folder location

participant = 'S1'
path = './' + participant + r'/Scanner/'
pathSave = './' + participant + r'/Areas/'
pathLetters = './' + participant + r'/Letters/'
pathTexts = './' + participant + r'/Texts/'

#%% 

'''Complete processing for get each area in the image. 

Threshold of 170 and 40 can be changed, they depend of the image features.

Final image are saved in Areas folder'''

def getRegions (setImage, pathSave):
    
    # Binarization for getting numbers and lines
    threshold = 170
    grayImage = cv2.cvtColor(setImage, cv2.COLOR_BGR2GRAY)
    _, binaryImage = cv2.threshold(grayImage, threshold, 255, cv2.THRESH_BINARY)

    # Binarization for getting numbers
    threshold = 40
    _, number = cv2.threshold(grayImage, threshold, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    number = cv2.dilate(~number, kernel, iterations=4)

    # Delete number in the image 
    result = ~binaryImage - (number)

    # Get exteral contour and separate main circle 
    r,c = np.shape(grayImage)
    ext = np.zeros((r,c), np.dtype('uint8'))
    
    # Next line can change depending on cv2 version
    image, contour, _  = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #_, binaryImage = cv2.threshold(grayImage, threshold, 255, cv2.THRESH_BINARY)
    ext = cv2.drawContours(ext, contour, -1, 255, -1)

    # Delete small points in the image
    kernel = np.ones((2, 2), np.uint8)
    extErode= cv2.erode(ext, kernel, iterations=5)
    extDilate = cv2.dilate(extErode, kernel, iterations=5)

    # Find where the circle is and make a cropped region
    points = np.argwhere(extDilate==255) # find where the black pixels are
    points = np.fliplr(points) # store them in x,y coordinates instead of row,col indices
    x, y, w, h = cv2.boundingRect(points) # create a rectangle around those points
    x, y, w, h = x-10, y-10, w+20, h+20 # make the box a little bigger

    # Cropp image
    imaIn = ~result[y:y+h, x:x+w]*ext[y:y+h, x:x+w]

    # Identify secction and put specific lables for each one
    sections, labels = cv2.connectedComponents(imaIn) #imaIn

    # Get each section, make a mask with original image and save it
    for i in range(sections):
        area = np.sum(labels==i)
        if (area > 200 and i != labels[0,0]): # Delete small areas and external area
            section =  labels.copy()
            section[section != i] = 0
            section[section == i] = 255
            newSection = section.astype(np.uint8)
            newImage = cv2.bitwise_and(setImage[y:y+h, x:x+w], setImage[y:y+h, x:x+w], mask=newSection)
            cv2.imwrite( pathSave + '_' + str(area) +'.png', newImage)

    print('Images saved in folder')

#%% 
    
''' 
Section for opening all images in a folder and splitting for electrode and 
directions. Folders for each electrode are created

'''
files = os.listdir(path)

number = 1
circle = 0
direction = ['Right', 'Left', 'Up', 'Down', 'Center']
electrode = 'E' + str(number)

if not os.path.exists(pathSave + electrode):
    os.makedirs(pathSave + electrode)

for file in files:
    print ('Processing: ' + file)
    image = cv2.imread(path + file)
    middle = int(len(image)/2)
    folder = pathSave + '/' + electrode + '/' 
    if (circle < 4):
        getRegions(image[:middle], folder + direction[circle])
        circle += 1
        getRegions(image[middle:], folder + direction[circle])
        circle += 1
    elif (circle == 4):
        getRegions(image[:middle], folder + direction[circle])
        circle = 0
        number += 1
        electrode = 'E' + str(number)
        if not os.path.exists(pathSave + electrode):
            os.makedirs(pathSave + electrode)

print('Completed processing: areas split')

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

print('Completed processing: get letters')

#%%

folders = os.listdir(pathSave)
summaryList = []

for electrode in folders:
    files = os.listdir(pathLetters + electrode)
    columns = ['Electrode', 'Direction', 'Area', 'Label']

    print ('Processing: ' + electrode)
    for file in files:
        commandLine = 'tesseract ' + pathLetters + electrode + '/' + file[:-4] + '.png' + ' ' + pathTexts + file[:-4] + ' -l eng --psm 6'
        os.system(commandLine)
        f = open(pathTexts + file[:-4] + '.txt', "r")
        text = f.read()
        direction = file[:-4].split('_')[0]
        pixels = file[:-4].split('_')[1]
        label = text.replace('\n','')
        summaryList.append([electrode, direction, pixels, label])
        
summary = pd.DataFrame(summaryList, columns=columns)
summary.to_csv( './' + participant + '/' + participant + '_summary.csv' , sep=';')
 
print('Completed processing: Final summary')