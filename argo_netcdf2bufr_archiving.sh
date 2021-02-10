#!/bin/bash

source /home/marinedg/.bash_profile
source /home/marinedg/.bashrc

# Aim to run this once per month to clear out the previous months' data files:
#  1. remove the source netCDF files older than 2 months old (do not store to MASS, these files can be 're-got' from BODC if they are needed).
#  2. Store the previous months' BUFR files in MASS, then remove files from exvmarproc01.

onemonthago=$(date +%Y%m%d -d '29 days ago')
onemonthago_y=$(date +%Y -d '29 days ago')
onemonthago_m=$(date +%m -d '29 days ago')
twomonthsago=$(date +%Y%m%d -d '59 days ago')
twomonthsago_y=$(date +%Y -d '59 days ago')
twomonthsago_m=$(date +%m -d '59 days ago')

echo One month ago was ${onemonthago}, month ${onemonthago_m}, year ${onemonthago_y}
echo Two months ago was ${twomonthsago}, month ${twomonthsago_m}, year ${twomonthsago_y}

netcdffileext=nc
bufrfileext=dat

SCRIPTDIR=/home/marinedg/bin/argo/netcdf2bufr_py3
DATATOPDIR=/data/local/marinedg/argo/netcdf_py3
WORKING=${DATATOPDIR}/archive
SRC_BUFR=${DATATOPDIR}/outgoing/bufr/processed
SRC_NETCDF=${DATATOPDIR}/incoming/processed
MOO_BASE=moo:/adhoc/users/marinedg/argo
MOO_BUFR=bufr
emailToList="fiona.carse@metoffice.gov.uk jon.turton@metoffice.gov.uk"
emailSubject="Archiving failure report from Argo netcdf2bufr system on exvmarproc01"

# 0. Start monthly archiving run
dtnow=$(date +%Y%m%d_%H:%M)
echo --
echo --
echo -- Starting monthly archiving run for Argo BUFR data, commencing ${dtnow}.
echo --
echo --

