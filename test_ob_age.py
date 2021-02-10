# some code to check if a file contains an ob 
# more than X days old
# if so, a decision can be made not to process it into BUFR for the GTS.

import pdb
import netCDF4 as nc
import numpy as np
import datetime
import sys

#DATADIR="/data/local/marinedg/argo/netcdf_py3/incoming/processed"
#FILE="R2901892_238.nc"
#ACCEPTABLE_AGE=30.0

PATHANDFILE = sys.argv[1]
ACCEPTABLE_AGE = float(sys.argv[2])
 
#fn = '{}/{}'.format(DATADIR,FILE)
fn = PATHANDFILE
ds = nc.Dataset(fn)

time_var = ds.variables['JULD']
obtime = nc.num2date(time_var[:],time_var.units)
if obtime.size > 0:
    obdt = obtime[0]
else:
    obdt = np.nan

dtnow = datetime.datetime.now()    

ob_age = dtnow - obdt
ob_age_in_s = ob_age.seconds
ob_age_in_d = ob_age.days
ob_age_in_days = ob_age_in_d + (ob_age_in_s / (24.0 * 60.0 * 60.0) )

if ob_age_in_days > ACCEPTABLE_AGE:
    verdict = 1
    #print('Profile is {} days old, this is more than {}, do not process into BUFR'.format(np.round(ob_age_in_days,1), ACCEPTABLE_AGE))
else:
    verdict = 0
    #print('Profile is {} days old (less than threshold of {} days), process into BUFR'.format(np.round(ob_age_in_days,1), ACCEPTABLE_AGE))

print(verdict)

