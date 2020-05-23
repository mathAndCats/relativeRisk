# -*- coding: utf-8 -*-


# importing csv module 
import csv
import matplotlib.pyplot as plt
import numpy as np;

fields = [] 
rows = []  
pneumoniaDeaths = []

nameList = list();
colorArray2 = ("gray","blue","limegreen","orange","darkviolet","green","coral","dodgerblue","gold","turquoise");

colorArray1 = ("limegreen","forestgreen","seagreen","Blue","darkblue","cornflowerblue","Red","Coral","Salmon")

###############################################################################
def extractCauseOfDeathData(filename='causeOfDeath25_34.txt'):

    rows = [] 
    with open(filename,'r',encoding="ASCII") as csvfile:
        # creating a csv reader object 
        csvreader = csv.reader(csvfile) 
          
        # extracting field names through first row 
        fields = next(csvreader) 
      
        # extracting each data row one by one 
        for row in csvreader: 
            rows.append(row) 
      
        rows.reverse();
        return rows, fields;


###############################################################################
def extractCovidDeathData():

    with open('Provisional_COVID-19_Death_Counts_by_Sex__Age.txt','r',encoding="ASCII") as csvfile:
        # creating a csv reader object 
        csvreader = csv.reader(csvfile) 
          
        # extracting field names through first row 
        fields = next(csvreader) 
      
        # extracting each data row one by one 
        for row in csvreader: 
            rows.append(row) 
      
        return rows, fields;
    
###############################################################################    
def extractAndProcCovidDeathData():
    rows, fields = extractCovidDeathData();
    sexIndex = fields.index("Sex");
    ageIndex = fields.index("Age group");
    totalDeathsIndex = fields.index("Total Deaths");
    covidDeathsIndex = fields.index("COVID-19 Deaths");
    
    sexList = [a[sexIndex] for a in rows];
    ageList = [a[ageIndex] for a in rows];
    covidDeathsList = [a[covidDeathsIndex] for a in rows];
    
    totalRowIndex = sexList.index("All Sexes Total");
    totalCovidDeaths = np.array(float(covidDeathsList[totalRowIndex]));
    
    allSexesIndex = [ii for ii, x in enumerate(sexList) if x == "All Sexes"];
    agesToPlot = [ ageList[ii] for ii in allSexesIndex];
    covidDeathsToPlot = np.array([ float(covidDeathsList[ii]) for ii in allSexesIndex]);
    
    percentDeaths = covidDeathsToPlot / totalCovidDeaths;
    tooSmallIndexes = np.where(percentDeaths*100 < 0.5);
    numCombined = tooSmallIndexes[0].shape[0];
    
    rePercentDeaths = sum(percentDeaths[tooSmallIndexes]);
    largerDeaths = percentDeaths[numCombined:];
    rePercentDeaths = np.insert(largerDeaths,0,rePercentDeaths)
    
    reAges = agesToPlot[numCombined-1:];
    reAges[0] = "0-25 years";
    return reAges, rePercentDeaths;

###############################################################################
def calcP_Death(pAgeGivenDeath, caseFatalRate, pSick):
    
    pAge = np.array((3.8 + 16 + 41.1 + 43, 45.7, 41.3, 41.6, 42.3, 30.5, 15.4, 6.5))/330;
    
    pDeath = (pAgeGivenDeath*caseFatalRate*pSick)/pAge;
    
    return pDeath;

###############################################################################
def plotCauseOfDeathData(ax, totalDeathArray, dataArray, fields, ageArray, covidArray=np.zeros((8,100))):

    count = 0;
    for data in dataArray:
        plotBar(ax, totalDeathArray[count], data, fields, count, covidArray[:,count]);
        count = count + 1;
    
    ax.set_xticks(range(len(ageArray)))
    ax.set_xticklabels(ageArray);

    
###############################################################################
def plotBar(ax, totalPerHundredThous, rows, fields, count, covidCount):

    totalPerHundredThous = float(totalPerHundredThous);
    numIndex = fields.index("perHundredThousand");   
    nameIndex = fields.index("cause");

    numPerHundredThous = float(rows[0][numIndex]);
    deathSum = 0;
    labelArray = [];
    
    perHundredThousList = list();
    for row in rows:
        perHundredThousList.append(float(row[numIndex]));
        
    percentList = [x / totalPerHundredThous for x in perHundredThousList];

    numDeathsPlotted = 0;
    pIndex = 0;
    rowsToPlotList = list();
    for p in percentList:
        if pIndex >= len(percentList)-4:
            rowsToPlotList.append(rows[pIndex]);
            numDeathsPlotted = numDeathsPlotted + float(rows[pIndex][numIndex]);
        pIndex = pIndex + 1;
    
    numOther = totalPerHundredThous - numDeathsPlotted;
    appendColorArray("Other");
    chosenColor = getColor("Other");
    ax.bar(count, numOther, bottom=0, color=chosenColor) ;
    
    deathSum= numOther;
    pIndex = 0;
    for row in rowsToPlotList:
        numPerHundredThous = float(row[numIndex]);
        appendColorArray(row[nameIndex]);
        chosenColor = getColor(row[nameIndex]);
        ax.bar(count, numPerHundredThous, bottom=deathSum, color=chosenColor) 
        deathSum = deathSum + numPerHundredThous;
        
    if covidCount[4] > 0:
        err=[[100000*(covidCount[4]-min(covidCount))],[100000*(max(covidCount)-covidCount[4])]]
        ax.bar(count, covidCount[4]*100000, bottom=deathSum, color="red", yerr=err);  
     
    plt.show();
    
    
