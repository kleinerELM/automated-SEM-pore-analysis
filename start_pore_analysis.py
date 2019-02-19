#########################################################
# Automated Pore Analysis for SEM images for CSH-phases
#
# © 2019 Florian Kleiner
#   Bauhaus-Universität Weimar
#   Finger-Institut für Baustoffkunde
#
# programmed using python 3.7, gnuplot 5.2, Fiji/ImageJ 1.52k
# don't forget to install PIL with pip!
#
#########################################################


import csv
import os, sys, getopt
import subprocess
import math
import tkinter as tk
import mmap
from PIL import Image
from tkinter import filedialog
from subprocess import check_output

print("#########################################################")
print("# Automated Pore Analysis for SEM images for CSH-phases #")
print("#                                                       #")
print("# © 2019 Florian Kleiner                                #")
print("#   Bauhaus-Universität Weimar                          #")
print("#   Finger-Institut für Baustoffkunde                   #")
print("#                                                       #")
print("#########################################################")
print()

#### directory definitions
outputDir_Pores = "/pores/"
#suffix_Pores = "_pores_sqnm.csv"
suffix_Pores = "_pores_sqpx.csv"
home_dir = os.path.dirname(os.path.realpath(__file__))

#### global var definitions
root = tk.Tk()
root.withdraw()
runImageJ_Script = True #False
runGnuPlot_Script = True #False
printGnuPlotSums = False #False
showDebuggingOutput = False
calculatePoreDiameter = False
doSpeckleCleaning = 1
outputType = 0 # standard output type (y-axis value) is area-%
thresholdLimit = 140
infoBarHeight = 63
metricScale = 0
pixelScale  = 0
poreSizeRangeArray = [ 0, 1, 2, 4, 8, 16, 31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000, 31500, 63000, 125000, 250000 ] # in nm or nm², depending on parameter -p!
# prepare result arrays
poreCountSumArray = []
poreSizeSumPercentArray = []
#for val in poreSizeRangeArray:
#    poreSizeSumPercentArray.append( 0 )
#    poreCountSumArray.append( 0 )
#areaSum = 0
resulCSVTable = []
gnuplotBefehl = 'plot '
gnuplotPlotID = 1

def processArguments():
    argv = sys.argv[1:]
    usage = sys.argv[0] + " [-h] [-i] [-g] [-s] [-c] [-p] [-o <outputType>] [-t <thresholdLimit>] [-d]"
    try:
        opts, args = getopt.getopt(argv,"higscpo:t:d",["noImageJ=","noGnuPlot=","printSumPlot=","calcPoreDia="])
    except getopt.GetoptError:
        print( usage )
    for opt, arg in opts:
        if opt == '-h':
            print( 'usage: ' + usage )
            print( '-h,                  : show this help' )
            print( '-i, --noImageJ       : skip ImageJ processing' )
            print( '-g, --noGnuPlot      : skip GnuPlot processing' )
            print( '-s, --printSumPlot   : printing sums in GnuPlot' )
            print( '-o, --setOutputType  : set output type (0: area%, 1: nm², 2: particle count)' )
            print( '                       Not changeable while using -p! Will be set to 2 automatically.' )
            print( '-c                   : do not clean the image using erode/dilate' )
            print( '-p, --calcPoreDia    : calculate using mean pore diameter instead of pore area' )
            print( '                       Resets parameter -o to 2 (particle count).' )
            print( '-t                   : set threshold limit (0-255)' )
            print( '-d                   : show debug output' )
            print( '' )
            sys.exit()
        elif opt in ("-i", "-noImageJ"):
            print( 'deactivating ImageJ processing!' )
            global runImageJ_Script
            runImageJ_Script = False
        elif opt in ("-g", "-noGnuPlot"):
            print( 'deactivating GnuPlot processing!' )
            global runGnuPlot_Script
            runGnuPlot_Script = False
        elif opt in ("-s", "-printSumPlot"):
            print( 'printing sums in GnuPlot' )
            global printGnuPlotSums
            printGnuPlotSums = True
        elif opt in ("-o", "-setOutputType"):
            global outputType
            outputType = int( arg )
        elif opt in ("-c"):
            print( 'disable image cleanup using erode/delate' )
            global doSpeckleCleaning
            doSpeckleCleaning = 0
        elif opt in ("-p", "-calcPoreDia"):
            print( 'calculating pore diameter' )
            global calculatePoreDiameter
            calculatePoreDiameter = True
        elif opt in ("-t"):
            if ( int( arg ) < 256 and int( arg ) > -1 ):
                global thresholdLimit
                thresholdLimit = int( arg )
                print( 'set threshold limit to ' + str( thresholdLimit ) )
        elif opt in ("-d"):
            print( 'show debugging output' )
            global showDebuggingOutput
            showDebuggingOutput = True
    # reset -o / outputType to 2 (particle count)!
    if ( calculatePoreDiameter ):
        outputType = 2
    print( '' )

