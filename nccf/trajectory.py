import calendar

import numpy as np
import pandas as pd
import netCDF4 as nc

from .cf import CFWriter, datetimes2unixtimes, setncattrs, LAT_VAR, LON_VAR, DEPTH_VAR

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
        lats = df[LAT_VAR]
        lons = df[LON_VAR]
        depths = df[DEPTH_VAR]

        # all non spatiotemporal variables
        variables = df[[col for col in df.columns if col not in [LAT_VAR, LON_VAR, DEPTH_VAR]]]

        trajectory_vars = self.get_feature_vars('trajectory')

        # global attributes
        setncattrs(self.ds, {
            'Conventions': 'CF-1.6',
            'featureType': 'trajectory',
            'cdm_data_type': 'Trajectory',
            'cdm_trajectory_variables': trajectory_vars,
            'subsetVariables': trajectory_vars
        })

        # any user-specified global attributes
        setncattrs(self.ds, global_attributes)

        # trajectory id and dimension
        id_long_name = platform_attributes.get('long_name','my_platform')
        self.create_id_var('trajectory', long_name=id_long_name)

        var_dims = ('time',)
        
        # time
        times = datetimes2unixtimes(df.index)
        self.create_time_var(times)

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
        self.create_obs_vars(variables, var_dims, units)
