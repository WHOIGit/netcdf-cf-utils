import calendar

import numpy as np
import pandas as pd
import netCDF4 as nc

def df2trajectory(df, ds, global_attributes={}, platform_attributes={}, instrument_attributes={}, units={}):
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

    lats = df['latitude']
    lons = df['longitude']
    depths = df['depth']

    times = np.asarray([calendar.timegm(x.utctimetuple()) for x in df.index]).astype(np.float)

    # all non spatiotemporal variables
    variables = df[[col for col in df.columns if col not in ['latitude','longitude','depth']]]

    # global attributes
    ds.Conventions = 'CF-1.6'
    ds.featureType = 'trajectory'
    ds.cdm_data_type = 'Trajectory'

    # any user-specified global attributes
    for k, v in global_attributes.items():
        ds.setncattr(k, v)

    # trajectory id
    ds.createDimension('trajectory',1)
    tid = ds.createVariable('trajectory',int,('trajectory',))
    tid.cf_role = 'trajectory_id'
    tid.long_name = 'trajectory' # does not matter what this is
    tid[:] = [0]
    
    FILL_VALUE = -9999.9

    # time
    ds.createDimension('time', size=len(times))
    t = ds.createVariable('time', times.dtype, ('trajectory', 'time'))
    t.units = 'seconds since 1970-01-01T00:00:00Z'
    t.standard_name = 'time'
    t.long_name = 'time'
    t.calendar = 'gregorian'
    t.axis = 'T'
    t[:] = times

    def create_var(name, values, fill_value=FILL_VALUE, valid_range=None):
        v = ds.createVariable(name, values.dtype, ('trajectory','time'),
                              fill_value=fill_value)
        v.long_name = name
        v.standard_name = name
        if valid_range is not None:
            v.valid_min, v.valid_max = valid_range
        v[:] = np.array(values)
        return v

    # lat / lon / depth
    lat = create_var('latitude', lats, valid_range=(-90., 90.))
    lat.units = 'degrees_north'
    lat.axis = 'Y'

    lon = create_var('longitude', lons, valid_range=(-180., 180.))
    lon.units = 'degrees_east'
    lon.axis = 'X'

    depth = create_var('depth', depths, valid_range=(0., 10971.))
    depth.standard_name = 'depth'
    depth.units = 'm'
    depth.positive = 'down'
    depth.axis = 'Z'

    plat = ds.createVariable('platform','S1')
    for k, v in platform_attributes.items():
        plat.setncattr(k, v)
    plat = ''

    inst = ds.createVariable('instrument','S1')
    for k, v in instrument_attributes.items():
        inst.setncattr(k, v)

    # crs
    crs = ds.createVariable('crs', np.float)
    crs.grid_mapping_name = 'latitude_longitude'
    crs.longitude_of_prime_meridian = 0.
    crs.semi_major_axis = 6378137.
    crs.inverse_flattening = 298.257223563
    crs.epsg_code = 'EPSG:4326'
    crs = 0.

    # all non-spatiotemporal variables
    for varname in variables.columns:
        v = create_var(varname, variables[varname])
        v.coordinates = 'time depth latitude longitude'
        if varname in units:
            v.units = units[varname]
        else:
            v.units = '1'
        v.grid_mapping = 'crs'
        v.platform = 'platform'
        v.instrument = 'instrument'
