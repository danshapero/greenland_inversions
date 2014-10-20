#!/usr/bin/env python

import os
import zipfile

# -----------------------
# Retrieve velocity data
# -----------------------

# Dictionary to store names of glacier velocity data files and URLs for where
# to find them on the internet
helheim_files = {
    'TSX_E66.50N_27Jan09_07Feb09': 'ftp://sidads.colorado.edu/pub/DATASETS/nsidc0481_MEASURES_greenland_V01/Ecoast-66.50N/TSX_Jan-27-2009_Feb-07-2009_19-57-11/'}

jakobshavn_files = {
    'mosaicOffsets': 'http://students.washington.edu/shapero/jakobshavn/'
}

kangerd_files = {
    'TSX_E68.80N_28Jan09_08Feb09': 'ftp://sidads.colorado.edu/pub/DATASETS/nsidc0481_MEASURES_greenland_V01/Ecoast-68.80N/TSX_Jan-28-2009_Feb-08-2009_19-40-29/'}

glacier_data = {
    'helheim': helheim_files,
    'jakobshavn': jakobshavn_files,
    'kangerd': kangerd_files
}
             

# Make directories
for glacier in glacier_data.keys():
    if not os.path.exists(glacier):
        os.makedirs(glacier)
            

# Retrieve data
extensions = ['.vx', '.vx.geodat', '.vy', '.vy.geodat',
                '.ex', '.ex.geodat', '.ey', '.ey.geodat', '.meta']
for glacier in glacier_data.keys():
    for filestem in glacier_data[glacier].keys():
        for e in extensions:
            filename = filestem + e
            if not os.path.exists(glacier + '/' + filename):
                url = glacier_data[glacier][filestem] + filename
                os.system('wget ' + url + ' -P ' + glacier)



# -----------------------------
# Retrieve data for Jakobshavn
# -----------------------------

url = "http://students.washington.edu/shapero/jakobshavn/"
if not os.path.exists("jakobshavn/dem13Mar.smooth"):
    os.system("wget " + url + "dem13Mar.smooth -P jakobshavn")
    os.system("wget " + url + "dem13Mar.smooth.geodat -P jakobshavn")

