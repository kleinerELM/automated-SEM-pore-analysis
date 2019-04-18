/*
* Automated calculation of line lengths using an binarized image
*
* © 2019 Florian Kleiner
*   Bauhaus-Universität Weimar
*   Finger-Institut für Baustoffkunde
*
* programmed using Fiji/ImageJ 1.52k
*
*/

import ij.*;
import ij.process.*;
import ij.gui.*;
import java.awt.*;
//import java.util.List;
//import java.util.ArrayList;
import ij.plugin.filter.*;
import ij.measure.*;

public class Line_Length_Counter implements PlugInFilter {
	ImagePlus imp;

	public int setup(String arg, ImagePlus imp) {
		this.imp = imp;

		IJ.log( "Line Length Counter is running..." );

		return DOES_8G;//DOES_ALL;
	}

	public void run(ImageProcessor ip) {
        Calibration cal = imp.getCalibration();
		int width = ip.getWidth();
		int height = ip.getHeight();
		int size = width*height;
		int position = 0;
		int value = 0;
		int lastValue = 0;
		int lastChangedX = -1;
		int lastChangedY = -1;
		int lineCount = 0;
		int length = 0;
		int voidColor = 255;
		int materialColor = 0;
		
		boolean ignoreBorder = true;
		boolean isBorder = true;
		boolean borderReached = false;
		boolean processHorizontal = true;
		boolean processVertical = false;

		IJ.setColumnHeadings( "Line-Nr.	length [" + cal.getUnit() + "]" );
		int minLenght = 3;

		if (IJ.isMacro() && Macro.getOptions() != null && !Macro.getOptions().trim().isEmpty()) {
			IJ.log( "processing macro arguments:" );
			String [] arguments = Macro.getOptions().trim().split(" ");
			for ( int i = 0; i< arguments.length; i++ ) {
				IJ.log( arguments[i] );
			}
			// TODO!
		} else {
			IJ.log( "asking user for arguments" );
			GenericDialog gd = new GenericDialog("Please check the following parameters");
			gd.addCheckbox("Ignore Border lines", ignoreBorder);
			gd.addCheckbox("Process vertical lines", processVertical);
			gd.addCheckbox("Process horizontal lines", processHorizontal);
			gd.addNumericField("minimal line length [px]", minLenght, 0);

			gd.showDialog();
			if ( gd.wasCanceled() ) return;

			ignoreBorder = gd.getNextBoolean();
			processVertical = gd.getNextBoolean();
			processHorizontal = gd.getNextBoolean();
			minLenght = (int)gd.getNextNumber();
		}


		if ( processHorizontal ) {
			IJ.log( "processing horizontal lines" );

			for ( int y = 0; y<height; y++ ) {
				for ( int x = 0; x<width; x++ ) {
					position++;
					IJ.showProgress(position, size);
					value = ip.getPixel(x,y);
					borderReached = (x == width-1);
					if ( value != lastValue || borderReached ) {
						isBorder = ( lastChangedX < 0 || borderReached );
						if ( value == materialColor || ( isBorder && !ignoreBorder ) ) { // if materialColor appeares a completed void line is detected
							length = x - lastChangedX;
							lastChangedX = x;
							if ( length != width && length > minLenght ) {
								lineCount++;
								//lineArray.add( String.valueOf( cal.pixelWidth * length ) );
								IJ.write( String.valueOf( lineCount ) + "	" + String.valueOf( IJ.d2s( cal.pixelWidth * length, 4) ) );
							}
						}
						if ( borderReached ) lastChangedX = -1;
					}
					lastValue = value;
				}
			}
		}

		if ( processVertical ) {
			IJ.log( "processing vertical lines" );

			lastChangedY = -1;
			for ( int x = 0; x<width; x++ ) {
				for ( int y = 0; y<height; y++ ) {
					position++;
					IJ.showProgress(position, size);
					value = ip.getPixel(x,y);
					borderReached = (y == height-1);
					if ( value != lastValue || borderReached ) {
						//IJ.showMessage( "valuechange at", String.valueOf( x ) + " x " + String.valueOf( y ) );
						isBorder = ( lastChangedX < 0 || borderReached );
						if ( value == materialColor || ( isBorder && !ignoreBorder ) ) { // if materialColor appeares a completed void line is detected
							length = y - lastChangedY;
							lastChangedY = y;
							if ( length != width && length > minLenght ) {
								lineCount++;
								//lineArray.add( String.valueOf( cal.pixelHeight * length ) );
								IJ.write( String.valueOf( lineCount ) + "	" + String.valueOf( IJ.d2s( cal.pixelHeight * length, 4) ) );
							}
						}
						if ( borderReached ) lastChangedY = -1;
					}
					lastValue = value;
				}
			}
		}

		IJ.log( "Done" );
	}
}
