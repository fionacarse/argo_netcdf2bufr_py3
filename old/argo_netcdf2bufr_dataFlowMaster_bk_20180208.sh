#!/bin/bash

# The two source lines below make this script work in crontab
# It seems like the .bash_profile is the best option (if use only bashrc, the bitstring module cannot be found.
# Either / or also works, couldn't decide which one was best, so left both in.
#source /home/marinedg/.bash_profile
source /home/marinedg/.bashrc

today=$(date +%Y%m%d)
todayHM=$(date +%Y%m%d_%H%M)
todayH=$(date +%k)
yesterday=$(date +%Y%m%d -d '1 days ago')

# Set file path variables
SCRIPTDIR=/home/marinedg/bin/argo/netcdf2bufr
PYTHONCODEDIR=${SCRIPTDIR}/MetOffice_ArgoToNetCDF_Export_Python2.7/ArgoToNetCDF_Export/Code/ArgoNetCDFToBufr/src
PYTHONCODENAME=argonetcdftobufr.py
WORKINGDATADIR=${SCRIPTDIR}/working/data
DATATOPDIR=/data/local/marinedg/argo/netcdf
NCDEST=$DATATOPDIR/incoming
BUFRDEST=$DATATOPDIR/outgoing/bufr
PROCESSEDNCDIR=${NCDEST}/processed
PROCESSEDBUFRDIR=${BUFRDEST}/processed

# Set file name string variables 
# Contact MSS team (Duncan Jeffery) if naming convention changes!
ascFileString="R*_*[0-9].nc"
dscFileString="R*_*[0-9]D.nc"

# Configure FTP settings for sending BUFR files to MetDB
REMOTEHOSTBUFR=exxmetswitchprod
#REMOTEHOSTBUFR=exxmetswitchdev
UNBUFR=argobufr
PWBUFR=4rg0bufr

# Configure FTP settings for sending netCDF files to external-facing FTP site

# Set up server to send data for web page to

<<'COMMENT'

 1.  Create a variable 'filestohandle' which is list files of netCDF files to process
 2.  Move these files to a working data folder in the script dir
 3.  Process the netCDF files into BUFR, using python script by Dom Jenkins at Dot Software
 4.  Check that netcdf files has a corresponding BUFR file, if not, print file name
 5.  Move the netcdf files to a processed folder
 6.  FTP the BUFR files to MSS team (exxmetswitchprod, or dev)  so MetSwitch can pick them up 
 7.  Move the BUFR files to a processed folder

COMMENT

echo -e "\n === Running "$0" ==="
echo -e " Started at "$(date +"%d/%m/%Y %H:%M:%S")"\n"

cd ${SCRIPTDIR} 

# 1.
# List the files and check there are any available to be processed.
countfilesA=0
for i in ${NCDEST}/${ascFileString} 
do 
  test -f "$i" && 
  echo Ascending profile files exist && 
  filestohandleA=$(ls ${NCDEST}/${ascFileString} 2>/dev/null) &&
  countfilesA=$(ls -l ${NCDEST}/${ascFileString} 2>/dev/null | wc -l) &&
  break
done
countfilesD=0
for i in ${NCDEST}/${dscFileString}
do
  test -f "$i" &&
  echo Descending profile files exist && 
  filestohandleD=$(ls ${NCDEST}/${dscFileString} 2>/dev/null) && 
  countfilesD=$(ls -l ${NCDEST}/${dscFileString} 2>/dev/null | wc -l) &&
  break
done
countfiles=$(( ${countfilesA} + ${countfilesD} ))

# Check whether there are any files to process, exit the script if there are none.
if [[ $countfiles -eq 0 ]] 
then
  echo There are no files to process, exiting $0 ...
  echo -e "\n Finished at "$(date +"%d/%m/%Y %H:%M:%S")
  echo -e " === DONE ===\n"
  exit 0
else
  echo There are ${countfiles} netCDF files to process, comprising ${countfilesA} ascending and ${countfilesD} descending profile files.
fi

# 2.
# Move files to working area
echo Moving files to working area...
for fa in ${filestohandleA}
do
mv ${fa} ${WORKINGDATADIR}
done
for fd in ${filestohandleD}
do
mv ${fd} ${WORKINGDATADIR}
done
# make new files lists
if [[ $countfilesA -gt 0 ]]
then
  ascFiles=$(ls ${WORKINGDATADIR}/${ascFileString} 2>/dev/null) 
fi
if [[ $countfilesD -gt 0 ]]
then
  dscFiles=$(ls ${WORKINGDATADIR}/${dscFileString} 2>/dev/null)
fi

