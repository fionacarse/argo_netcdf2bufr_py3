# This script is intended to run at 09:00 daily 
# It will send an email to a list of addresses reporting on total files processed per day.
# It reads in text from file hourly_report_argo_netcdf2bufr.txt and empties this file at the end of the day
# It also appends numbers to a csv file to keep a longer term record of files handled (will be easy to plot).
#
# This script was updated on 28 August 2018 to prevent sending to argo@bodc.ac.uk. 
# MO rules say I cannot email directly to (or autoforward to) an external email address.
# Instead, I am trying to set up an FTP of 2 files, which MSS team (DART) will send on to argo@bodc.ac.uk .

#emailToList="fiona.carse@metoffice.gov.uk jon.turton@metoffice.gov.uk argo@bodc.ac.uk"
emailToList="fiona.carse@metoffice.gov.uk jon.turton@metoffice.gov.uk"
filenameH="hourly_report_argo_netcdf2bufr.txt"
filenameHO="hourly_report_argo_netcdf2bufr_old.txt"
filenameD="daily_report_argo_netcdf2bufr.csv"
filenameFLH="hourly_report_netcdf_file_list.txt"
filenameFLHO="hourly_report_netcdf_file_list_old.txt"
filenameDEB="daily_summary_report_for_email_body.txt"

# FTP details
REMOTEHOST=excftpcdn
#REMOTEDIR=XXXX
UN=observation-data
PW=vob1reme

# 0. Start daily email report run
dtnow=$(date +%Y%m%d_%H:%M)
echo --
echo --
echo -- Starting daily monitoring run for Argo netCDF2BUFR data, commencing ${dtnow}
echo --
echo --

# 1. change into script directory, to enable access to the text file 
cd $HOME/bin/argo/netcdf2bufr_py3/

# 2a. COUNTS Get info from hourly file and send email
# 2b. FILES get info from hourly file and add to email.
todayHM=$(date +%d/%m/%Y_%H:%M)
#totalNC=$(awk '{ sum += $1 } END { print sum }' ${filenameH}) 
totalNCR=$(awk '{ sum += $1 } END { print sum }' ${filenameH}) 
totalNCBR=$(awk '{ sum += $6 } END { print sum }' ${filenameH}) 
totalBUFR=$(awk '{ sum += $13 } END { print sum }' ${filenameH})
emailbodytextH="${totalNCR} netCDF R files and ${totalNCBR} nc BR files processed into ${totalBUFR} BUFR messages in the 24 hours up to ${todayHM}."
echo "${emailbodytextH}" | mail -a ${filenameFLH} -s "report from Argo netCDF-to-BUFR py3 processing on exvmarproc01" ${emailToList} 

# 3. FTP list of netCDF files and email body text file to DART
# attachment file will be ${filenameFLH}
# email body file, create filenameDEB from string variable ${emailbodytextH}
# Dave Smith of MSS team said I must sent the email body file first, before the file list.
echo "${emailbodytextH}" > ${filenameDEB}
echo FTPing two daily report files to ${REMOTEHOST} for emailing to argo@bodc.ac.uk
ftpfilelist="${filenameDEB} ${filenameFLH}"
for f in ${ftpfilelist}
do
  bn=$(basename $f)
  ftp -n ${REMOTEHOST} <<END_SCRIPT
  quote USER ${UN}
  quote PASS ${PW}
  put ${f} ${bn}.tmp  
  rename ${bn}.tmp ${bn}
  quit
END_SCRIPT
done



# 4a. COUNTS remove hourly file and start a new, empty file
cp ${filenameH} ${filenameHO}
rm ${filenameH}
touch ${filenameH} 

# 4b. FILE LISTS remove hourly file and start a new, empty file
cp ${filenameFLH} ${filenameFLHO}
rm ${filenameFLH}
touch ${filenameFLH} 

# 5. append key numbers and date to daily file 
csvFileText="${totalNCR},${totalNCBR},${totalBUFR},${todayHM}"
echo ${csvFileText} >> ${filenameD} 

# 6. change back to original directory
cd -

# 7. End daily monitoring run
dtnow=$(date +%Y%m%d_%H:%M)
echo --
echo --
echo -- Ending daily monitoring run for Argo netCDF to BUFR data, finished running at ${dtnow}
echo --
echo --
echo 
echo 

exit 0
