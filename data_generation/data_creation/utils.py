import random

# restrict latitude and longitude to a rectangle
def generate_coordinates_within_bounds(bounds, num_coordinates):
    """ bounds should be a tuple of tuples ((lat_min, lat_max), (lon_min, lon_max)) or a vector of tuples, 
    num_coordinates is an integer"""

    coordinates = []
    for _ in range(num_coordinates):
        lat = random.uniform(bounds[0][0], bounds[0][1])
        lon = random.uniform(bounds[1][0], bounds[1][1])
        coordinates.append((round(lat, 6), round(lon, 6)))
    return coordinates