# 3.
# process into BUFR, for ascending and descending profiles  
# NB. we need to decide if we really want to make BUFR from the descent profiles ??? 
# Contact MSS team (Duncan Jeffery) if naming convention of output BUFR files changes!
echo -e "\nStart python processing to convert to BUFR (ascending profiles) ..." 
countnetcdfnotprocessed=0
arrayofnetcdffilesnotproc=()
countbufrfilesmadeA=0
if [[ $countfilesA -gt 0 ]]
then
  for file in ${ascFiles}
  do
    fl="$(basename ${file})"
    echo -e "\nProcessing $fl"
    f="${fl%.*}_p_${todayHM}"
    python2.7 ${PYTHONCODEDIR}/${PYTHONCODENAME} -i ${file} -o ${BUFRDEST}/${f}.dat
    if test -f ${BUFRDEST}/${f}.dat
    then
      countbufrfilesmadeA=$(( $countbufrfilesmadeA + 1 ))
    else
      arrayofnetcdffilesnotproc+=("$fl")
      countnetcdfnotprocessed=$(( $countnetcdfnotprocessed+1 ))
      echo -e "$fl was not processed successfully"
    fi
  done
else
  echo -e "There are no ascending profile files to process."
fi
echo -e "\nStart python processing to convert to BUFR (descending profiles) ..." 
countbufrfilesmadeD=0
if [[ $countfilesD -gt 0 ]]
then
  for file in ${dscFiles}
  do
    fl="$(basename ${file})"
    echo -e "\nProcessing $fl"
    f="${fl%.*}_p_${todayHM}"
    python2.7 ${PYTHONCODEDIR}/${PYTHONCODENAME} -i ${file} -o ${BUFRDEST}/${f}.dat
    if test -f ${BUFRDEST}/${f}.dat
    then
      countbufrfilesmadeD=$(( $countbufrfilesmadeD + 1 ))
    else
      arrayofnetcdffilesnotproc+=("$fl")
      countnetcdfnotprocessed=$(( $countnetcdfnotprocessed+1 ))
      echo -e "$fl was not processed successfully"
    fi
  done
else
  echo -e "There are no descending profile files to process."
fi
# summarise...
countbufrfilesmade=$(( ${countbufrfilesmadeA} + ${countbufrfilesmadeD} ))
echo -e "\nSummary: "
echo -e "${countfiles} netCDF files were processed, comprising ${countfilesA} ascending and ${countfilesD} descending profile files."
echo -e "$countbufrfilesmade BUFR files were created and delivered to $BUFRDEST."
echo -e "Comprising ${countbufrfilesmadeA} ascending and ${countbufrfilesmadeD} descending profiles."
if [[ $countnetcdfnotprocessed -gt 0 ]]
then
  echo -e "\n$countnetcdfnotprocessed netCDF files were not converted into BUFR."
  echo -e "These are listed below ..."
  echo -e ${arrayofnetcdffilesnotproc[@]}
fi


# 4. 
# move original netCDF files to processed folder 
if [[ $countfilesA -gt 0 ]]
then
  mv $ascFiles $PROCESSEDNCDIR
fi
if [[ $countfilesD -gt 0 ]]
then
  mv $dscFiles $PROCESSEDNCDIR
fi

# 5.
# FTP the BUFR files to MetSwitch
countBUFRfilestomove=$(ls ${BUFRDEST}/*.dat 2>/dev/null | wc -l)
bufrfilestohandle=$(ls ${BUFRDEST}/*.dat 2>/dev/null)
echo -e "\nFTPing ${countBUFRfilestomove} BUFR files to MetSwitch ${REMOTEHOSTBUFR}"
for f in ${bufrfilestohandle}
do
  bn=$(basename $f)
  ftp -n ${REMOTEHOSTBUFR} <<END_SCRIPT
  quote USER ${UNBUFR}
  quote PASS ${PWBUFR}
  put ${f} ${bn}.tmp  
  rename ${bn}.tmp ${bn}
  quit
END_SCRIPT
done
echo -e "Finished FTPing"

# 5b. 
# send myself a report email
echo "${countBUFRfilestomove} BUFR files were sent to metswitch (${REMOTEHOSTBUFR}) at $(date +"%d/%m/%Y %H:%M")." | mail -s "report from Argo netCDF-to-BUFR processing on exvmarproc01" fiona.carse@metoffice.gov.uk

# 6.
# Move the BUFR files away into a processed folder
echo -e "\nMoving FTPed BUFR files into ${PROCESSEDBUFRDIR}"
for i in ${bufrfilestohandle}
do
  mv ${i} ${PROCESSEDBUFRDIR}
done


# 7. 
# The end
echo -e "\n Finished at "$(date +"%d/%m/%Y %H:%M:%S")
echo -e " === DONE ===\n"

exit 0

