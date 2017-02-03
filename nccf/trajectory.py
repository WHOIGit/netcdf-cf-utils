import calendar

import numpy as np
import pandas as pd
import netCDF4 as nc

from .cf import CFWriter, datetimes2unixtimes, setncattrs

class TrajectoryWriter(CFWriter):
    def from_dataframe(self, df, global_attributes={}, platform_attributes={}, instrument_attributes={}, units={}):
        """Convert a Pandas dataframe to a netCDF4 CF trajectory dataset.
        The dataframe is assumed to be indexed by UTC datetime and have
        columns called 'latitude' and 'longitude', and 'depth' ('altitude'
        is not supported). Depth should be in m.

        :param df: the dataframe
        :param ds: an open netCDF4 dataset
        :param global_attributes: global attributes to add to the dataset
        :param platform_attributes: attributes of the platform object
        :param instrument_attributes: attributes of the instrument object
        :param units: units for other variables, may be empty, any variables
          not mentioned will be given the units '1'
        """

        # spatiotemporal variables
        lats = df['latitude']
        lons = df['longitude']
        depths = df['depth']

        # all non spatiotemporal variables
        variables = df[[col for col in df.columns if col not in ['latitude','longitude','depth']]]

        # global attributes
        setncattrs(self.ds, {
            'Conventions': 'CF-1.6',
            'featureType': 'trajectory',
            'cdm_data_type': 'Trajectory'
        })

        # any user-specified global attributes
        setncattrs(self.ds, global_attributes)

        # trajectory id and dimension
        self.create_id_var('trajectory')

        var_dims = ('trajectory','time')
        
        # time
        times = datetimes2unixtimes(df.index)
        self.create_time_var(times, dimensions=var_dims)

        # lat / lon / depth
        lat = self.create_lat_var(dimensions=var_dims)
        lat[:] = np.array(lats)

        lon = self.create_lon_var(dimensions=var_dims)
        lon[:] = np.array(lons)

        depth = self.create_depth_var(dimensions=var_dims)
        depth[:] = np.array(depths)

        # platform / instrument
        self.create_platform_var(platform_attributes)
        self.create_instrument_var(instrument_attributes)

        # crs
        self.create_crs_var()

        # all non-spatiotemporal variables
        for varname in variables.columns:
            v = self.create_var(varname, variables[varname], dimensions=var_dims, units=units.get(varname))
            v.coordinates = 'time depth latitude longitude'
            v.grid_mapping = 'crs'
            v.platform = 'platform'
            v.instrument = 'instrument'
