import os
import pandas as pd

#%% Folder location

participant = 'S1'
path = './' + participant + r'/Scanner/'
pathSave = './' + participant + r'/Areas/'
pathLetters = './' + participant + r'/Letters/'
pathTexts = './' + participant + r'/Texts/'

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
print('Completed processing')