"""This module provides an interface for Misty's SLAM and camera functions.
This includes mapping and tracking. The documentation for Misty's corresponding
API functionality can be found at
https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#navigation
"""

import base64
from api_wrappers import ApiWrapperMixin

class MappingMixin(ApiWrapperMixin):
    """Provide an interface for Misty's mapping functions.

    """
    def __init__(self, ip):
        super().__init__(ip)

    def delete_slam_map(self, key: str):
        """Delete one of Misty's saved SLAM maps.

        Parameters
        ----------
        key: str
            unique key identifier for map
        """
        endpoint = 'slam/map'
        params = {'key': key}
        self.wrapper_delete(endpoint, params)

    def get_map(self):
        """Obtain occupancy grid data for currently active map.
        
        Notes
        -----
        Values for occupancy grid:

        * 0: unknown
        * 1: open
        * 2: occupied
        * 3: covered

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
        ----------
        key: str
			unique key identifier for map
        name: str
			new name for the map corresponding to key
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


class TrackingMixin(ApiWrapperMixin):
    """Provide an interface for Misty's tracking functions.

    """
    def __init__(self, ip):
        super().__init__(ip)

    def drive_to_location(self, x: int, y: int):
        """Drives to provided destination at (x, y).

        ..IMPORTANT::
          Use `start_tracking` before calling this function
          to have Misty start tracking the location, and use `stop_tracking`
          to stop tracking after arriving to the destination.

        Parameters
        ----------
        x: int
            X coordinate for the cell in the occupancy grid to drive to.
            In the occupancy grid, the X coordinate represents the
            index of the array that contains the desired cell.
        y: int
            Y coordinate for the cell in the occupancy grid to drive to.
            In the occupancy grid, the Y coordinate represents the
            index of the desired cell, within its corresponding array in
            the occupancy grid.
        """
        dest = f'{x}:{y}'
        endpoint = 'drive/coordinates'
        params = {'Destination': dest}
        self.wrapper_post(endpoint, params)

    def follow_path(self, path: list, velocity: float = 0.5,
                    full_spin_duration: float = 15, 
                    waypoint_accuracy: float = 0.1,
                    rotate_threshold: float = 10):
        """Drives Misty on the path defined by a list of given coordinates.

        ..IMPORTANT:
          Use `start_tracking` before calling this function to have
          Misty start tracking the location. Misty will not be able to
          follow a path if there are unmapped obstacles in the way.

        Parameters
        ----------
        path: list of [x, y] pairs
           A list of coordinate pairs, each of which represents a waypoint
           on Misty's path.
        velocity: float, default 0.5
            A fraction of Misty's maximum velocity (should be between 0 and
            1 exclusive). Determines how fast Misty drives in a straight line.
        full_spin_duration: float, default 15
            Duration in seconds it takes for Misty to complete a 360 degree
            spin; determines how fast Misty spins or pivots.
        waypoint_accuracy: float, default 0.1
            How close in meters Misty gets to a waypoint before considering
            itself to have reached it.
        rotate_threshold: float, default 10
            When Misty's bearing relative to the next waypoint (in degrees)
            is larger than the threshold, the robot pivots until it becomes
            lower than the threshold.
        """
        if not 0 < velocity < 1:
            raise ValueError('Invalid value for velocity, should be between 0 and 1.')
        if waypoint_accuracy <= 0:
            raise ValueError('Invalid value for waypoint_accuracy, should be'
                             + 'greater than 0')
        if not 0 <= rotate_threshold <= 360:
            raise ValueError('Invalid value for rotate_threshold, should be'
                             + 'between 0 and 360')

        path_coords = [f'{x}:{y}' for x, y in path]
        strpath = ','.join(path_coords)

        endpoint = 'drive/path'
        params = {
            'Path': strpath,
            'Velocity': velocity,
            'FullSpinDuration': full_spin_duration,
            'WaypointAccuracy': waypoint_accuracy,
            'RotateThreshold': rotate_threshold,
        }
        self.wrapper_post(endpoint, params)


    def start_tracking(self):
        """Make Misty start tracking its location."""
        endpoint = 'slam/track/start'
        self.wrapper_post(endpoint)


    def stop_tracking(self):
        """Make Misty stop tracking its location."""
        endpoint = 'slam/track/stop'
        self.wrapper_post(endpoint)

class SlamSettingsMixin(ApiWrapperMixin):
    """Provide an interface to Misty's SLAM settings."""

    def __init__(self, ip):
        super().__init__(ip)

    def get_hazard_settings(self):
        """Obtain the current hazards system settings for Misty's time-of-flight and bump sensors.

        Returns a dictionary with the following key-value pairs:

        * `bumpSensors` (array): An array of objects that describe whether each bump sensor is
          enabled or disabled. Each object in the bumpSensors array includes the following
          key/value pairs:

            - `enabled` (bool): Whether hazards are enabled for a sensor (`true`) or not (`false`).
            - `sensorName` (str): The name of this bump sensor. May be one of

                + `Bump_FrontRight`
                + `Bump_FrontLeft`
                + `Bump_RearRight`
                + `Bump_RearLeft`

        * `timeOfFlightSensors` (array): An array of objects that describe the distance
          threshold that triggers a hazard response for each of Misty's time-of-flight
          sensors. Includes the following key/value pairs:

            - `sensorName` (str): The name of this time-of-flight sensor. One of the following:

                + `TOF_Right`
                + `TOF_Center`
                + `TOF_Left`
                + `TOF_Back`
                + `TOF_DownFrontRight`
                + `TOF_DownFrontRight`
                + `TOF_DownFrontLeft`
                + `TOF_DownBackRight`
                + `TOF_DownBackLeft`

            - `threshold` (double): The minimum distance (in meters) that triggers a hazard
              state for this time-of-flight sensor. A threshold value of 0 means hazards
              are disabled for this sensor.

        """

        endpoint = 'hazards/settings'
        return self.wrapper_get(endpoint)

    def get_slam_ir_exposure_and_gain(self):
        """Obtain the current exposure and gain settings for the infrared cameras in the
        Occipital Structure Core depth sensor.

        Returns a dictionary with the following key/value pairs:

        * `exposure` (float): The current exposure levels for the infrared cameras in
          the depth sensor (in seconds).
        * `gain` (int): The current gain levels for the infrared cameras in the
          depth sensor (in dB).

        """

        endpoint = 'slam/settings/ir'
        return self.wrapper_get(endpoint)

    def get_slam_navigation_diagnostics(self):
        """Obtain diagnostic information about Misty's navigation system.

        Returns a stringified JSON object with diagnostic information about the current
        status of Misty's SLAM system.

        Notes
        -----
        The information in the data object for this command is primarily used by the Misty
        Robotics engineering and support staff to troubleshoot and root-cause issues with
        Misty's SLAM system. The contents of this data object are likely to change without
        notice in future system updates.

        """

        endpoint = 'slam/diagnostics'
        return self.wrapper_get(endpoint)

    def get_slam_visible_exposure_and_gain(self):
        """Obtain the current exposure and gain settings for the fisheye camera in the
        Occipital Structure Core depth sensor.

        Returns a dictionary with the following key/value pairs:

        * `exposure` (float): The current exposure levels for the infrared cameras in
          the depth sensor (in seconds).
        * `gain` (int): The current gain levels for the infrared cameras in the
          depth sensor (in dB).

        """

        endpoint = 'slam/settings/ir'
        return self.wrapper_get(endpoint)

    def reset_slam(self):
        """Reset Misty's SLAM sensors."""

        endpoint = 'slam/reset'
        self.wrapper_post(endpoint)

    def set_slam_ir_exposure_and_gain(self, exposure, gain):
        """Set the exposure and gain settings for the infrared cameras in the Occipital
        Structure Core depth sensor.

        ..IMPORTANT::
          This can impact the performance of Misty's SLAM system. It is recommended to avoid
          changing these settings.

        Parameters
        ----------
        exposure: float
            Exposure levels for the infrared cameras in the depth sensor (in seconds).
            Should be a value between 0.001 and 0.033.
        gain: int
            Gain levels for the infrared cameras in the depth sensor (in dB). Should be
            a value between 0 and 3.

        Notes
        -----
        If this function is called when the SLAM system is not streaming, the camera
        settings will not update. Use start_slam_streaming to begin streaming.

        """

        if not 0.001 <= exposure <= 0.033:
            raise ValueError('Invalid value for exposure, should be between 0.001 and 0.033.')
        if not int(gain) == gain:
            raise TypeError('Invalid type for gain argument, should be int.')
        elif not 0 <= gain <= 3:
            raise ValueError('Invalid value for gain, should be between 0 and 3.')

        params = {'Exposure': exposure, 'Gain': int(gain)}
        endpoint = 'slam/settings/ir'
        self.wrapper_post(endpoint, params)

    def set_slam_visible_exposure_and_gain(self, exposure, gain):
        """Set the exposure and gain settings for the fisheye camera in the Occipital
        Structure Core depth sensor.

        Parameters
        ----------
        exposure: float
            Exposure levels for the fisheye camera in the depth sensor (in seconds).
            Should be a value between 0.001 and 0.033.
        gain: int
            Gain levels for the fisheye camera in the depth sensor (in dB). Should be
            a value between 1 and 8.

        Notes
        -----
        If this function is called when the SLAM system is not streaming, the camera
        settings will not update. Use start_slam_streaming to begin streaming.

        """

        if not 0.001 <= exposure <= 0.033:
            raise ValueError('Invalid value for exposure, should be between 0.001 and 0.033.')
        if not int(gain) == gain:
            raise TypeError('Invalid type for gain argument, should be int.')
        elif not 0 <= gain <= 8:
            raise ValueError('Invalid value for gain, should be between 0 and 8.')

        params = {'Exposure': exposure, 'Gain': int(gain)}
        endpoint = 'slam/settings/visible'
        self.wrapper_post(endpoint, params)

    def start_slam_streaming(self):
        """Open the data stream from the Occipital Structure Core depth sensor, so you can
        obtain image and depth data when Misty is not actively tracking or mapping.

        ..IMPORTANT:
          Use the `stop_slam_streaming` function to close the depth sensor data stream after
          using it. This turns off the laser in the depth sensor and lowers power consumption.

        Notes
        -----
        Misty's 4K camera may not work while the depth sensor data stream is open.

        """
        endpoint = 'slam/streaming/start'
        self.wrapper_post(endpoint)

    def stop_slam_streaming(self):
        """Close the data stream from the Occipital Structure Core depth sensor.

        ..IMPORTANT:
          Always use this function after using `start_slam_streaming` or any functions that
          use Misty's Occipital Structure Core depth sensor.

        """
        endpoint = 'slam/streaming/stop'
        self.wrapper_post(endpoint)

    def update_hazard_settings(self,
                               revert_to_default: bool = False,
                               disable_time_of_flights: bool = False,
                               disable_bump_sensors: bool = False,
                               bump_sensors_enabled: list = None,
                               time_of_flight_thresholds: list = None):
        """Change the hazard system settings for Misty's bump and time-of-flight sensors.

        Enable or disable hazard triggers for all bump or time-of-flight sensors, or adjust
        the hazard trigger settings for each sensor individually. See the documentation at
        https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#updatehazardsettings
        for the default values.

        .. WARNING::
           Misty cannot safely drive over ledges taller than 0.06 m. Navigating drops higher
           than 0.06 meters can cause Misty to tip or fall and become damaged.

        Parameters
        ----------
        revert_to_default: bool, default False
            If `True`, sets Misty to use default hazard system settings. No efect if `False`.
        disable_time_of_flights: bool, default False
            If `True`, disables hazards for all time-of-flight sensors by setting their
            `threshold` values to 0.
        disable_bump_sensors: bool, default False
            If `True`, disables hazards for all bump sensors.
        bump_sensors_enabled: list of (sensor_name, enabled), default None
            An unordered list of up to four tuples that you can use to turn hazards
            on or off for each of Misty's bump sensors. It only needs to include tuples 
            for the sensors that you want to adjust. Each tuple must include the
            following values:

            * `sensor_name` (`str`): The name of one of Misty's bump sensors. May be one of
              `Bump_FrontRight`, `Bump_FrontLeft`, `Bump_RearRight` and `Bump_RearLeft`.
            * `enabled` (`bool`): Whether hazards should be enabled for the corresponding
              bump sensor (`True`) or not (`False`).

        time_of_flight_thresholds: list of (sensor_name, threshold), default None
            An unordered list of up to eight tuples that set the minimum distance threshold
            to trigger a hazard state for each of Misty's TOF sensors. It only needs to
            include tuples for the sensors you want to adjust. Each tuple must include the
            following values.

            * `sensor_name` (`str`): The name of one of Misty's time-of-flight sensors.
              May be one of `TOF_DownFrontRight`, `TOF_DownFrontLeft`, `TOF_DownBackRight`,
              `TOF_DownBackLeft`, `TOF_Right`, `TOF_Left`, `TOF_Center`, and `TOF_Back`.
            * `threshold` (`double`): Minimum distance in meters that triggers a hazard
               state for the corresponding TOF sensor. A threshold of 0 disables hazards.

        Notes
        -----
        The settings for Misty's hazard system reset to default values every time the robot
        boots up. This means changes applied with this function do not save across reboot cycles.

        """

        if bump_sensors_enabled:
            bump_sensors_enabled = [{'sensorName': name, 'enabled': enabled} \
                                    for name, enabled in bump_sensors_enabled]
        if time_of_flight_thresholds:
            time_of_flight_thresholds = [{'sensorName': name, 'threshold': threshold} \
                                         for name, threshold in time_of_flight_thresholds]

        params = {
            'RevertToDefault': revert_to_default,
            'DisableTimeOfFlights': disable_time_of_flights,
            'BumpSensorsEnabled': bump_sensors_enabled,
            'TimeOfFlightThresholds': time_of_flight_thresholds,
        }

        headers = {'Content-type': 'application/json'}
        endpoint = 'hazard/updatebasesettings'
        self.wrapper_post(endpoint, params=params, headers=headers)

    def take_depth_picture(self):
        """Provide the current distance of objects from Misty's Occipital Structure Core depth sensor.

        Returns a dictionary with a value for `image`, which contains an array of numerical
        values which represent the distance in millimeters from the sensor for each pixel in
        the captured image. The `image` array should be interpreted as a matrix of size
        `height` x `width`, which are the other key/value pairs in the dictionary.

        Notes
        -----
        Depending on the scene being viewed, the sensor may return a large proportion of
        unknown values as `None`.

        """
        endpoint = 'cameras/depth'
        return self.wrapper_get(endpoint)

    def take_fisheye_picture(self):
        """Take a picture using Misty's Occipital Structure Core depth sensor.

        Returns the data for a 480 x 640 png image. This can be written to a file or be
        further processed.

        """
        endpoint = 'cameras/fisheye?Base64=true'
        data = self.wrapper_get(endpoint)
        return base64.b64decode(data['base64'])

class NavigationMixin(MappingMixin, TrackingMixin, SlamSettingsMixin):
    """Provide an interface to Misty's navigation capabilities."""
    def __init__(self, ip):
        super().__init__(ip)