# 1. Remove all netcdf files older than 2 months (62 days) 
#    DO this by simple deletion, no need to store in MASS as they can be re-got from BODC if needed. 
#    
cd ${SCRIPTDIR}
countNetCDFFiles=$(find ${SRC_NETCDF}/*.${netcdffileext} -mtime +62 -type f | wc -l)
cd -
find ${SRC_NETCDF}/*.${netcdffileext} -mtime +62 -type f -delete
echo Removing ${countNetCDFFiles} netCDF files that are over 62 days old from ${SRC_NETCDF}
echo --

# 2. Process the outgoing BUFR messages into monthly .tar.gz files, 
#    Put these into MASS, 
#    then remove the BUFR files from exvmarproc01.

dtnow=$(date +%Y%m%d_%H:%M)
echo Processing BUFR files at ${dtnow}...

cd ${WORKING}

# Count up the files to be archived... process if there are more than zero files.
c_argobufrfiles=$(ls ${SRC_BUFR}/*_${onemonthago_y}${onemonthago_m}??_*.${bufrfileext} ${SRC_BUFR}/*_${twomonthsago_y}${twomonthsago_m}??_*.${bufrfileext} 2>/dev/null | wc -l)
if [ "${c_argobufrfiles}" -gt "0" ]; then
  # count files one month old
  c_argobufrfiles_1=$(ls ${SRC_BUFR}/*_${onemonthago_y}${onemonthago_m}??_*.${bufrfileext} 2>/dev/null | wc -l)
  # count files two months old
  c_argobufrfiles_2=$(ls ${SRC_BUFR}/*_${twomonthsago_y}${twomonthsago_m}??_*.${bufrfileext} 2>/dev/null | wc -l)
  #
  # process files 1 month old
  #
  if [ ! -d "tmp" ]; then
    mkdir tmp
  fi
  if [ "${c_argobufrfiles_1}" -gt "0" ]; then
    argobufrfiles_1=$(ls ${SRC_BUFR}/*_${onemonthago_y}${onemonthago_m}??_*.${bufrfileext})
    for i in ${argobufrfiles_1}
    do
      mv ${i} tmp/
    done
    echo Tarring up ${c_argobufrfiles_1} bufr files for ${onemonthago_y} ${onemonthago_m}...
    tarfilename1=Argo_netcdf2bufr_${onemonthago_y}${onemonthago_m}.tar.gz
    tar -zcf ${tarfilename1} tmp/
    echo Putting ${tarfilename1} into MASS...
    moo put ${tarfilename1} ${MOO_BASE}/${MOO_BUFR}
    wait
    testMooFileOK1="$(moo test -f ${MOO_BASE}/${MOO_BUFR}/${tarfilename1})"
    if ${testMooFileOK1} -eq "true"; then
      echo ${tarfilename1} arrived in MASS OK, remove tar.gz file and tmp folder from exvmarproc01
      rm -r tmp/
      rm ${tarfilename1}
      echo "Archiving argo BUFR worked well" | mail -s "argo bufr archiving worked well" fiona.carse@metoffice.gov.uk 
    else
      echo ${tarfilename1} did not arrive in MASS. 
      echo Move raw data files back to original location, remove tmp/ and tar.gz file 
      echo and email a warning.
      for f in tmp/*_${onemonthago_y}${onemonthago_m}??_*.${bufrfileext}
      do
        mv ${f} ${SRC_BUFR}
      done
      rm -r tmp/
      rm ${tarfilename1}
      emailbodytext="The monthly archiving of BUFR files from the netCDF to BUFR processing system on exvmarproc01 has failed for year ${onemonthago_y}, month ${onemonthago_m}. The BUFR files have not been stored in MASS, leaving ${c_argobufrfiles_1} BUFR files in folder ${SRC_BUFR} in exvmarproc01. A build-up of small files can lead to failure of all processing (not just Argo) on exvmarproc01, because the machine has a finite starage capacity and also a finite number of i-nodes available. Please try to manually re-run the archiving script, which is here: ${SCRIPTDIR}/argo_netcdf2bufr_archiving.sh "
      echo "${emailbodytext}" | mail -s "${emailSubject}" ${emailToList}
    fi 
  fi
  #
  # process files 2 months old
  #
  if [ ! -d "tmp" ]; then
    mkdir tmp
  fi
  if [ "${c_argobufrfiles_2}" -gt "0" ]; then
    argobufrfiles_2=$(ls ${SRC_BUFR}/*_${twomonthsago_y}${twomonthsago_m}??_*.${bufrfileext})
    for i in ${argobufrfiles_2}
    do
      mv ${i} tmp/
    done
    echo Tarring up ${c_argobufrfiles_2} bufr files for ${twomonthsago_y} ${twomonthsago_m}...
    tarfilename2=Argo_netcdf2bufr_${twomonthsago_y}${twomonthsago_m}.tar.gz
    tar -zcf ${tarfilename2} tmp/
    echo Putting ${tarfilename2} into MASS...
    moo put ${tarfilename2} ${MOO_BASE}/${MOO_BUFR}
    wait
    testMooFileOK2="$(moo test -f ${MOO_BASE}/${MOO_BUFR}/${tarfilename2})"
    if "${testMooFileOK2}" -eq "true"; then
      echo ${tarfilename2} arrived in MASS OK, remove tar.gz file and tmp folder from exvmarproc01
      rm -r tmp/
      rm ${tarfilename2}
      echo "Archiving argo BUFR worked well" | mail -s "argo bufr archiving worked well" fiona.carse@metoffice.gov.uk 
    else
      echo ${tarfilename2} did not arrive in MASS. 
      echo Move raw data files back to original location, remove tmp/ and tar.gz file 
      echo and email a warning.
      for f in tmp/*_${twomonthsago_y}${twomonthsago_m}??_*.${bufrfileext}
      do
        mv ${f} ${SRC_BUFR}
      done
      rm -r tmp/
      rm ${tarfilename2}
      emailbodytext="The monthly archiving of BUFR files from the netCDF to BUFR processing system on exvmarproc01 has failed for year ${twomonthsago_y}, month ${twomonthsago_m}. The BUFR files have not been stored in MASS, leaving ${c_argobufrfiles_2} BUFR files in folder ${SRC_BUFR} in exvmarproc01. A build-up of small files can lead to failure of all processing (not just Argo) on exvmarproc01, because the machine has a finite starage capacity and also a finite number of i-nodes available. Please try to manually re-run the archiving script, which is here: ${SCRIPTDIR}/argo_netcdf2bufr_archiving.sh "
      echo "${emailbodytext}" | mail -s "${emailSubject}" ${emailToList}
    fi 
  fi
else
  echo There are no BUFR files from last month or the month before to archive to MASS. 
fi

cd -

# 3. End monthly archiving run
dtnow=$(date +%Y%m%d_%H:%M)
echo --
echo --
echo -- Ending monthly archiving run for Argo netcdf2bufr data, finished running at ${dtnow}.
echo --
echo --

exit 0



