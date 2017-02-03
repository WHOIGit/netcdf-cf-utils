import calendar

import numpy as np
import pandas as pd
import netCDF4 as nc

from .cf import CFWriter, datetimes2unixtimes, setncattrs

class TimeseriesWriter(CFWriter):
    def from_dataframe(self, df, lat=0., lon=0., depth=0., global_attributes={}, platform_attributes={}, instrument_attributes={}, units={}):
        """Convert a Pandas dataframe to a netCDF4 CF time series dataset.
        The dataframe is assumed to be indexed by UTC datetime.

        :param df: the dataframe
        :param ds: an open netCDF4 dataset
        :param lat: the latitude of the time series
        :param lon: the longitude of the time series
        :param depth: the depth of the time series (altitude is not supported)
        :param global_attributes: global attributes to add to the dataset
        :param platform_attributes: attributes of the platform object
        :param instrument_attributes: attributes of the instrument object
        :param units: units for other variables, may be empty, any variables
          not mentioned will be given the units '1'
        """

        # global attributes
        setncattrs(self.ds, {
            'Conventions': 'CF-1.6',
            'featureType': 'timeSeries',
            'cdm_data_type': 'Station'
        })

        # any user-specified global attributes
        setncattrs(self.ds, global_attributes)

        # time series id and dimension
        self.create_id_var('timeseries')

        FILL_VALUE = -9999.9

        # time
        times = datetimes2unixtimes(df.index)
        self.create_time_var(times)

        scalar_dim = ('timeseries',)
        
        # lat / lon / depth
        vlat = self.create_lat_var(dimensions=scalar_dim)
        vlat[:] = lat

        vlon = self.create_lon_var(dimensions=scalar_dim)
        vlon[:] = lon

        vdepth = self.create_depth_var(dimensions=scalar_dim)
        vdepth[:] = depth

        # platform / instrument

        self.create_platform_var(platform_attributes)
        self.create_instrument_var(instrument_attributes)

        # crs
        self.create_crs_var()

        # all non-spatiotemporal variables
        for varname in df.columns:
            v = self.create_var(varname, df[varname], ('timeseries','time'), units=units.get(varname))
            v.coordinates = 'time depth latitude longitude'
            v.grid_mapping = 'crs'
            v.platform = 'platform'
            v.instrument = 'instrument'
