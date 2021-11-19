// Mitochondria Distance Measurement Example


// Author : Luke Hammond
// Cellular Imaging | Zuckerman Institute, Columbia University
// Date:	November 3, 2021

// Example script to detect mitochondria in images captured with 40x 1.15 NA water objective on W1 SDC

// Initalization

requires("1.53c");
run("Options...", "iterations=3 count=1 black edm=Overwrite");
run("Colors...", "foreground=white background=black selection=yellow");
run("Clear Results");
close("Log");
run("Close All");

// Parameters

#@ File(label="Input data:", value = "C:/", style= "directory") input
#@ Integer(label="Background subtraction", value = 15, style = "spinner") BGSub

input = input + "/"
files = getFileList(input);	
files = ImageFilesOnlyArray( files );

File.mkdir(input + "Output");
output = input +"Output/"


setBatchMode(true);


start = getTime();

// loop over files

for(i=0; i<files.length; i++) {	
	print("Processing image " + i+1 + " of " + files.length);
	//print("\\Update0: Processing image " + i+1 + " of " + files.length);
	
	// open image
	run("Bio-Formats Importer", "open=[" + input + files[i] + "] autoscale color_mode=Default view=Hyperstack stack_order=XYCZT series_1");
	filename = clean_title(files[i]);
	
	rename("Input");
	run("Split Channels");

	selectWindow("C3-Input");

	//Nucleus
	
	run("Duplicate...", "title=NucMask");
	run("Median...", "radius=20");
	setAutoThreshold("Otsu dark");
	run("Convert to Mask");

	run("Duplicate...", "title=Distance");
	run("Invert");
	run("Distance Map");
	run("16-bit");


	// Mitochondria
	selectWindow("C1-Input");
	run("Duplicate...", "title=MitoMask");
	run("Subtract Background...", "rolling="+BGSub+" stack");
	run("Unsharp Mask...", "radius=2 mask=0.7");
	setAutoThreshold("Otsu dark");
	run("Convert to Mask");
	run("Set Measurements...", "area min redirect=Distance decimal=3");

	run("Analyze Particles...", "size=1-Infinity show=Nothing display exclude clear");
	run("16-bit");
	
	saveAs("Results", output +filename+"_Distances.csv");

	// Cells

	selectWindow("C1-Input");
	run("Duplicate...", "title=CellMask");
	run("Gaussian Blur...", "sigma=15");
	setAutoThreshold("Li dark");
	run("Convert to Mask");
	run("Set Measurements...", "area mean min integrated redirect=None decimal=3");
	run("Analyze Particles...", "size=50.00-Infinity show=[Count Masks] in_situ");
	run("glasbey_on_dark");
	run("16-bit");
		

	run("Merge Channels...", "c2=C1-Input c4=Distance c4=NucMask c5=CellMask c6=MitoMask create");
		
	// save image
	
	save(output + filename +"_Objects.tif");
	
	close("*");
	
}

end = getTime();

time = end-start

print("Total time = " + time);



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

function clean_title(imagename){
	nl=lengthOf(imagename);
	nl2=nl-3;
	Sub_Title=substring(imagename,0,nl2);
	Sub_Title = replace(Sub_Title, "(", "_");
	Sub_Title = replace(Sub_Title, ")", "_");
	Sub_Title = replace(Sub_Title, "-", "_");
	Sub_Title = replace(Sub_Title, "+", "_");
	Sub_Title = replace(Sub_Title, " ", "_");
	Sub_Title = replace(Sub_Title, ".", "_");
	Sub_Title=Sub_Title;
	return Sub_Title;
}





