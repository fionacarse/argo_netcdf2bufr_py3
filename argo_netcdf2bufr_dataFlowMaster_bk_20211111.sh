#!/bin/bash

# The two source lines below make this script work in crontab
# It seems like the .bash_profile is the best option (if use only bashrc, the bitstring module cannot be found.
# Either / or also works, couldn't decide which one was best, so left both in.
source /home/marinedg/.bash_profile

module unload scitools
module load scitools/production-os44-1
pyver=$(which python)

today=$(date +%Y%m%d)
todayHM=$(date +%Y%m%d_%H%M)
todayH=$(date +%k)
yesterday=$(date +%Y%m%d -d '1 days ago')

# Set file path variables
SCRIPTDIR=/home/marinedg/bin/argo/netcdf2bufr_py3
PYTHONCODEDIR=${SCRIPTDIR}/ArgoNetCDFToBufr/src
PYTHONCODENAME=argonetcdftobufr.py
WORKINGDATADIR=${SCRIPTDIR}/working/data
#DATATOPDIR=/data/local/marinedg/argo/netcdf_py3/test_20200806
DATATOPDIR=/data/local/marinedg/argo/netcdf_py3
NCDEST=$DATATOPDIR/incoming
BUFRDEST=$DATATOPDIR/outgoing/bufr
PROCESSEDNCDIR=${NCDEST}/processed
UNPROCESSEDNCDIR=${NCDEST}/unprocessed
PROCESSEDBUFRDIR=${BUFRDEST}/processed
TOOOLDNCDIR=${NCDEST}/unprocessed

# Set file name string variables 
# Contact MSS team (Duncan Jeffery) if naming convention changes!
ascFileString="R*_*[0-9].nc"
dscFileString="R*_*[0-9]D.nc"

# Configure FTP settings for sending BUFR files to MetDB
# changed to prod on 26/05/21 - also switched off py2 version this same day
REMOTEHOSTBUFR=exxmetswitchprod
#REMOTEHOSTBUFR=exxmetswitchdev
UNBUFR=argobufr
PWBUFR=4rg0bufr

# set an acceptable age for profiles, in days
acceptableAge=56.0

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
# List the files and check there are any available to be processed (also check age).
# check there are ascending files and move away any that are too old
countTooOldFilesA=0
countfilesA=0
countfilesA=$(ls -l ${NCDEST}/${ascFileString} 2>/dev/null | wc -l) 
if [[ ${countfilesA} -gt 0 ]]
then
  for i in ${NCDEST}/${ascFileString}
  do
    # check age of file is less than 56 days: 0 means False ie not too old; 
    #  1 means True, too old, do not process.
    tooOld=$(python test_ob_age.py ${i} ${acceptableAge})
    if [[ ${tooOld} -eq 1 ]]
    then
      echo The profile in $i is too old, it will not be processed for distribution to MetDB or GTS.
      countTooOldFilesA=${countTooOldFilesA}+1
      mv ${i} ${TOOOLDNCDIR}
    fi
  done
fi

# count ascending files again, should be just the new-enough ones left
countfilesA=$(ls -l ${NCDEST}/${ascFileString} 2>/dev/null | wc -l) 
if [[ $countfilesA -gt 0 ]]
then
  for i in ${NCDEST}/${ascFileString} 
  do 
    test -f "$i" && 
    echo Ascending profile files exist && 
    filestohandleA=$(ls ${NCDEST}/${ascFileString} 2>/dev/null) &&
    #countfilesA=$(ls -l ${NCDEST}/${ascFileString} 2>/dev/null | wc -l) &&
    break
  done
fi

# check there are descending files and move away any that are too old
countTooOldFilesD=0
countfilesD=0
countfilesD=$(ls -l ${NCDEST}/${dscFileString} 2>/dev/null | wc -l)
if [[ ${countfilesD} -gt 0 ]]
then
  for i in ${NCDEST}/${dscFileString}
  do
    # check age of file is less than 56 days: 0 means False ie not too old; 
    #  1 means True, too old, do not process.
    tooOld=$(python test_ob_age.py ${i} ${acceptableAge})
    if [[ ${tooOld} -eq 1 ]]
    then
      echo The profile in $i is too old, it will not be processed for distribution to MetDB or GTS.
      countTooOldFilesD=${countTooOldFilesD}+1
      mv ${i} ${TOOOLDNCDIR}
    fi
  done
