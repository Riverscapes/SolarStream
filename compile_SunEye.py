# file name:	compile_SunEye.py
# description:	This tool calculates total net solar insolation values for each CHaMP site
#               within a CHaMP watershed, then compiles those values into a single csv table.
#				The user supplies a directory with csv files that have been downloaded
#				from the CHaMP Monitoring website (http://www.champmonitoring.org).
#				On champmonitoring.org these files are named SkyXXDailySolarAccess.csv and
#				SkyXXInsolation.csv. Each CHaMP site has 11 Skyview samples, totaling 22 csv
#               files per CHaMP site. The tool iterates through each CHaMP site folder in the
#               input directory, calculating the total solar insolation for July 1st through
#               Aug. 31st for each CHaMP site.
# author:		Jesse Langdon
# dependencies: os module, CSV module
# version:		0.2

import os, csv

# CONSTANTS
SKY_SUFFIXES = ['DailySolarAccess.csv', 'Insolation.csv']


# FUNCTIONS
# def list_sites(in_dir):
#     """Compiles list of CHaMP sites based on subdirectories in
#     the directory indicated by the user.
#
#     :param in_dir: directory storing all CHaMP site folders
#     :return list_sites: list of CHaMP sites
#     """
#     list_sites = os.listdir(in_dir)
#     return list_sites


def get_dirs(in_dir):
    """Compiles list of full subdirectory paths for each CHaMP site

    :param in_dir: directory storing all CHaMP site folders
    :return list_dirs: list of CHaMP site subdirectories
    """
    list_dirs = []
    for root, dirs, files in os.walk(in_dir):
        for d in dirs:
            list_dirs.append(os.path.join(root, d))
    return list_dirs


def get_skyview_names(dir_path):
    """Returns list of unique Skyview file name prefixes, i.e. 'Sky01', 'Sky02', etc.

    :param dir_name: single CHaMP site directory path name
    :return list_skyview_names:
    """
    skyview_file_list = os.listdir(dir_path)
    all_prefixes = []
    for f in skyview_file_list:
        prefix = f[:5] # get prefix from Skyview file name
        all_prefixes.append(prefix)
    skyview_prefixes = (sorted(set(all_prefixes)))
    return skyview_prefixes


def compile_sky_filenames(sky_prefixes, sky_suffixes):
    """Compiles 2D list of CHaMP SkyView filenames found in the site subdirectory,
    i.e. [[Sky01DailySolarAccess.csv],[Sky01Insolation.csv]]."""
    #count_sites = len(sky_prefixes)
    list_file_pairs = []
    for s in sky_prefixes:
        file_pair = []
        file_pair.append(str(s).zfill(2) + sky_suffixes[0])
        file_pair.append(str(s).zfill(2) + sky_suffixes[1])
        list_file_pairs.append(file_pair)
    return list_file_pairs


def read_csv(site_dir, file_name):
    """Opens CSV file and adds content to an array

    :param site_dir: CHaMP site subdirectory path
    :param file_name: CSV filename
    :return sol_access_contents: csv file with contents from opened CSV file
    """
    file_contents = []
    csv_name = site_dir + "\\" + file_name
    i = open(csv_name, 'r')
    reader = csv.reader(i)
    for row in reader:
        file_contents.append(row)
    return file_contents


def list_sol_access(sol_access_contents):
    """Build list of daily solar access values for July 1 - Aug 31.

    :param sol_access: list of all contents from opened daily solar access CSV file
    :return: list of solar access values for date range
    """
    list_sol_access = []
    month_columns = [8, 9]
    for col in month_columns:
        for row in sol_access_contents[14:45]:
            list_sol_access.append(float(row[col]))
    return list_sol_access


def sum_gross_sol(insol_contents):
    """Calculate total insolation per day for each Skyview sample.

    :param insol_contents: list of content from opened insolation file
    :return list_gross_sol: list of total insolation values per day, July 1 - Aug 31
    """
    list_gross_sol = []
    for row in insol_contents[199:261]:
        row_dbl = []
        for n in row[1:63]:
            if n == '':
                row_dbl.append(0)
            else:
                row_dbl.append(float(n))
        #row_dbl = [0 if n == '' else float(n) for n in row[1:63]]
        row_sum = sum(row_dbl)
        list_gross_sol.append(row_sum)
    return list_gross_sol


