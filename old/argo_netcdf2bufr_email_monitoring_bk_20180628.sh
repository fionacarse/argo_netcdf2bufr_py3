# This script is intended to run at 09:00 daily 
# It will send an email to a list of addresses reporting on total files processed per day.
# It reads in text from file hourly_report_argo_netcdf2bufr.txt and empties this file at the end of the day
# It also appends numbers to a csv file to keep a longer term record of files handled (will be easy to plot).

emailToList="fiona.carse@metoffice.gov.uk jon.turton@metoffice.gov.uk argo@bodc.ac.uk"
filenameH="hourly_report_argo_netcdf2bufr.txt"
filenameHO="hourly_report_argo_netcdf2bufr_old.txt"
filenameD="daily_report_argo_netcdf2bufr.csv"

# 0. Start daily email report run
dtnow=$(date +%Y%m%d_%H:%M)
echo --
echo --
echo -- Starting daily monitoring run for Argo netCDF2BUFR data, commencing ${dtnow}
echo --
echo --

# 1. change into script directory, to enable access to the text file 
cd $HOME/bin/argo/netcdf2bufr/

# 2. Get info from hourly file and send email
todayHM=$(date +%d/%m/%Y_%H:%M)
totalNC=$(awk '{ sum += $1 } END { print sum }' ${filenameH}) 
totalBUFR=$(awk '{ sum += $7 } END { print sum }' ${filenameH})
emailbodytextH="${totalNC} netCDF files processed into ${totalBUFR} BUFR messages in the 24 hours up to ${todayHM}."
echo "${emailbodytextH}" | mail -s "report from Argo netCDF-to-BUFR processing on exvmarproc01" ${emailToList} 

# 3. remove hourly file and start a new, empty file
cp ${filenameH} ${filenameHO}
rm ${filenameH}
touch ${filenameH} 

# 4. append key numbers and date to daily file 
csvFileText="${totalNC},${totalBUFR},${todayHM}"
echo ${csvFileText} >> ${filenameD} 

# 5. change back to original directory
cd -

# 5. End daily monitoring run
dtnow=$(date +%Y%m%d_%H:%M)
echo --
echo --
echo -- Ending daily monitoring run for Argo netCDF to BUFR data, finished running at ${dtnow}
echo --
echo --
echo 
echo 

exit 0
