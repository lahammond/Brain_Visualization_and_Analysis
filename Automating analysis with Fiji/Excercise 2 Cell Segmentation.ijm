// Segmenting Cells

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
close("Log");

// Parameters
#@ File(label="Raw data:", value = "C:/", style="directory") input
#@ Integer(label="Median:", value = 10, style="spinner") Med
#@ Integer(label="Background Subtraction:", value = 5, style="spinner") BGSub


setBatchMode(true);

start = getTime();
//process folder
input = input +"/";
files = getFileList(input);	
files = ImageFilesOnlyArray( files );

//make output directory
File.mkdir(input + "Output");
output = input + "Output/"

//process files

for(i=0; i<files.length; i++) {	

	print("Processing file "+i+1+" of "+files.length);

	// open image
	open(input + files[i]);

	//rename
	filename =  clean_title(files[i]);
	rename("Image");

	//Split Channel
	run("Split Channels");
	selectWindow("C1-Image");
	
	run("Duplicate...", "title=Mask");
	
	// Filtering
	run("Median...", "radius="+Med);
	
	//bg subtract
	run("Subtract Background...", "rolling="+BGSub+" stack");

	run("8-bit");
	
	run("Auto Local Threshold", "method=Bernsen radius=30 parameter_1=0 parameter_2=0 white");

	run("Set Measurements...", "area mean min integrated redirect=C2-Image decimal=3");
	
	run("Analyze Particles...", "  show=[Count Masks] display exclude clear in_situ");
	
	positive = 0;
	for (f = 0; f < nResults; f++) {
		if (getResult("Mean", f) > 0){
			positive = positive + 1;
		}
	}

	print(nResults+" cells detected.");
	print(positive+" double labeled cells detected.");
	print(positive/nResults*100 +"% double labeled cells.");

	run("glasbey_on_dark");
	
	run("Merge Channels...", "c2=C1-Image c6=Mask create");
	
	
	// save image
	
	saveAs("Results", output + "Cellcounts"+filename+".csv");
	save(output + filename+"merge.tif");

	close("*");
	
}
end = getTime();
time = end-start
print("Processing time = "+time)
selectWindow("Log");
saveAs("txt", input+"/Analysis_Log.txt");


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