def calc_net_sol(list_gross_sol, list_sol_access):
    """Calculate net insolation per day.

    :param gross_insol:
    :return net_sol_val:
    """
    decimal_sol_access = [a / 100 for a in list_sol_access]
    net_sol_list = [i * j for i, j in zip(list_gross_sol, decimal_sol_access)]
    return net_sol_list


def sum_net_sol_row(net_sol_list):
    """Calculate total of net insolation values for a skyview sample.

    :param net_sol_list: list of net insolation values (for a skyview sample)
    :return total_net_sol: summed net insolation
    """
    total_net_sol_row = sum(net_sol_list)
    return total_net_sol_row

def sum_net_sol_per_sky():

    return


def calc_avg_sol(site_dir, net_sol_val):
    """Calculate average net insolation for a CHaMP site.

    :param dict_net_sol: dictonary of net insolation values per site
    :return list_avg_sol: list with CHaMP site and average net insolation values"""
    site_name = os.path.basename(site_dir)
    list_avg_sol = []
    avg_net_sol = sum(net_sol_val)/len(net_sol_val)
    list_avg_sol.append(site_name)
    list_avg_sol.append(avg_net_sol)
    return list_avg_sol


def write_csv(list_sol, out_csv):
    """Take 2D list of CHaMP site and avg net insolation, and
    write to csv file.

    :param list_sol:
    :param out_csv:
    :return  :
    """
    with open(dir_csv + "\\" + out_csv, "wb") as w:
        column_headers = ["Site_Name", "Avg_Sol"]
        write = csv.writer(w)
        write.writerow(column_headers)
        write.writerows(list_sol)


def main(in_dir, out_csv, sky_suffixes):
    """Main function which performs processing.

    :param in_dir: Directory with CHaMP site subdirectories, each storing CSV files
    :param out_csv: Name of the output CSV file with averaged net solar insolation values
    """
    site_dirs = get_dirs(in_dir)
    insol_per_site = []
    total_net_insol_sky_list = []
    for site in site_dirs:
        sky_prefixes = get_skyview_names(site)
        sky_files = compile_sky_filenames(sky_prefixes, sky_suffixes)
        for skyview in sky_files:
            sol_access_content = read_csv(site, skyview[0])
            insolation_content = read_csv(site, skyview[1])
            sol_access_list = list_sol_access(sol_access_content)
            gross_insol_list = sum_gross_sol(insolation_content)
            net_sol_val = calc_net_sol(gross_insol_list, sol_access_list)
            sum_sol_sky = sum_net_sol_row(net_sol_val)
            total_net_insol_sky_list.append(sum_sol_sky)
        avg_sol_list = calc_avg_sol(site, total_net_insol_sky_list)
        insol_per_site.append(avg_sol_list)
    write_csv(insol_per_site, out_csv)
    return


print ""
print "CHaMP SunEye Data Prep Tool"
print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
print "This tool calculates total net solar insolation for each CHamP site"
print "within a CHaMP study area (i.e. watershed). SunEye Skyview csv files"
print "must be downloaded into a local directory prior to running this tool,"
print "using the following directory structure:"
print ""
print "     - CHaMP Study Area (i.e. Lemhi)"
print "          - CHaMP site name (i.e. CBW05583-XXXXXX)"
print "              - SkyXXDailySolarAccess.csv"
print "              - SkyXXInsolation.csv"
print ""
print "The latest version of the tool can be downloaded from "
print "https://github.com/jesselangdon."
print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"

# user input
while True:
    dir_csv = raw_input("Enter a file path and folder containing the CHaMP site folders: ")
    if os.path.isdir(dir_csv):
        break
    else:
        print "ERROR: That is not a valid file path or folder name. Please try again."
out_csv = raw_input("Enter the name of the output csv file: ")

#TESTING
# dir_csv = r"C:\JL\Testing\solar\SunEye\Lemhi\2015"
# out_csv = "test_201610125.csv"

main(dir_csv, out_csv, SKY_SUFFIXES)

print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
print "Average solar access values compiled. Process complete!"