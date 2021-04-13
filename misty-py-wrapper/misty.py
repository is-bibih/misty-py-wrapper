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

