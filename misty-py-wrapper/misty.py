from api_wrappers import ApiWrapperMixin
from asset import AssetMixin
from system import SystemMixin
from movement import Head, BothArms, DrivingMixin
from navigation import NavigationMixin
from typing import List
from io import BytesIO
import gtts

class Robot(NavigationMixin, DrivingMixin, SystemMixin, AssetMixin, ApiWrapperMixin):
    """Provide an interface to the Misty API and text-to-speech.

    """
    def __init__(self, ip: str):
        """Initialize Robot instance."""
        super().__init__(ip)
        self.head = Head(ip)
        self.arms = BothArms(ip)

    def add_touch_sensor(self, event_name,
                         sensor_position: List[str] = None, **kwargs):
        """Adds a touch sensor WebSocket connection to the given sensor positions."""
        sensors = ['Chin', 'HeadLeft', 'HeadRight', 'HeadBack', 'HeadFront', 'Scruff']
        if not sensor_position:
            conditions = None
        # if only one sensor
        elif isinstance(sensor_position, str):
            if sensor_position in sensors:
                conditions = [('sensorPosition', '==', sensor_position)]
            else:
                raise ValueError(f'Invalid sensor position {sensor_position}')
        # if more than one sensor
        else:
            exclude_sensors = sensors.copy()
            for sensor in sensor_position:
                if not sensor in sensors:
                    raise ValueError(f'Invalid sensor position {sensor}')
                else:
                    exclude_sensors.remove(sensor)
            conditions = [('sensorPosition', '!=', sensor) \
                          for sensor in exclude_sensors]
        self.add_websocket('TouchSensor', event_name, conditions=conditions, **kwargs)

    def add_hazard_notification(self, event_name: str,
                                hazard_type: List[str] = None, **kwargs):
        """Add a WebSocket connection to receive hazard notification event messages.

        Misty sends event messages each time the hazard system detects a change to a
        hazard state. You can subscribe to these events to be
        notified when Misty enters or exits a specific hazard state.

        Parameters
        ----------
        event_name: str
            Unique identifier for the subscription to hazard notification events.
        hazard_type: list of str, default None
            List with hazard event types to subscribe to. May be one of the
            following (check Misty documentation at
            https://docs.mistyrobotics.com/misty-ii/robot/sensor-data/#hazardnotification
            for details):

            - `bumpSensorsHazardState`
            - `criticalInternalError`
            - `driveStopped`
            - `timeOfFlightSensorsHazardState`
            - `excessiveSpeedHazard`

            If no hazard event types are passed, the event subscription returns
            information from all types.

        """

        hazards = ['bumpSensorsHazardState', 'criticalInternalError', 'driveStopped'
                   'timeOfFlightSensorsHazardState', 'excessiveSpeedHazard']
        if not hazard_type:
            conditions = None
        # if only one type 
        elif isinstance(hazard_type, str):
            if hazard_type in hazards:
                conditions = [('Hazard', '==', hazard_type)]
            else:
                raise ValueError(f'Invalid hazard type {hazard_type}')
        # if more than one type
        else:
            exclude_hazards = hazards.copy()
            for hazard in hazard_type:
                if not hazard in hazards:
                    raise ValueError(f'Invalid hazard type {hazard}')
                else:
                    exclude_hazards.remove(hazard)
            conditions = [('Hazard', '!=', hazard) \
                          for hazard in exclude_hazards]
        self.add_websocket('HazardNotification', event_name, conditions=conditions, **kwargs)

    def add_imu(self, event_name, **kwargs):
        """Provide  information from Misty's IMU sensor.

        This WebSocket stream includes information about:

        - the pitch, yaw, and roll orientation angles of the sensor (in degrees)
        - the force (in meters per second) currently applied to the sensor along
          its pitch, yaw, and roll rotational axes
        - the force (in meters per second squared) currently applied to the
          sensor along its X, Y, and Z axes

        Parameters
        ----------
        event_name: str
            Unique identifier for the subscription to the IMU sensor data stream.

        Notes
        -----
        Whenever Misty boots up or resets the real-time controller, the IMU
        defines that position to be a heading of 0 degrees. The IMU is located
        in Misty's torso, so the relative position of Misty's head does not
        change readings.

        By default, Misty sends IMU events every five seconds. Pass a `debounce`
        keyword argument with a different value (in ms) to change it.

        """
        self.add_websocket('IMU', event_name, **kwargs)

    def add_slam_status(self, event_name, **kwargs):
        """Provide information about the SLAM system's status.

        It returns a dictionary with `status`, `statusList`, `runMode`, and
        `sensorStatus`.

        - `status`: an integer which, when converted to binary, represents whether
          each status code for the SLAM system is on (1) or off (0)
        - `statusList`: a list of the status codes which are in the 'on' state
        - `runMode`: represents which task the navigation system is currently
          carrying out (tracking, exploring, etc.)
        - `sensorStatus`: describes the status of the depth sensor

        See the Misty documentation for details:
        https://docs.mistyrobotics.com/misty-ii/robot/sensor-data/#slamstatus

        Parameters
        ----------
        event_name: str
            Unique identifier for the subscription to the IMU sensor data stream.

        Notes
        -----
        It is recommended to only use returned `SensorStatus` and `RunMode` as
        supplemental information if coding SLAM functionality, and focus on 
        `Status` and `StatusList`.
        """
        self.add_websocket('SlamStatus', event_name, **kwargs)

    def text_to_speech(self, msg: str, lang: str = 'es',
                           file_name: str = 'temp.mp3',
                       delete_after: bool = True, **kwargs):
        """Generate speech audio from text and play it in Misty."""
        file_obj = BytesIO()
        sound = gtts.gTTS(msg, lang=lang, **kwargs)
        sound.write_to_fp(file_obj)
        self.save_audio(file_name, file=file_obj,
                        immediately_apply=True, overwrite_existing=True)
        if delete_after:
            self.delete_audio(file_name)

