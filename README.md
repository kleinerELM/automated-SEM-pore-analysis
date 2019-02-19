# Automated Pore Analysis for SEM images of CSH-phases

## Requirements
[Fiji](https://fiji.sc/) (tested with ImageJ 1.52i)

[Python](https://www.python.org/) (tested with Python 3.7.2)

[GNUPlot](https://www.python.org/) (tested with gnuplot 5.2 patchlevel 6a)

## Usage
Put all images of one specimen in one folder. If the images were aquired using a SEM by Thermofischer Scientific or FEI, the scale will be read out automatically.

run the script using the following parameters:
```
start_process.py [-h] [-i] [-g] [-s] [-c] [-p] [-o <outputType>] [-t <thresholdLimit>] [-d]
-h,                  : show this help
-i, --noImageJ       : skip ImageJ processing
-g, --noGnuPlot      : skip GnuPlot processing
-s, --printSumPlot   : printing sums in GnuPlot
-o, --setOutputType  : set output type (0: area%, 1: nm², 2: particle count)
                       Not changeable while using -p! Will be set to 2 automatically.
-c                   : do not clean the image using erode/dilate
-p, --calcPoreDia    : calculate using mean pore diameter instead of pore area
                       Resets parameter -o to 2 (particle count).
-t                   : set threshold limit (0-255)
-d                   : show debug output
```

## Results
The script creates a results.csv and a PDF with a graph of all images

## TODO

[] description of folder based scale recognition