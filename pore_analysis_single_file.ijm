// Macro for ImageJ 1.52d for Windows
// written by Florian Kleiner 2019
// run from command line as follows
// ImageJ-win64.exe -macro "C:\path\to\REMPorenanalyse.ijm" "D:\path\to\data\|thresholdLimit|infoBarheight|metricScale|pixelScale|doSpeckleCleaning"

macro "REMPorenanalyse" {
	// check if an external argument is given or define the options
	arg = getArgument();
	doSpeckleCleaning = true;
	if ( arg == "" ) {
		filePath = File.openDialog("Choose a file");
		//define number of slices for uniformity analysis
		thresholdLimit	= 140; // max threshold value to detect Pores
		infoBarHeight	= 63; // height of the info bar at the bottom of SEM images
		metricScale		= 0; // size for the scale bar in nm
		pixelScale		= 0; // size for the scale bar in px
		doRemoveBorderPercent = 0;
	} else {
		print("arguments found");
		arg_split = split(getArgument(),"|");
		filePath		= arg_split[0];
		thresholdLimit	= parseInt(arg_split[1]);
		infoBarHeight	= parseInt(arg_split[2]);
		metricScale		= parseFloat(arg_split[3]);
		pixelScale		= parseInt(arg_split[4]);
		if ( parseInt(arg_split[5]) == 0 ) {
			doSpeckleCleaning = false;
		}
		doRemoveBorderPercent	= parseInt(arg_split[6]);
	}
	dir = File.getParent(filePath);
	print("Starting process using the following arguments...");
	print("  File: " + filePath);
	print("  Directory: " + dir);
	print("  Pore brightness limit: " + thresholdLimit);
	print("  argument based image-scale: " + pixelScale + " px / " + metricScale + " nm");
	if ( metricScale == 0 || pixelScale == 0 ) {
		do_scaling = false;
		print("  No image-scaling set! Calculation only pixel values!");
	} else {
		do_scaling = true;
		scaleX = metricScale/pixelScale;
		print( "  Set scale 1 px = " + scaleX + " nm" );
	}
	print("  Info bar height: " + infoBarHeight + " px");
	print("------------");
	
	//directory handling
	outputDir_Cut = dir + "/cut/";
	outputDir_Pores = dir + "/pores/";
	outputDir_Processed = dir + "/processed/";
	File.makeDirectory(outputDir_Cut);
	File.makeDirectory(outputDir_Pores);
	File.makeDirectory(outputDir_Processed);
	//list = getFileList(dir);
	
	// running main loop
	//setBatchMode(true);
	
	if (!endsWith(filePath,"/") && ( endsWith(filePath,".tif") || endsWith(filePath,".jpg") || endsWith(filePath,".JPG") ) ) {
		open(filePath);
		imageId = getImageID();		// get image id to be able to close the main image
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
			if ( do_scaling ) {
				run("Set Scale...", "distance=" + pixelScale + " known=" + metricScale + " pixel=1 unit=nm"); //set 
			}

			//////////////////////
			// processing
			//////////////////////
			if ( doRemoveBorderPercent > 0 ) {
				removeBorderWidth = floor(width/100*doRemoveBorderPercent);
				removeBorderHeight = floor((height-infoBarHeight)/100*doRemoveBorderPercent);
			} else {
				removeBorderWidth = 0;
				removeBorderHeight = 0;
			}
			//makeRectangle(	removeBorderWidth, removeBorderHeight,
			//				(width-2*removeBorderWidth), (height-infoBarHeight-2*removeBorderHeight)); // remove info bar
			makeRectangle(	0,removeBorderHeight,
							(width-removeBorderWidth), (height-infoBarHeight-removeBorderHeight)); // remove info bar
			run("Crop");
			run("8-bit"); // convert to 8-bit-grayscale
			saveAs("Tiff", outputDir_Cut + cutName );
			// image enhancements
			run("Subtract Background...", "rolling=100 light sliding"); // removing shadowing using a rather large ball
			run("Gaussian Blur...", "sigma=2.5");//run("Smooth"); // remove some noise
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
				//makeRectangle(	1, 1, 
				//				width-2*removeBorderWidth-2, height-infoBarHeight-2*removeBorderHeight-2); // remove info bar
				makeRectangle(	1, 1, 
								width-removeBorderWidth-2, height-infoBarHeight-removeBorderHeight-2); // remove info bar
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
				print( "  analysing pores ..." );
				run("Analyze Particles...", "  show=Overlay display clear");
				selectWindow("Results");
				// saving masked pores file
				saveAs("Text", outputDir_Pores + baseName + "_pores_sqnm.csv");
								run("Clear Results");
				//selectWindow("C3S 28d cryoBIB_004-masked.tif");
				//run("Line Length Counter");
				//selectWindow("Results");
				//saveAs("Text", outputDir_Pores + baseName + "_pores_hor_lines.csv");
				//Table.deleteRows(0, 1);
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

	// exit script
	print("Done!");
	if ( arg != "" ) {
		run("Quit");
	}
}
