from .api_wrappers import ApiWrapperMixin

class MappingMixin:
    """Provide an interface for Misty's mapping functions.

    """
    def __init__(self, ip):
        super().__init__(ip)

    def delete_slam_map(self, key: str):
        """Delete one of Misty's saved SLAM maps.

            Parameters
                key (str): unique key identifier for map
        """
        endpoint = 'slam/map'
        params = {'key': key}
        self.wrapper_delete(endpoint, params)

    def get_map(self):
        """Obtain occupancy grid data for currently active map.

            Values for occupancy grid:
                0: unknown
                1: open
                2: occupied
                3: covered
        """
        endpoint = 'slam/map'
        return self.wrapper_get(endpoint)

    def get_current_slam_map(self):
        """Obtain key for currently active map."""
        endpoint = 'slam/map/current'
        return self.wrapper_get(endpoint)

    def get_slam_maps(self):
        """Obtain a list of keys and names for existing maps."""
        endpoint = 'slam/map/ids'
        return self.wrapper_get(endpoint)

    def rename_slam_map(self, key: str, name: str):
        """Rename the existing map corresponding to the given key.

            Paremeters
                key (str): unique key identifier for map
                name (str): new name for the map corresponding to key
        """
        endpoint = 'slam/map/rename'
        params = {'Key': key, 'Name': name}
        self.wrapper_post(endpoint, params)

    def start_mapping(self):
        """Begin mapping for an area."""
        endpoint = 'slam/map/start'
        self.wrapper_post(endpoint)

    def stop_mapping(self):
        """Stop mapping process."""
        endpoint = 'slam/map/stop'
        self.wrapper_post(endpoint)

