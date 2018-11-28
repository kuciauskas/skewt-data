#!/usr/bin/python
import os
import glob
import datetime
import metpy
from netCDF4 import Dataset

# Installed Libraries
from IPython import embed as shell
import numpy as np
import netCDF4 as ncdf
import metpy.calc as mpcalc
from metpy.plots import add_metpy_logo, SkewT
from metpy.units import units
from netCDF4 import Dataset

import matplotlib.pyplot as plt

# work on a selected set of files
for path in glob.glob("NUCAPS*.nc"):
    print(path)
    nc = Dataset(path)

    for index in range(len(nc.dimensions['Number_of_CrIS_FORs'])):
        time = nc.variables['Time'][index]
        tym = time/1000.0
        final_time = datetime.datetime.fromtimestamp(tym).strftime('%Y%m%d.%H%M%S')

#    skew = SkewT(plt.figure(figsize=(6, 7)))
        lat = nc.variables[u'Latitude'][index]
        lon = nc.variables[u'Longitude'][index]
        lon_a = lon

# check if lat and lon are within the range
        if ((lat > 12.0 and lat < 16.0)) and ((lon > -19.0 and lon < -15.0)):
           print 'lat: ', lat, 'and lon: ', lon, ' is within limts'
        else:
           continue

        lon = abs(lon)
        lat = "%.1f" % (float(lat))
        lon = "%.1f" % (float(lon))
        lon_a = "%.1f" % (float(lon_a))

        fig = plt.figure(figsize=(13,8))
        add_metpy_logo(fig, 115, 100)
#        skew = SkewT(plt.figure(figsize=(13,8)))
        skew = SkewT(fig, rotation=45)

        temp_K = nc.variables[u'Temperature'][index] * units.kelvin
        temp_C = temp_K.to('degC')
        mixing = nc.variables[u'H2O_MR'][index]
        press = nc.variables[u'Pressure'][index] * units.hPa

        e = mpcalc.vapor_pressure(press, mixing)
        dewp_C = mpcalc.dewpoint(e)
        dewp_K = dewp_C.to('degK')

# Calculate LCL height and plot as black dot
        lcl_pressure, lcl_temperature = mpcalc.lcl(press[0], temp_C[0], dewp_C[0])
        skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')


# Plot the parcel profile as a black line
        prof = mpcalc.parcel_profile(press, temp_K[0], dewp_K[0]).to('degC')
        prof_K = mpcalc.parcel_profile(press, temp_K[0], dewp_K[0])
        skew.plot(press, prof, 'k', linewidth=4)

# plot out the skew-T paramters
# Add the relevant special lines
#        skew.plot(press, temp.to('degC'), color='tab:red', linewidth=3, alpha=0.5)
        skew.plot(press, temp_C, color='tab:red', linewidth=3, alpha=0.5)
#        skew.plot(press, dewp.to('degC'), color='tab:blue', linewidth=3, alpha=0.5)
        skew.plot(press, dewp_C, color='tab:green', linewidth=3, alpha=0.5)
        skew.ax.set_xlim(-50, 50)
        skew.ax.set_ylim(1000, 100)
        skew.plot_dry_adiabats()
        skew.plot_moist_adiabats()

# An example of a slanted line at constant T -- in this case the 0
# isotherm
        skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

#        skew.plot_mixing_lines()
# Shade areas of CAPE and CIN
#        skew.shade_cin(press, temp, prof)
        skew.shade_cape(press, temp_K, prof)

# calculate Convective inhibition (CIN) and Convective available potential energy (CAPE)
#        cin = mpcalc.cape_cin(press, temp, dewp, prof)
        cin = mpcalc.cape_cin(press, temp_C, dewp_C, prof_K)
        lfc = mpcalc.lfc(press, temp_K, dewp_K, prof)
        cin_val = cin[1].magnitude
        cin_val = "%.2f" % (float(cin_val))
        print('cin: ',cin_val, 'lfc: ', lfc)

        plt.ylabel('log P')
        title = "DTG: ", final_time, "    Lat: ", lat, "Lon: ", lon_a, "CI: ", cin_val
        plt.title(title, fontsize=12)
        index = "%03d" % (int(index+1))

#        plt.savefig('test_{}.png'.format(index))
        temp_fn = "NUCAPS_"+str(final_time)+".lat"+str(lat)+"lon"+str(lon)
        plt.savefig('{}.png'.format(temp_fn))
        plt.close()
    plt.show()
