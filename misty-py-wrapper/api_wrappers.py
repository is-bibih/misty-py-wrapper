from typing import Iterable, Tuple, TypeVar
import requests
import json
import websockets
import asyncio

# custom types
Property = str
Inequality = str
Value = str
Conditions = TypeVar('Conditions', Iterable[Tuple[Property, Inequality, Value]], None)

class ApiWrapperMixin:
    def __init__(self, ip):
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
        r"""Add new WebSocketStream instance to list of websocket connections.

            Parameters
            ----------
            event_type: str
                        Misty event type (see API documentation)  
            event_name: str
                        Unique identifier for connection  
            debounce: int
                      How frequently (in ms) new event data should be sent  
            return_property: str, default None
                             Property to restrict received events to (supports dot notation; e. g. "MentalState.Affect.Valence"); no restrictions if None  
            conditions: iterable of tuples, default None
                        Filters to limit the kinds of events received, in (Property, Inequality, Value) format; no restrictions if None  

                        Property: str  
                            Event property to check (see API documentation)  
                        Inequality: str  
                            Comparison operator; can be '=>', '==', '!=','>', '<', 'exists', 'empty', or 'delta'  
                        Value: str  
                            Value to check against  
        """
        ws = WebSocketStream(
            self.api_uri,
            event_type,
            event_name,
            debounce,
            return_property,
            conditions)
        self.websockets[event_name] = ws

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

