#!/bin/bash

# The two source lines below make this script work in crontab
# It seems like the .bash_profile is the best option (if use only bashrc, the bitstring module cannot be found.
# Either / or also works, couldn't decide which one was best, so left both in.
source /home/marinedg/.bash_profile

# load up python 3
# change to using conda access to Python 12/01/2023
conda deactivate
conda activate production-os46-1
#module unload scitools
#module load scitools/production-os45-1
pyver=$(which python)

# Set file path variables
SCRIPTDIR=/home/marinedg/bin/argo/netcdf2bufr_py3
DATATOPDIR=/data/local/marinedg/argo/netcdf_py3
NCDIR=${DATATOPDIR}/incoming/processed
BUFRDIR=${DATATOPDIR}/outgoing/bufr/processed

# set year month and day strings to grab statistics for
YEAR="2023"
MONTH="01"
#DAY="13"
DAY="??"

# set ouput file name
OUTNAME="ArgoTimeStats_${YEAR}${MONTH}.csv"

<<'COMMENT'

 1.  Create a variable 'bufrfiles' which is list files of .dat files to process
 2.  Loop over the BUFR files and do the following:
 3.  Extract the processed dates and WMOID_ProfNo string from the 'bufrfile' file names
 4.  Use the WMOID_ProfNo string to find the matching source .nc file and extract the JULD variable
 5.  (Compute the delay in hours)
 6.  Write out the results to a csv file, OUTNAME

COMMENT

echo -e "\n === Running "$0" ==="
echo -e " Started at "$(date +"%d/%m/%Y %H:%M:%S")"\n"

cd ${SCRIPTDIR} 

# 1.
# List the BUFR files for desired Y M D
bufrfiles=$(ls ${BUFRDIR}/R*_${YEAR}${MONTH}${DAY}_*.dat 2>/dev/null ) 
countBufrFiles=$(ls ${BUFRDIR}/R*_${YEAR}${MONTH}${DAY}_*.dat 2>/dev/null | wc -l) 
echo There are ${countBufrFiles} BUFR files processed on ${YEAR}${MONTH}${DAY}

# set up output file 
header="WMOID,ProfileNumber,BUFR_Produced_Time,Ob_Validity_Time,Delay_In_Seconds,Delay_In_Hours"
echo ${header} > ${OUTNAME}

# loop over BUFR files 
if [[ ${countBufrFiles} -gt 0 ]]
then
  for bf in ${bufrfiles}
  do
    # 3.
    # extract WMO ID, profile ID and processed datetime
    bn=$(basename ${bf})
    echo Matching details for ${bn} ...
    wmo=$(echo ${bn} | cut -d "_" -f 1)
    pn=$(echo ${bn} | cut -d "_" -f 2)
    pdate=$(echo ${bn} | cut -d "_" -f 4)
    ptime=$(echo ${bn} | cut -d "_" -f 5 | cut -d "." -f 1)
    echo WMO ID is ${wmo}, profile number is ${pn}
    echo Processed date and time is ${pdate} ${ptime}
    # 4.
    # find matching source netCDF file
    ncfile=$(ls ${NCDIR}/${wmo}_${pn}.nc 2>/dev/null)
    countncfiles=$(ls ${NCDIR}/${wmo}_${pn}.nc 2>/dev/null | wc -l)
    if [[ ${countncfiles} -eq 1 ]]
    then
      # extract the JULD info from the nc file
      echo Extracting validity time from ${ncfile}
      ncdump -t -v JULD ${ncfile} | tail -4  > tmp/ncdump.txt
      juldline=$(grep "JULD = " tmp/ncdump.txt)
      dt=$(echo ${juldline} | cut -d '"' -f 2)
      datestr=$(echo ${dt} | cut -d " " -f 1)
      timestr=$(echo ${dt} | cut -d " " -f 2)
      yyyy=$(echo ${datestr} | cut -d "-" -f 1)
      month=$(echo ${datestr} | cut -d "-" -f 2)
      day=$(echo ${datestr} | cut -d "-" -f 3)
      hour=$(echo ${timestr} | cut -d ":" -f 1)
      min=$(echo ${timestr} | cut -d ":" -f 2)
      echo JULD line in ncdump is: ${juldline}
      echo DT is: ${dt}
      echo date is: ${datestr}: YYYY is ${yyyy}, MM is ${month}, DD is ${day}
      echo time is: ${timestr}: HH is ${hour}, MM is ${min}
      #
      # 5. work out the difference, in seconds
      bufrdatestr="${pdate} ${ptime}"
      echo ${bufrdatestr}
      obsdatestr="${yyyy}${month}${day} ${hour}${min}"
      echo ${obsdatestr}
      bufrdate=$(date +%s -d"${bufrdatestr}")
      obsdate=$(date +%s -d"${obsdatestr}")
      delay_in_seconds=$(( ${bufrdate} - ${obsdate} ))
      delay_in_hours=$(( (bufrdate - obsdate) / (60*60) ))
      echo XXXXX 
      echo Delay in hours is ${delay_in_hours}
      echo XXXXX 
      #
      # 6.
      # write stats out to a csv file
      echo Writing stats to output csv file
      statsStr="${wmo},${pn},${bufrdatestr},${obsdatestr},${delay_in_seconds},${delay_in_hours}"
      echo ${statsStr} >> ${OUTNAME}
    else
      echo There is not an exact match, there are ${countncfiles} that match ${wmo}_${pn}
    fi
  done
fi

