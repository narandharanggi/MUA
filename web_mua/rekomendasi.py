from geopy.geocoders import Photon

class Geolocation():
    def __init__(self):
        self.geolocator = Photon(user_agent="geoapiExercises")

    def get_latitude_longitude(self, address):
        self.location = self.geolocator.geocode(address)
        return (self.location.latitude, self.location.longitude)