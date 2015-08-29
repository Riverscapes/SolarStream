# file name:	compile_SunEye.py
# description:	This tool compiles monthly solar access percentage values into a single  
#				csv table. The user supplies a directory with csv files that have been 
#				downloaded from the CHaMP Monitoring website (http://www.champmonitoring.org).  
#				On champmonitoring.org these files are named AverageSolarAccess.csv, and 
#				one is available for each site visit.  The tool then iterates through each  
#				csv in the list, and pulls the site name, and the solar access percentage  
#				values for July and August.  These values  are then compiled into a single 
#				csv file.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, CSV module
# version:		0.1

import os, csv

# function compile=ing a list based on opened csv file contents
def csvAsList(dir_csv, file_name):
	file_contents = []
	csv_name = dir_csv + "\\" + file_name
	i = open(csv_name, 'r')
	reader = csv.reader(i)
	for row in reader:
		file_contents.append(row)
	return file_contents

print ""
print "CHaMP SunEye Data Prep Tool"
print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
print "This tool extracts monthly solar access data from a directory"
print "of CSV files, and compiles that data into a single table. The"
print "solar access files can be downloaded from the CHaMP Monitoring"
print "website (http://champmonitoring.org).  The resulting table will"
print "be exported as a csv file. The latest version of the tool can"
print "be found at https://github.com/jesselangdon."
print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"

# user input
while True:
	dir_csv = raw_input("Enter a file path and folder containing the solar access files: ")
	if os.path.isdir(dir_csv):
		break
	else:
		print "ERROR: That is not a valid file path or folder name. Please try again."
out_csv = raw_input("Enter the name of the new, compiled csv file: ")

file_list = os.listdir(dir_csv)

# create a list that will be column headers in output file
hdr_list = ['SiteName',
       'Jan','Feb','Mar','Apr','May','June','July','Aug','Sep','Oct','Nov','Dec']

# iterate through files in directory, append solar access values to new list
value_list = []
for f in file_list:
	csv_list = csvAsList(dir_csv, f)
	row_list = []
	row_list.append(csv_list[1][1]) #append site name
	for row in csv_list[15:27]:
		row_list.append(row[1]) #append solar access values for 12 months
	value_list.append(row_list)

with open(dir_csv + "\\" + out_csv, "wb") as w:
	write = csv.writer(w)
	write.writerow(hdr_list)
	write.writerows(value_list)
	
print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
print "Average solar access values compiled. Process complete!"