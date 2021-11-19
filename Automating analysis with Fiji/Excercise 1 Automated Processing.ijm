// MaxIP with bg subtract

// Author: 	Luke Hammond
// Cellular Imaging | Zuckerman Institute, Columbia University
// Date:	November 3, 2021

// Preprocesses tif z-stacks and creates max ip images with background subtraction

// Initialization
requires("1.53c");
run("Options...", "iterations=3 count=1 black edm=Overwrite");
run("Colors...", "foreground=white background=black selection=yellow");
run("Clear Results"); 
run("Close All");

// Parameters
#@ File(label="Raw data:", value = "C:/", style="directory") input
#@ Integer(label="Background Subtraction (rolling ball radius in px, 0 if none):", value = 5, style="spinner") BGSub


setBatchMode(true);

start = getTime();
//process folder
input = input +"/";
files = getFileList(input);	
files = ImageFilesOnlyArray( files );

//make output directory
File.mkdir(input + "MaxIP");
output = input + "MaxIP/"

//process files

for(i=0; i<files.length; i++) {	

	// open image
	open(input + files[i]);
	
	//bg subtract
	run("Subtract Background...", "rolling="+BGSub+" stack");
	
	// create max ip
	run("Z Project...", "projection=[Max Intensity]");
	// save image
	
	save(output + "MaxIP_"+files[i]);

	close("*");
	
}
end = getTime();
time = end-start
print(time)


function ImageFilesOnlyArray (arr) {
	//pass array from getFileList through this e.g. NEWARRAY = ImageFilesOnlyArray(NEWARRAY);
	setOption("ExpandableArrays", true);
	f=0;
	files = newArray;
	for (i = 0; i < arr.length; i++) {
		if(endsWith(arr[i], ".tif") || endsWith(arr[i], ".nd2") || endsWith(arr[i], ".LSM") || endsWith(arr[i], ".czi") || endsWith(arr[i], ".jpg") ) {   //if it's a tiff image add it to the new array
			files[f] = arr[i];
			f = f+1;
		}
	}
	arr = files;
	arr = Array.sort(arr);
	return arr;
}

