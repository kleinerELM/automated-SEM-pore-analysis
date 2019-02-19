// Macro for ImageJ 1.52d for Windows
// written by Florian Kleiner 2019
// run from commandline as follows
// ImageJ-win64.exe -macro "C:\path\to\REMPorenanalyse.ijm" "D:\path\to\data\|thresholdLimit|infoBarheight|metricScale|pixelScale|doSpeckleCleaning"

macro "REMPorenanalyse" {
	// check if an external argument is given or define the options
	arg = getArgument();
	doSpeckleCleaning = true;
	if ( arg == "" ) {
		dir = getDirectory("Choose a Directory");	
		//define number of slices for uniformity analysis
		thresholdLimit	= 140; // max threshold value to detect Pores
		infoBarHeight	= 63; // height of the infobar at the bottom of SEM images
		metricScale		= 0; // size fo the scale bar in nm
		pixelScale		= 0; // size fo the scale bar in px
	} else {
		arg_split = split(getArgument(),"|");
		dir				= arg_split[0];
		thresholdLimit	= parseInt(arg_split[1]);
		infoBarHeight	= parseInt(arg_split[2]);
		metricScale		= parseInt(arg_split[3]);
		pixelScale		= parseInt(arg_split[4]);
		if ( parseInt(arg_split[5]) == 0 ) {
			doSpeckleCleaning = false;
		}
	}
	print("Starting process using the following arguments...");
	print("Directory: " + dir);
	print("Pore brightness limit: " + thresholdLimit);
	if ( metricScale == 0 || pixelScale == 0 ) {
		do_scaling = false;
		print("No image-scale assumed! Calculation only pixel values!");
	} else {
		do_scaling = true;
		print("Assumed image-scale: " + pixelScale + " px / " + metricScale + " nm");
	}
	print("Info bar height: " + infoBarHeight + " px");
	print("------------");
	
	//directory handling
	outputDir_Cut = dir + "/cut/";
	outputDir_Pores = dir + "/pores/";
	outputDir_Processed = dir + "/processed/";
	File.makeDirectory(outputDir_Cut);
	File.makeDirectory(outputDir_Pores);
	File.makeDirectory(outputDir_Processed);
	list = getFileList(dir);
	
	// running main loop
	setBatchMode(true);
	for (i=0; i<list.length; i++) {
		path = dir+list[i];
		showProgress(i, list.length);
		// select only images
		if (!endsWith(path,"/") && ( endsWith(path,".tif") || endsWith(path,".jpg") || endsWith(path,".JPG") ) ) {
			open(path);
			imageId = getImageID();
			if (nImages>=1) {
				//////////////////////
				// name definitions
				//////////////////////
				filename = getTitle();
				print( filename );
				baseName		= substring(filename, 0, lengthOf(filename)-4);
				cutName			= baseName + "-cut.tif";
				poresName		= baseName + "-masked.tif";
				processedName	= baseName + "-processed.tif";
				
				//////////////////////
				// image constants
				//////////////////////
				width			= getWidth();
				height			= getHeight();
				
				//////////////////////
				// processing
				//////////////////////
				makeRectangle(0, 0, width, height-infoBarHeight); // remove info bar
				run("Crop");
				run("8-bit"); // convert to 8-bit-grayscale
				saveAs("Tiff", outputDir_Cut + cutName );
				// image enhancements
				run("Subtract Background...", "rolling=100 light sliding"); // removing shadowing using a rather large ball
				run("Smooth"); // remove some noise
				run("Enhance Contrast...", "saturated=0.3 normalize");
				run("Subtract Background...", "rolling=30 light sliding"); // removing some left over artifacts
				print( "  saving pores TIF..." );
				saveAs("Tiff", outputDir_Processed + processedName );
				// get pores
				setThreshold(0, thresholdLimit);
				run("Convert to Mask");
				// remove too small masks
				if ( doSpeckleCleaning ) {
					run("Erode");
					run("Dilate");
					makeRectangle(1, 1, width-2, height-infoBarHeight-2); // remove info bar
				}
				// saving processed file
				saveAs("Tiff", outputDir_Pores + poresName );
				print( "  saving pores TIF..." );
				// analyse particle sizes (px scale)
				run("Analyze Particles...", "  show=Overlay display clear");
				selectWindow("Results");
				// saving masked pores file
				saveAs("Text", outputDir_Pores + baseName + "_pores_sqpx.csv");
				Table.deleteRows(0, 1);
				// get scaled values of the particle analysis
				if ( do_scaling ) {
					run("Set Scale...", "distance=" + pixelScale + " known=" + metricScale + " pixel=1 unit=nm"); //set scale
					run("Analyze Particles...", "  show=Overlay display clear");
					selectWindow("Results");
					// saving masked pores file
					saveAs("Text", outputDir_Pores + baseName + "_pores_sqnm.csv");
					Table.deleteRows(0, 1);
				}

				//////////////////////
				// close this file
				//////////////////////
				print( "  closing file ..." );
				selectImage(imageId);
				close();
				print( "" );
			}
		}
	}
	// exit script
	print("Done!");
	if ( arg != "" ) {
		run("Quit");
	}
}