def analyseImages( directory ):
    command = "ImageJ-win64.exe -macro \"" + home_dir +"\pore_analysis.ijm\" \"" + directory + "/|" + str(thresholdLimit) + "|" + str(infoBarHeight) + "|" + str(metricScale) + "|" + str(pixelScale) + "|" + str(doSpeckleCleaning) + "\""
    print( "starting ImageJ Macro..." )
    if ( showDebuggingOutput ) : print( command )
    try:
        subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print( "Error" )#"returned error (code {}): {}".format(e.returncode, e.output))
        pass

def getPixelSizeFromMetaData( directory, filename ):
    pixelSize = 0
    with open(directory + '/' + filename, 'rb', 0) as file, \
        mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
        if s.find(b'PixelWidth') != -1:
            file.seek(s.find(b'PixelWidth'))
            tempLine = str( file.readline() ).split("=",1)[1]
            pixelSize = float( tempLine.split("\\",1)[0] )*1000000000
            print( " detected image scale: " + str( pixelSize ) + " nm / px" )
    return pixelSize

def getInfoBarHeightFromMetaData( directory, filename ):
    contentHeight = 0
    global infoBarHeight
    with open(directory + '/' + filename, 'rb', 0) as file, \
        mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
        if s.find(b'ResolutionY') != -1:
            file.seek(s.find(b'ResolutionY'))
            tempLine = str( file.readline() ).split("=",1)[1]
            contentHeight = float( tempLine.split("\\",1)[0] )
    if ( contentHeight > 0 ):
        im = Image.open( directory + '/' + filename )
        width, height = im.size
        infoBarHeight = int( height - contentHeight )
        print( " detected info bar height: " + str( infoBarHeight ) + " px" )# + str( height ) + '|' + str(contentHeight))
    else:
        print( " info bar height not detected" )
    return infoBarHeight

def scaleInMetaData( directory ):
    global infoBarHeight
    result = False
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if ( filename.endswith(".jpg") or filename.endswith(".JPG") or filename.endswith(".tif") or filename.endswith(".TIF")):
            if getPixelSizeFromMetaData( directory, filename ) > 0:
                getInfoBarHeightFromMetaData( directory, filename )
                result = True
                break
    return result

def matchSubdirName( subDir ):
    metricScaleArray = [ 400, 500, 2000 ] #nm
    pixelScaleArray = [ 275, 170, 345 ] # px
    global metricScale
    global pixelScale
    result = False
    for i in range(len(metricScaleArray)):
        if subDir == ( str( metricScaleArray[i] ) + "nm" ):
            result = True
            metricScale = metricScaleArray[i]
            pixelScale = pixelScaleArray[i]
        i += 1
    return result

