### Validation with CHaMP SunEye Measurements

#### Validation Data Processing Methodology

* The compile_SunEye.py script is designed specifically to work with CHaMP SunEye solar measurements. It calculates total solar insolation for each CHaMP site within a CHaMP study area (i.e. watershed), as modeled by SunEye software. Specifically, after the user has downloaded the Insolation and Solar Access Values table for each CHaMP site, the tool then iterates
through each CHaMP site folder, and calculate the total solar insolation for the site, per day, per time interval, from July 1st through Aug. 31st.

#### Instructions

* To validate the results of the solar insolation model, solar measurement data can be downloaded from [Columbia Habitat Monitoring Program](https://www.champmonitoring.org/) website. Solar radiation data has been collected by CHaMP field survey crews using SunEye instruments, and this data can be compared modeled solar insolation values.
* SunEye data must be downloaded separately per CHaMP survey site. 
* Navigate to Watershed (Name) > Field Support > Data Check In > click the "File Upload" icon associated with the Site ID > Solar Input Photos.  Download the all of the SkyXXDailySolarAccess.csv and SkyXXInsolation.csv files.  There should be 11 skyview samples, so 22 CSV files per site (although there may be less for some CHaMP sites).
* Once all of the DailySolarAccess and Insolation files have been downloaded for each CHaMP site within the basin of interest, run the compile\_SunEye.py from the command line (i.e. > python compile\_SunEye.py).
* Enter the filepath to the directory containing all of the CHaMP site subdirectories, each containing the downloaded SunEye CSV files.
* Enter the name of the output file.  This will be stored in the same directory as the SunEye files.