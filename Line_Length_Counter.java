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
		int lineCount = 0;
		int length = 0;
		int voidColor = 255;
		int materialColor = 0;
		//int[] lineArray;
		//List lineArray = new ArrayList();
		boolean ignoreBorder = true;
		boolean isBorder = true;
		boolean borderReached = false;
		IJ.setColumnHeadings( "Line-Nr.	length [" + cal.getUnit() + "]" );
		int minLenght = 3;
		//if ( cal.scaled() ) IJ.showMessage( "Scaled?", "Yes, Scaled!" );
		/*if ( IJ.WaitForUserDialog("Title","text") ) {
			IJ.showMessage( "Lines found:", "ok" ); //lineArray.size() ) );
		} else {
			IJ.showMessage( "Lines found:", "cancel" ); //lineArray.size() ) );
		}*/

		// horizontal lines
		for ( int y = 0; y<height; y++ ) {
			for ( int x = 0; x<width; x++ ) {
				position++;
				IJ.showProgress(position, size);
				value = ip.getPixel(x,y);
				borderReached = (x == width-1);
				if ( value != lastValue || borderReached ) {
					//IJ.showMessage( "valuechange at", String.valueOf( x ) + " x " + String.valueOf( y ) );
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
		// vertical lines
		/*
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
			*/
		//IJ.showMessage( "Lines found:", String.valueOf( cal.pixelWidth) ); //lineArray.size() ) );
	}
}