def processData( directory, filename, pixelSize ):
    # pore analysis
    resultLine = ""
    global resulCSVTable
    global outputType
    with open(directory + outputDir_Pores + filename + suffix_Pores, 'r') as csv_file:
        im = Image.open( directory + outputDir_Pores + filename + "-masked.tif")
        width, height = im.size
        im.close()
        imageArea = width * pixelSize * height * pixelSize
        print( " image area: " + str( width * height ) + " px² | " + str( imageArea ) + " nm²" )
        csv_reader = csv.reader(csv_file)
        lineNr = 0
        poreSizeArray = []
        poreSizePercentArray = []
        poreCountArray = []
        for val in poreSizeRangeArray:
            poreSizeArray.append( float( 0 ) )
            poreSizePercentArray.append( float( 0 ) )
            poreCountArray.append( 0 )
        # read every line in csv
        for line in csv_reader:
            if ( lineNr > 0 and line != "" ): # ignore first line (headline) and empty lines
                
                area = float( line[1] ) * pixelSize * pixelSize # get area in nm
                poreSize = math.sqrt( area ) if ( calculatePoreDiameter ) else area
                #search the correct size range and insert into corresponding result array
                for i in range(len(poreSizeRangeArray)):
                    if ( i > 0 ):
                        if ( showDebuggingOutput ) : print(str(i) + '|' + str( poreSizeRangeArray[i-1]) + '|' + str(poreSizeRangeArray[i]))
                        if (len(poreSizeRangeArray)-1 == i and poreSizeRangeArray[i] < poreSize ):
                            if ( showDebuggingOutput ) : print( 'A: ' + str(poreSizeRangeArray[i]) + '<' + str(poreSize))
                            poreSizeArray[i]  += poreSize
                            poreSizePercentArray[i] += area/imageArea*100
                            poreSizeSumPercentArray[i] += area/imageArea*100
                            poreCountArray[i] += 1
                            poreCountSumArray[i] += 1
                        elif ( poreSizeRangeArray[i-1] < poreSize and poreSizeRangeArray[i] > poreSize ):
                            if ( showDebuggingOutput ) : print( 'B: ' + str(poreSizeRangeArray[i-1]) + '<' + str(poreSize) + '<' + str( poreSizeRangeArray[i]) )
                            poreSizeArray[i]  += poreSize
                            poreSizePercentArray[i] += area/imageArea*100
                            poreSizeSumPercentArray[i] += area/imageArea*100
                            poreCountArray[i] += 1
                            poreCountSumArray[i] += 1
            lineNr += 1
        print ( " processed elements: " + str( lineNr ) )
        # process result line
        fullAreaPoresSum = 0
        resulCSVTable[0] += "," + filename
        resulCSVTable[1] += "," + str( round( pixelSize, 3 ) )
        offset = 2 # depends on previous/comment lines in the resultCSVTable
        for i in range(len(poreSizeRangeArray)):
            debugMessage = '  - ' + str( poreSizeRangeArray[i] ) + ' nm: ' + str( poreCountArray[i] ) + 'x (' + str( round( poreSizePercentArray[i], 2 ) ) + ' Area-%, '
            if ( calculatePoreDiameter ):
                debugMessage += 'Ø' + str( round( poreSizeArray[i], 2 ) ) + ' nm)'
            else:
                debugMessage += str( round( poreSizeArray[i], 2 ) ) + ' nm²)'
            print( debugMessage )
            # calculating result table in csv format depending on the requested output type
            if ( outputType == 0 ):
                resulCSVTable[i+offset] += "," + str( round( poreSizePercentArray[i], 2 ) )
                resultLine += "," + str( round( poreSizePercentArray[i], 2 ) )
            elif ( outputType == 1 ):
                resulCSVTable[i+offset] += "," + str( round( poreSizeArray[i], 2 ) )
                resultLine += "," + str( round( poreSizeArray[i], 2 ) )
            elif ( outputType == 2 ):
                resulCSVTable[i+offset] += "," + str( poreCountArray[i] )
                resultLine += "," + str( poreCountArray[i] )
            # calculating summed up area for terminal output
            if calculatePoreDiameter:
                fullAreaPoresSum += poreSizeArray[i] * poreSizeArray[i]
            else:
                fullAreaPoresSum += poreSizeArray[i]
        print( " summed up pore area: " + str( round( fullAreaPoresSum/imageArea*100, 2 ) ) + ' Area-%, ' + str( round( fullAreaPoresSum, 2) ) + ' nm²' )
        
        global gnuplotPlotID
        global gnuplotBefehl
        gnuplotPlotID += 1
        gnuplotBefehl += "'mr_result.csv' using 1:" + str( gnuplotPlotID ) + " title '" + filename.replace('_', '\_') + "' with linespoints, "
    return resultLine

