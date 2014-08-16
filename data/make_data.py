#!/usr/bin/env python

import os
import zipfile

# Dictionary to store names of glacier data files and URLs for where to find them on the internet
helheim_files = {
    'TSX_E66.50N_27Jan09_07Feb09.vx': 'ftp://sidads.colorado.edu/pub/DATASETS/nsidc0481_MEASURES_greenland_V01/Ecoast-66.50N/TSX_Jan-27-2009_Feb-07-2009_19-57-11/*'}

jakobshavn_files = {
    'TSX_W69.10N_29Jan09_09Feb09.vx': 'ftp://sidads.colorado.edu/pub/DATASETS/nsidc0481_MEASURES_greenland_V01/Wcoast-69.10N/TSX_Jan-29-2009_Feb-09-2009_10-05-12/*'
}

kangerd_files = {
    'TSX_E68.80N_28Jan09_08Feb09.vx': 'ftp://sidads.colorado.edu/pub/DATASETS/nsidc0481_MEASURES_greenland_V01/Ecoast-68.80N/TSX_Jan-28-2009_Feb-08-2009_19-40-29/*'}

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
for glacier in glacier_data.keys():
    for filename in glacier_data[glacier].keys():
        if not os.path.exists(glacier+'/'+filename):
            url = glacier_data[glacier][filename]
            os.system('wget '+url+' -P '+glacier)