fi

# count descending files again, should be just the new-enough ones left
countfilesD=$(ls -l ${NCDEST}/${dscFileString} 2>/dev/null | wc -l)
if [[ $countfilesD -gt 0 ]]
then
  for i in ${NCDEST}/${dscFileString}
  do
    test -f "$i" &&
    echo Descending profile files exist &&
    filestohandleD=$(ls ${NCDEST}/${dscFileString} 2>/dev/null) &&
    #countfilesD=$(ls -l ${NCDEST}/${dscFileString} 2>/dev/null | wc -l) &&
    break
  done
fi

countfiles=$(( ${countfilesA} + ${countfilesD} ))
countTooOldFiles=$(( ${countTooOldFilesA} + ${countTooOldFilesD} ))

# Check whether there are any files to process, exit the script if there are none.
echo ${countTooOldFiles} files were not processed because the profiles in them were older than ${acceptableAge} days. 
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
    echo -e "\nUsing python version $pyver"
    f="${fl%.*}_p_${todayHM}"
    python ${PYTHONCODEDIR}/${PYTHONCODENAME} -i ${file} -o ${BUFRDEST}/${f}.dat
    if test -f ${BUFRDEST}/${f}.dat
    then
      countbufrfilesmadeA=$(( $countbufrfilesmadeA + 1 ))
    else
      arrayofnetcdffilesnotproc+=("$fl")
      countnetcdfnotprocessed=$(( $countnetcdfnotprocessed+1 ))
      mv ${file} ${UNPROCESSEDNCDIR}
      echo -e "$fl was not processed successfully, moved to ${UNPROCESSEDNCDIR}"
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
    python ${PYTHONCODEDIR}/${PYTHONCODENAME} -i ${file} -o ${BUFRDEST}/${f}.dat
    if test -f ${BUFRDEST}/${f}.dat
    then
      countbufrfilesmadeD=$(( $countbufrfilesmadeD + 1 ))
    else
      arrayofnetcdffilesnotproc+=("$fl")
      countnetcdfnotprocessed=$(( $countnetcdfnotprocessed+1 ))
      mv ${file} ${UNPROCESSEDNCDIR}
      echo -e "$fl was not processed successfully, moved to ${UNPROCESSEDNCDIR}"
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
echo -e "${countTooOldFiles} netCDF files were not processed because their profiles were older than ${acceptableAge} days."
if [[ $countnetcdfnotprocessed -gt 0 ]]
then
  echo -e "\n$countnetcdfnotprocessed other netCDF files were not converted into BUFR."
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
# write line to text file so I can send myself a daily report email
# the last line of this setcion sends me an hourly email. This is too much info, now that the daily email is working.
emailbodytext="${countfiles} netCDF files were processed into ${countBUFRfilestomove} BUFR files. These BUFR files were sent to metswitch (${REMOTEHOSTBUFR}) at $(date +"%d/%m/%Y_%H:%M") - Python 3 test system."
#emailbodytext="${countfiles} netCDF files were processed into ${countBUFRfilestomove} BUFR files. These BUFR files were sent to metswitch (${REMOTEHOSTBUFR}) at $(date +"%d/%m/%Y_%H:%M")."
echo "${emailbodytext}" >> hourly_report_argo_netcdf2bufr.txt 
#echo "${emailbodytext}" | mail -s "report from Argo netCDF-to-BUFR py3 processing on exvmarproc01" fiona.carse@metoffice.gov.uk

# 5c.
# write file names to a text file, to add to daily email monitoring report sent to fiona.carse and BODC
ascFiles_bn=$(for a in $ascFiles;  do echo "$(basename $a)"; done)
dscFiles_bn=$(for d in $dscFiles;  do echo "$(basename $d)"; done)
echo "${ascFiles_bn}" "${dscFiles_bn}" >> hourly_report_netcdf_file_list.txt 


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