def processImageJResults( directory, forcedScale = None ):
    forcedScale = forcedScale or 1
    if os.path.isdir(directory + outputDir_Pores):
        analysedImages = 0
        csv_file = open(directory + '/results.csv', 'w')
        csv_headline = ""
        seperator = ", "
        for val in poreSizeRangeArray:
            csv_headline += seperator + str(val)
        
        csv_file.write( "name" + csv_headline + "\n" )
        
        global poreCountSumArray
        global poreSizeSumPercentArray
        poreCountSumArray = []
        poreSizeSumPercentArray = []
        for val in poreSizeRangeArray:
            poreSizeSumPercentArray.append( 0 )
            poreCountSumArray.append( 0 )
        
        global resulCSVTable
        resulCSVTable = []
        resulCSVTable.append( "#bucket" )
        resulCSVTable.append( "#scale [nm/px]" )
        for i in range(len(poreSizeRangeArray)):
            resulCSVTable.append( str( poreSizeRangeArray[i] ) )

        for file in os.listdir(directory):
            analysedImages +=1
            filename = os.fsdecode(file)
            if ( filename.endswith(".jpg") or filename.endswith(".JPG") or filename.endswith(".tif") or filename.endswith(".TIF")):
                csv_filename = os.path.splitext(filename)[0]
                if os.path.exists( directory + outputDir_Pores +csv_filename + suffix_Pores ):
                    print("------")
                    print(filename)
                    pixelSize = getPixelSizeFromMetaData( directory, filename )
                    if pixelSize == 0:
                        pixelSize = forcedScale
                        if forcedScale == 1:
                            print( "Skalierung vermutlich fehlerhaft!" )
                    resultLine = processData( directory, csv_filename, pixelSize )
                    csv_file.write( filename + resultLine + "\n" )
                else:
                    print(csv_filename + suffix_Pores + " not found!")
            elif ( showDebuggingOutput ) : 
                print( "------" )
                print(filename + " is no Jpg / Tiff! Skipping!")
        resultLine = ''
        print( "------" )
        print( "Sum for folder " + directory )#+ " (" + str( round( pixelSize, 2 ) ) + " nm / px)" )
        #resulCSVTable[0] += ",bucketSum"
        resulCSVTable[0] += ",fullSum"
        #resulCSVTable[1] += ",-"
        resulCSVTable[1] += ",-"
        sumPercent = 0
        for i in range(len(poreSizeRangeArray)):
            sumAreaPercent = poreSizeSumPercentArray[i]/analysedImages
            sumPercent += sumAreaPercent
            print( '  - ' + str( poreSizeRangeArray[i] ) + ' nm: ' + str( poreCountSumArray[i] ) + 'x (' + str( round( sumAreaPercent, 5) ) + ' Area-%)')
            if ( calculatePoreDiameter ):
                resultLine += "," + str( poreCountSumArray[i] )
                resulCSVTable[i+2] += "," + str( poreCountSumArray[i] )
            else:
                resultLine += "," + str( poreCountSumArray[i] ) + "," + str( round( sumAreaPercent, 5) )
                resulCSVTable[i+2] += "," + str( round( sumAreaPercent, 5) )
                resulCSVTable[i+2] += "," + str( round( sumPercent, 5) )
        csv_file.write( 'Summe' + resultLine + "\n" )
        csv_file.close()
        
        csv_file = open(directory + '/mr_result.csv', 'w')
        for i in range(len(resulCSVTable)):
            csv_file.write( resulCSVTable[i] + "\n" )
        csv_file.close()
        
        if ( printGnuPlotSums ):
            global gnuplotPlotID
            global gnuplotBefehl
            #gnuplotPlotID += 1
            #gnuplotBefehl += "'mr_result.csv' using 1:" + str( gnuplotPlotID ) + " title 'bucketSum' with linespoints, "
            gnuplotPlotID += 1
            gnuplotBefehl += "'mr_result.csv' using 1:" + str( gnuplotPlotID ) + " title 'fullSum' with linespoints linewidth 3"
            
    else:
        print("Folder '" + outputDir_Pores + "' does not exist! Run ImageJ Macro first!")

