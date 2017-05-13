import urllib
# from novas import compat as novas
from astropy.coordinates import GCRS, ITRS, EarthLocation, CartesianRepresentation
from astropy import units as u
from astropy.time import Time
import datetime
import numpy as np

def eci2lla(x,y,z,dt):
    """
    Convert Earth-Centered Inertial (ECI) cartesian coordinates to latitude, longitude, and altitude, using astropy.

    Inputs :
    x = ECI X-coordinate (m)
    y = ECI Y-coordinate (m)
    z = ECI Z-coordinate (m)
    dt = UTC time (datetime object)
    Outputs :
    lon = longitude (radians)

    lat = geodetic latitude (radians)
    alt = height above WGS84 ellipsoid (m)
    """
    # convert datetime object to astropy time object
    tt=Time(dt,format='datetime')

    # Read the coordinates in the Geocentric Celestial Reference System
    gcrs = GCRS(CartesianRepresentation(x=x*u.m, y=y*u.m,z=z*u.m), obstime=tt)

    # Convert it to an Earth-fixed frame
    itrs = gcrs.transform_to(ITRS(obstime=tt))

    el = EarthLocation.from_geocentric(itrs.x, itrs.y, itrs.z)

    # conversion to geodetic
    lon, lat, alt = el.to_geodetic()
    # lon_val = lon.value

    return lon.value, lat.value, alt.value





def get_satellite_info(yyyymmdd):
    """
    Gets all of the J2000 data for satellites on a given day
    """
    response = urllib.urlopen("http://ephemerides.planet-labs.com/planet_" + yyyymmdd + ".states")
    info = response.read()
    satellite_info = {}

    rows = info.split('\n')
    for row in rows:
        if len(row) > 0:
            vals = row.split()
            satellite_info[vals[0]] = [float(v) for v in vals[1:-2]]
            utc_time = datetime.datetime.utcfromtimestamp(satellite_info[vals[0]][0]+946728000)
            lon, lat, alt = eci2lla(satellite_info[vals[0]][1],satellite_info[vals[0]][2],satellite_info[vals[0]][3],utc_time)
            # v_lon, v_lat, v_alt = eci2lla(satellite_info[vals[0]][4],satellite_info[vals[0]][5],satellite_info[vals[0]][6],utc_time)
            satellite_info[vals[0]] = [lon, lat, alt, satellite_info[vals[0]][4],satellite_info[vals[0]][5],satellite_info[vals[0]][6]]

    return satellite_info


def simulate_positions(satellite_info):
    positions = {}

    for k, v in satellite_info.items():
        lat = v[1]
        lon = v[0]
        alt = v[2]
        pos_list = [[lat, lon, alt]]
        lat_change = 30 * v[3] / 111111.0
        alt_change = 0
        for i in range(10):
            lon_change = 30 * v[4] / (111111.0 * np.cos(lat * 3.141593 / 180))
            lat = lat + lat_change
            lon = lon + lon_change
            alt = alt + alt_change
            pos_list.append([lat, lon, alt])
        positions[k] = pos_list

    return positions


def check_if_sat_above(sat_positions, desired_pos):
    for pos in sat_positions:
        lat_radius = pos[2] / 30000.0
        lon_radius = pos[2] / 15000.0
        if np.absolute(desired_pos[0] - pos[0]) < lat_radius and np.absolute(desired_pos[1] - pos[1]) < lon_radius:
            return True
    return False

def get_satellites(yyyymmdd, desired_pos):
    sat_info = get_satellite_info(yyyymmdd)
    positions = simulate_positions(sat_info)
    list_sats = []
    for k, v in positions.items():
        if check_if_sat_above(v, desired_pos):
            list_sats.append(k)
    return list_sats

# print(get_satellites('20170503', [34.0, 125.0]))
