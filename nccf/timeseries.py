import calendar

import numpy as np
import pandas as pd
import netCDF4 as nc

from .utils import create_crs_var, create_empty_var, create_time_var, create_var, create_id_var

def df2timeseries(df, ds, lat=0., lon=0., depth=0., global_attributes={}, platform_attributes={}, instrument_attributes={}, units={}):
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
    ds.Conventions = 'CF-1.6'
    ds.featureType = 'timeSeries'
    ds.cdm_data_type = 'Station'

    # any user-specified global attributes
    for k, v in global_attributes.items():
        ds.setncattr(k, v)

    # time series id and dimension
    create_id_var(ds, 'timeseries')
    
    FILL_VALUE = -9999.9

    # time
    create_time_var(ds, df.index)

    # lat / lon / depth
    vlat = ds.createVariable('latitude', np.float, ('timeseries',))
    vlat.units = 'degrees_north'
    vlat.valid_min = -90.
    vlat.valid_max = 90.
    vlat.axis = 'Y'
    vlat = lat

    vlon = ds.createVariable('longitude', np.float, ('timeseries',))
    vlon.units = 'degrees_east'
    vlon.valid_min = -180.
    vlon.valid_max = 180.
    vlon.axis = 'X'
    vlon = lon

    vdepth = ds.createVariable('depth', np.float, ('timeseries',))
    vdepth.standard_name = 'depth'
    vdepth.units = 'm'
    vdepth.positive = 'down'
    vdepth.axis = 'Z'
    vdepth.valid_min = 0.
    vdepth.valid_max = 10971.
    vdepth = depth

    # platform / instrument
    create_empty_var(ds, 'platform', platform_attributes)
    create_empty_var(ds, 'instrument', instrument_attributes)

    # crs
    create_crs_var(ds)

    # all non-spatiotemporal variables
    for varname in df.columns:
        v = create_var(ds, varname, df[varname], ('timeseries','time'))
        v.coordinates = 'time depth latitude longitude'
        if varname in units:
            v.units = units[varname]
        else:
            v.units = '1'
        v.grid_mapping = 'crs'
        v.platform = 'platform'
        v.instrument = 'instrument'