def createGnuplotPlot( directory, filename ):
    global gnuplotBefehl
    global gnuplotPlotID
    global poreSizeRangeArray
    print( "creating gnuplot plot" )
    if os.path.exists( directory + '/mr_result.csv' ):    
        gp_file = open( directory + '/' + filename + '.gp', 'w')
        gp_file.write( 'set logscale x' + "\n" )
        gp_file.write( 'set datafile separator ","' + "\n" )
        gp_file.write( 'set terminal pdf size 17cm,10cm' + "\n" )
        gp_file.write( 'set output "' + directory + '/' + filename + '.pdf"' + "\n" )
        gp_file.write( 'cd "' + directory + '"' + "\n" )
        
        if calculatePoreDiameter :
            gp_file.write( 'set xlabel "Porendurchmesser in nm"' + "\n" )
        else:
            gp_file.write( 'set xlabel "Porengröße in nm²"' + "\n" )
        
        if ( outputType == 0 ):
            gp_file.write( 'set ylabel "Gesamtfläche in % der Gesamtbildfläche"' + "\n" )
            gp_file.write( 'set key left top' + "\n" )
        elif ( outputType == 1 ):
            gp_file.write( 'set ylabel "Gesamtfläche in nm²"' + "\n" )
            gp_file.write( 'set key left top' + "\n" )
        elif ( outputType == 2 ):
            gp_file.write( 'set ylabel "Partikelanzahl"' + "\n" )
            gp_file.write( 'set key right top' + "\n" )
        
        
        poreSizeRangeStr = ','.join(str(e) for e in poreSizeRangeArray)
        gp_file.write( 'set xtics (' + poreSizeRangeStr + ') rotate by 45 right' + "\n" )
           
        gp_file.write( gnuplotBefehl + "\n" )
        gp_file.close()
        os.system('gnuplot "' + directory + '/' + filename + '.gp"')
        subprocess.Popen( directory + '/' + filename + '.pdf' ,shell=True)
    gnuplotBefehl = 'plot '
    gnuplotPlotID = 1
    print( "done" )

processArguments()
if ( showDebuggingOutput ) : print( "I am living in '" + home_dir + "'" )

if ( outputType == 0 ):
    print( 'Output type is set to area-%' )
elif ( outputType == 1 ):
    print( 'Output type is set to px²' )
elif ( outputType == 2 ):
    print( 'Output type is set to particle count' )
else:
    print( 'Output type is undefined! Resetting to area-%' )
    outputType = 0

workingDirectory = filedialog.askdirectory(title='Please select the image / working directory')
if ( showDebuggingOutput ) : print( "Selected working directory: " + workingDirectory )

#main process
if scaleInMetaData( workingDirectory ) :
    # use metaData in files to determine scale
    print( "Tif with scale metadata found!" )
    if ( runImageJ_Script ):
        analyseImages( workingDirectory )
    processImageJResults( workingDirectory )
    createGnuplotPlot( workingDirectory, 'Plot' )
else:
    # search for formatted folders (eg: 400nm) to determine scale
    for subDir in os.listdir(workingDirectory):
        print( "Formatted folder for scaling found." )
        directory = workingDirectory + "/" + subDir
        if os.path.isdir( directory ) and matchSubdirName( subDir ) :
            folderScale = metricScale/pixelScale #nm/px
            print( "Selected scale:  " + str( metricScale ) + " nm / " + str( pixelScale ) + " px = " + str( folderScale ) + " nm / px" )
            if ( runImageJ_Script ):
                analyseImages( directory )
            processImageJResults( directory, folderScale )
            if ( runGnuPlot_Script ):
                createGnuplotPlot( directory, subDir )
        else:
            print( "------" )
            print("'" + directory + "' is no valid directory!")


print("-------")
print("DONE!")
