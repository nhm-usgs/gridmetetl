import numpy as np
import datetime as dt
from numpy.ma import masked
import traceback
import netCDF4
from numpy import average
from netCDF4 import default_fillvals


def getaverage(data, wghts):
    try:
        v_ave = average(data, weights=wghts)
    except ZeroDivisionError:
        v_ave = default_fillvals['f8']
    return v_ave


def np_get_wval(ndata, wghts, hru_id=0):
    """
    Returns weighted average of ndata with weights = grp
    1) mdata = the subset of values associated with the gridmet id's that are mapped to hru_id.
    2) Some of these values may have nans if the gridmet id is outside of conus so only return values
    that are inside of conus
    3) this means that hru's that are entirely outside of conus will return nans which will ultimately,
    outside of this function get assigned zero's.
    4) the value is assigned the weighted average
    :param ndata: float array of data values
    :param wghts: float array of weights
    :param hru_id hru id number
    :return: numpy weighted averaged - masked to deal with nans associated with
            ndata that is outside of the conus.
    """
    mdata = np.ma.masked_array(ndata, np.isnan(ndata))
    tmp = np.ma.average(mdata, weights=wghts)

    if tmp is masked:
        # print(f'returning masked value: {hru_id}', ndata)
        return netCDF4.default_fillvals['f8']

    else:
        return tmp


def get_gm_url(type, dataset, numdays=None, startdate=None, enddate=None, ctype='GridMetSS'):
    """
    This helper function returns a url and payload to be used with requests
    to get climate data.  Returned values can be used in a request for example:
    myfile = requests.get(url, params=payload)

    :param numdays: proceeding number of days to retrieve
    :param dataset: datset to retrieve can be:
        'tmax', 'tmin', 'ppt'
    :param ctype: Type of url to retrieve:
        'GridMet':
    :return: URL for retrieving GridMet subset data and payload of options
    """
    sformat = "%Y-%m-%d"
    if type == 'days':
        dt1 = dt.timedelta(days=1)  # because Gridmet data release today is yesterdays data
        dt2 = dt.timedelta(days=numdays)

        end = dt.datetime.now() - dt1
        start = dt.datetime.now() - dt2
        str_start = start.strftime(sformat) + "T00:00:00Z"
        str_end = end.strftime(sformat) + "T00:00:00Z"
        str_start_cf = start.strftime(sformat) + " 00:00:00"
    elif type == 'date':
        str_start = startdate.strftime(sformat) + "T00:00:00Z"
        str_end = enddate.strftime(sformat) + "T00:00:00Z"
        str_start_cf = startdate.strftime(sformat) + " 00:00:00"

    dsvar = None
    url = None
    if ctype == 'GridMetSS':  # extract data using NetcdfSubset service
        if dataset == 'tmax':
            dsvar = 'daily_maximum_temperature'
            url = 'http://thredds.northwestknowledge.net:8080/thredds/ncss/agg_met_tmmx_1979_CurrentYear_CONUS.nc'
        elif dataset == 'tmin':
            dsvar = 'daily_minimum_temperature'
            url = 'http://thredds.northwestknowledge.net:8080/thredds/ncss/agg_met_tmmn_1979_CurrentYear_CONUS.nc'
        elif dataset == 'ppt':
            dsvar = 'precipitation_amount'
            url = 'http://thredds.northwestknowledge.net:8080/thredds/ncss/agg_met_pr_1979_CurrentYear_CONUS.nc'
        elif dataset == 'rhmax':
            dsvar = 'daily_maximum_relative_humidity'
            url = 'http://thredds.northwestknowledge.net:8080/thredds/ncss/grid/agg_met_rmax_1979_CurrentYear_CONUS.nc'
        elif dataset == 'rhmin':
            dsvar = 'daily_minimum_relative_humidity'
            url = 'http://thredds.northwestknowledge.net:8080/thredds/ncss/grid/agg_met_rmin_1979_CurrentYear_CONUS.nc'
        elif dataset == 'ws':
            dsvar = 'daily_mean_wind_speed'
            url = 'http://thredds.northwestknowledge.net:8080/thredds/ncss/grid/agg_met_vs_1979_CurrentYear_CONUS.nc'
        elif dataset == 'srad':
            dsvar = 'daily_mean_shortwave_radiation_at_surface'
            url = 'http://thredds.northwestknowledge.net:8080/thredds/ncss/grid/agg_met_srad_1979_CurrentYear_CONUS.nc'

        payload = {
            'var': dsvar,
            'north': '49.4000',
            'west': '-124.7666',
            'east': '-67.0583',
            'south': '25.0666',
            'disableLLSubset': 'on',
            'disableProjSubset': 'on',
            'horizStride': '1',
            'time_start': str_start,
            'time_end': str_end,
            'timeStride': '1',
            'accept': 'netcdf'}
        return str_start_cf, url, payload


def getxml():
    url = "http://thredds.northwestknowledge.net:8080/thredds/ncss/grid/agg_met_tmmx_1979_CurrentYear_CONUS.nc/dataset.xml"
    import urllib3
    import xmltodict

    http = urllib3.PoolManager()

    response = http.request('GET', url)
    try:
        data = xmltodict.parse(response.data)
    except:
        print("Failed to parse xml from response (%s)" % traceback.format_exc())
    return data