###############################################################################
def appendColorArray(name):
    
    if name not in nameList:
        nameList.append(name);
        
###############################################################################
def getColor(name):
    
    index = nameList.index(name);
    color = colorArray2[index];
    return color;
    


############################################################################### 

# Calculate probability of dying from COVID 
reAges, rePercentDeaths = extractAndProcCovidDeathData();

pAgeGivenDeath = rePercentDeaths;

IFR_Array = (0.006, 0.013, 0.021);
aArray = (0.1, 0.25, 0.5);

pDeath = list();
labelArray = list();
for IFR in IFR_Array:
    for a in aArray:
        d  = 1/(1-a);
        pDeath.append(calcP_Death(pAgeGivenDeath, IFR/d, 0.7))
        labelArray.append(['IFR = ' + str(IFR*100) + '% ; Asymp = ' + str(a*100) + '%']);
        

# linear line plot
fig = plt.figure();
ax = fig.add_subplot(1, 1, 1)
ax.grid(True);
ax.set_ylabel("Probability of Death from COVID-19")
colorCount = 0;
for p in pDeath:
    ax.plot(reAges, p*100, label=labelArray[0],Color=colorArray1[colorCount])
    colorCount = colorCount + 1;
ax.legend(labelArray);

# log line plot
fig = plt.figure();
ax = fig.add_subplot(1, 1, 1)
ax.grid(True);
ax.set_yscale("Log");
colorCount = 0;
for p in pDeath:
    ax.plot(reAges, p*100, label=labelArray[0],Color=colorArray1[colorCount])
    colorCount = colorCount + 1;
ax.legend(labelArray);
ax.set_yticks((.01,.1,1,10));
ax.set_yticklabels(('.01','.1','1','10'));
ax.set_ylabel("Probability of Death from COVID-19 (log scale)")

############################################################################### 

# Plot Cause of Death by age (with and without COVID)
totalDeathData, totalDeathFields = extractCauseOfDeathData(filename='totalDeaths.txt');
totalDeathData = np.array(totalDeathData);
totalDeathArray = totalDeathData[:,totalDeathFields.index('perHundredThous')];
totalDeathArray = totalDeathArray[::-1] ; # reverse array
data1, fields = extractCauseOfDeathData('causeOfDeath25_34.txt');
data2, fields = extractCauseOfDeathData('causeOfDeath35_44.txt');
data3, fields = extractCauseOfDeathData('causeOfDeath45_54.txt');
data4, fields = extractCauseOfDeathData('causeOfDeath55_64.txt');
data5, fields = extractCauseOfDeathData('causeOfDeath65_74.txt');
data6, fields = extractCauseOfDeathData('causeOfDeath75_84.txt');
data7, fields = extractCauseOfDeathData('causeOfDeath85.txt');

dataArray = (data1,data2,data3,data4,data5,data6,data7);

f, (ax1, ax2) = plt.subplots(1, 2, sharey=False)
plotCauseOfDeathData(ax1, totalDeathArray[0:4], dataArray[0:4], fields, reAges[1:5]);
plotCauseOfDeathData(ax2, totalDeathArray[4:7], dataArray[4:7], fields, reAges[5:8]);

custom_lines = list();
index = 0;
for name in nameList:
    custom_lines.append(Line2D([0], [0], color=colorArray2[index], lw=4));
    index = index + 1;

ax1.legend(custom_lines, nameList);

pDeathArray = np.array(pDeath);

f, (ax1, ax2) = plt.subplots(1, 2, sharey=False)
plotCauseOfDeathData(ax1, totalDeathArray[0:4], dataArray[0:4], fields, reAges[1:5], pDeathArray[:,1:5]);
plotCauseOfDeathData(ax2, totalDeathArray[4:7], dataArray[4:7], fields, reAges[5:8], pDeathArray[:,5:8]);

custom_lines.append(Line2D([0], [0], color='Red', lw=4));
nameList.append("COVID-19");
ax1.legend(custom_lines, nameList);
