from typing import Iterable, Tuple, TypeVar, List
from io import BytesIO
import base64
import requests
import json
import websockets
import asyncio
import gtts

# custom types
Property = str
Inequality = str
Value = str
Conditions = TypeVar('Conditions', Iterable[Tuple[Property, Inequality, Value]], None)

class Robot:
    """Provide an interface to the Misty API and text-to-speech.

    """
    def __init__(self, ip: str):
        """Initialize Robot instance."""
        self.ip = ip
        self.api_url = 'http://' + ip + '/api/'
        self.api_uri = 'ws://' + ip + '/pubsub'

        self.websockets = {}

    def add_websocket(
        self,
        event_type: str,
        event_name: str,
        debounce: int = 250,
        return_property: str = None,
        conditions: Conditions = None):
        """Add new WebSocketStream instance to list of websocket connections.

            Parameters:
                event_type (str): Misty event type (see API documentation)
                event_name (str): Unique identifier for connection
                debounce (int): How frequently (in ms) new event data should be sent
                return_property (str, default None): Property to restrict received events to (supports dot notation; e. g. "MentalState.Affect.Valence"); no restrictions if None
                conditions (iterable of tuples, default None): Filters to limit the kinds of events received, in (Property, Inequality, Value) format; no restrictions if None
                    Property (str): Event property to check (see API documentation)
                    Inequality (str): Comparison operator; can be '=>', '==', '!=','>', '<', 'exists', 'empty', or 'delta'
                    Value (str): Value to check against

        """
        ws = WebSocketStream(
            self.api_uri,
            event_type,
            event_name,
            debounce,
            return_property,
            conditions)
        self.websockets[event_name] = ws

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

    def wrapper_get(self, endpoint, params=None, timeout_ms=10000):
        """Do GET requests for the given endpoint."""
        url = self.api_url + endpoint
        resp = requests.get(url, params=params, timeout=timeout_ms).json()
        if resp['status'] == 'Success':
            return resp['result']
        else:
            raise Exception(resp['error'])

    def wrapper_post(self, endpoint, params=None, timeout_ms=10000):
        """Do POST requests for the given endpoint."""
        url = self.api_url + endpoint
        resp = requests.post(url, json=params, timeout=timeout_ms).json()
        if resp['status'] == 'Failed':
            raise Exception(resp['error'])

    def wrapper_delete(self, endpoint, params=None, timeout_ms=10000):
        """Do DELETE requests for the given endpoint."""
        url = self.api_url + endpoint
        resp = requests.delete(url, json=params, timeout=timeout_ms).json()
        if resp['status'] == 'Failed':
            raise Exception(resp)

    def set_default_volume(self, volume: int = 100):
        """Sets new default volume for system audio in range [0, 100]"""
        endpoint = 'audio/volume'
        params = {'Volume': volume}
        self.wrapper_post(endpoint, params=params)

    def get_audio_list(self):
        """Get list of Misty's saved audio files."""
        endpoint = 'audio/list'
        audio_dicts= self.wrapper_get(endpoint)
        audio_list = [file['name'] for file in audio_dicts]
        return audio_list

    def save_audio(self, file_name: str, data: str = None, file: object = None,
                   immediately_apply: bool = False, overwrite_existing: bool = False):
        """Saves either audio data string or audio file to Misty.

            Parameters
                file_name (str): The name Misty should use to save the file
                data (str, default None): Base 64 audio data passed as a string (either data or file must be passed, not both)
                file (file-like object, default None): Audio file; valid types are .wav, .mp3, .wma and .aac (either data or file must be passed, not both)
                immediately_apply (bool, default False): Indicates whether Misty should play the file immediately after saving it
                overwrite_existing (bool, default False): Indicates whether the file should overwrite any existing files with the same name
        """
        if data and file:
            raise Exception('Only one of data and file parameters may be used')
        endpoint = 'audio'
        # try as pathlike
        try:
            with open(file, 'rb') as f:
                file_bytes = f.read()
        # try as bytes
        except TypeError:
            file_bytes = file.getvalue()
        encoded_string = base64.b64encode(file_bytes).decode('ascii')
        data = encoded_string
        params = json.dumps({
            'FileName': file_name,
            'Data': data,
            'ImmediatelyApply': immediately_apply,
            'OverwriteExisting': overwrite_existing,
        })
        self.wrapper_post(endpoint, params=params)

    def delete_audio(self, file_name: str):
        """Delete previously uploaded audio file."""
        endpoint = 'audio'
        params = json.dumps({'FileName': file_name})
        self.wrapper_delete(endpoint, params=params)

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

class WebSocketStream:
    """Provide information about a Misty WebSocket connection stream.

    """
    def __init__(
        self,
        uri: str,
        event_type: str,
        event_name: str,
        debounce: int = 250,
        return_property: str = None,
        conditions: Conditions = None
    ):
        """Initialize WebSocketStream instance."""

        self.uri = uri
        self.websocket = None
        # see documentation on event types:
        # https://docs.mistyrobotics.com/misty-ii/robot/sensor-data
        self.event_type = event_type 
        # values for subscription
        self.event_name = event_name
        self.debounce = debounce
        self.return_property = return_property
        self.conditions = self.generate_event_conditions(conditions)

    def generate_event_conditions(self, conditions: Conditions):
        """Generate event conditions list"""
        if not conditions:
            return None
        cond_dicts = [{'Property': p, 'Inequality': i, 'Value': v} for p, i, v in conditions]
        return cond_dicts

    def async_wrapper(func):
        def async_func(*args, **kwargs):
            return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))
        return async_func

    @async_wrapper
    async def subscribe(self):
        """Create subscription to WebSocket server."""
        sub_msg = json.dumps({
            'Operation':        'subscribe',
            'Type':             self.event_type,
            'DebounceMs':       self.debounce,
            'EventName':        self.event_name,
            'ReturnProperty':   self.return_property,
            'EventConditions':  self.conditions,
        })
        self.websocket = await websockets.connect(self.uri)
        await self.websocket.send(sub_msg)
        resp = await self.websocket.recv()
        if 'message' not in resp:
            raise Exception('WebSocket stream exception: ' + str(resp))

    @async_wrapper
    async def unsubscribe(self):
        """Unsubscribe from WebSocket server and end connection."""
        if not self.websocket:
            raise Exception(f'No active WebSocket subscription for {self.event_name}')
        unsub_msg = json.dumps({
            'Operation': 'unsubscribe',
            'EventName': self.event_name,
        })
        await self.websocket.send(unsub_msg)
        await self.websocket.close()

    @async_wrapper
    async def get_message(self):
        """Get message from active WebSocket subscription."""
        if not self.websocket:
            raise Exception(f'No active WebSocket subscription for {self.event_name}')
        msg = await self.websocket.recv()
        return json.loads(msg)

