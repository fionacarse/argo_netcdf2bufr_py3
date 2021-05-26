#!/bin/bash

# copies the raw netcdf folder from the python 2 source to the python 3 source folder.
# to enable a period of parallel running
# Update 26/05/21: period of parallel running is finished today. Now MOVE the files across,
#   instead of copying.

# The two source lines below make this script work in crontab
# It seems like the .bash_profile is the best option (if use only bashrc, the bitstring module cannot be found.
# Either / or also works, couldn't decide which one was best, so left both in.
#source /home/marinedg/.bash_profile
 
echo -e "\n === Running "$0" ==="
echo -e " Started at "$(date +"%d/%m/%Y %H:%M:%S")"\n"

count="$(ls -l /data/local/marinedg/argo/netcdf/incoming/*.nc | wc -l)"
echo -e "Moving ${count} netcdf files to python 3 location."
#echo -e "Copying ${count} netcdf files to python 3 location."
#cp /data/local/marinedg/argo/netcdf/incoming/*.nc /data/local/marinedg/argo/netcdf_py3/incoming
mv /data/local/marinedg/argo/netcdf/incoming/*.nc /data/local/marinedg/argo/netcdf_py3/incoming

echo -e "\n Finished at "$(date +"%d/%m/%Y %H:%M:%S")
echo -e " === DONE ===\n"

exit 0

