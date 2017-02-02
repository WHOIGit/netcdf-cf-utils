import calendar

import numpy as np

def create_crs_var(ds, name='crs'):
    """:param ds: netCDF4 Dataset"""
    crs = ds.createVariable(name, np.float)
    crs.grid_mapping_name = 'latitude_longitude'
    crs.longitude_of_prime_meridian = 0.
    crs.semi_major_axis = 6378137.
    crs.inverse_flattening = 298.257223563
    crs.epsg_code = 'EPSG:4326'
    crs = 0.
    return crs

def create_empty_var(ds, name, attributes={}):
    ev = ds.createVariable(name,'S1')
    ev.long_name = name
    for k, v in attributes.items():
        ev.setncattr(k, v)
    ev = ''
    return ev

def create_id_var(ds, name, attributes={}):
    """create a dimension called name of size 1,
    a var called name with that dimension, and
    give it the attribute cf_role = {name}_id
    and long name name"""
    ds.createDimension(name,1)
    idvar = ds.createVariable(name,int,(name,))
    idvar.cf_role = '{}_id'.format(name)
    idvar.long_name = name
    idvar[:] = [0]
    return idvar

def create_time_var(ds, times, name='time'):
    """:param times: a datetime64 array, Series, or Index.
    also creates time dimension"""
    # convert datetime to floating point s since UNIX epoch
    times = np.asarray([calendar.timegm(x.utctimetuple()) for x in times]).astype(np.float)
    # call the dimension and variable the same thing
    ds.createDimension(name, size=len(times))
    t = ds.createVariable(name, times.dtype, (name,))
    t.units = 'seconds since 1970-01-01T00:00:00Z'
    t.standard_name = 'time'
    t.long_name = 'time'
    t.calendar = 'gregorian'
    t.axis = 'T'
    t[:] = times
    return t

FILL_VALUE = -9999.9

def create_var(ds, name, values, dimensions, fill_value=FILL_VALUE, valid_range=None):
    v = ds.createVariable(name, values.dtype, dimensions, fill_value=fill_value)
    v.long_name = name
    v.standard_name = name
    if valid_range is not None:
        v.valid_min, v.valid_max = valid_range
    v[:] = np.array(values)
    return v

