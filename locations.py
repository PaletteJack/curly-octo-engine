import csv
from math import radians, sin, cos, sqrt, atan2

def load_address_database(file_path):
    address_db = {}
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            address, lat, lon = row
            address_db[address.lower()] = (float(lat), float(lon))
    return address_db

def find_coordinates(address, address_db):
    return address_db.get(address.lower())

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

def find_nearby_locations(address, locations, radius_km, address_db):
    address_coords = find_coordinates(address, address_db)
    if not address_coords:
        print(f"Address not found in database: {address}")
        return []

    address_lat, address_lon = address_coords
    nearby_locations = []

    for name, (lat, lon) in locations.items():
        distance = haversine_distance(address_lat, address_lon, lat, lon)
        if distance <= radius_km:
            nearby_locations.append((name, distance))

    return sorted(nearby_locations, key=lambda x: x[1])

address_db = load_address_database('address_database.csv')
address = "1600 Amphitheatre Parkway, Mountain View, CA"
locations = {
    "Stanford University": (37.4275, -122.1697),
    "San Francisco Airport": (37.6213, -122.3790),
    "Golden Gate Bridge": (37.8199, -122.4783),
    "San Jose State University": (37.3352, -121.8811),
    # Add more locations as needed
}

nearby = find_nearby_locations(address, locations, 10, address_db)

print(f"Locations within 10 km of {address}:")
for name, distance in nearby:
    print(f"{name}: {distance:.2f} km")