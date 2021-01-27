from api_wrappers import ApiWrapperMixin
from math import radians

class ActuatorMixin(ApiWrapperMixin):
    def __init__(self, api_url, api_uri):
        self.api_url = api_url
        self.api_uri = api_uri
        self.websockets = {}

    def position_getter(self, event_name, sensor_name):
        self.add_websocket('ActuatorPosition', event_name,
                           conditions=[('sensorName', '==', sensor_name)])
        self.websockets[event_name].subscribe()
        msg = self.websockets[event_name].get_message()
        self.websockets[event_name].unsubscribe()
        return msg['message']['value']

class Head(ActuatorMixin):
    """Provide an interface to Misty's head.

    All position getters are in degrees.

    """

    pitch_lower_bound = -40
    pitch_upper_bound = 26 
    roll_lower_bound = -40 
    roll_upper_bound = 40
    yaw_lower_bound = -81
    yaw_upper_bound = 81

    def __init__(self, api_url, api_uri):
        self.api_url = api_url
        self.api_uri = api_uri

        self.websockets = {}

    @property
    def pitch(self):
        return self.position_getter('pitch', 'Actuator_HeadPitch')

    @pitch.setter
    def pitch(self, new_pitch):
        self.move(new_pitch, self.roll, self.yaw)

    @property
    def roll(self):
        return self.position_getter('roll', 'Actuator_HeadRoll')

    @roll.setter
    def roll(self, new_roll):
        self.move(self.pitch, new_roll, self.yaw)

    @property
    def yaw(self):
        return self.position_getter('yaw', 'Actuator_HeadYaw')

    @yaw.setter
    def yaw(self, new_yaw):
        self.move(self.pitch, self.pitch, new_yaw)

    def move(self, pitch: float, roll: float, yaw: float,
                  velocity: float = 10, duration: float = None,
                  units: str = 'degrees'):
        """Move Misty's head to the given position.

        Either velocity of duration must be supplied (not both, not neither).

        Valid ranges:
            degrees:
                pitch: -40 (up) to 26 (down)
                roll: -40 (left) to 40 (right)
                yaw: -81 (right) to 81 (left)
            radians:
                pitch: -0.1662 (up) to 0.6094 (down)
                roll: -0.75 (left) to 0.75 (right)
                yaw: -1.57 (right) to 1.57 (left)
            position:
                pitch: -5 (up) to 5 (down)
                roll: -5 (left) to 5 (right)
                yaw: 5 (right) to 5 (left)

            Parameters
                pitch (float): up/down position
                roll (float): tilt ("ear to shoulder") position
                yaw (float): left/right position
                velocity (float, default 10): percentage of max velocity for movement
                duration (float, default None): time in s for duration of movement
                units (str, default 'degrees'): unit for position values ('degrees', 'radians' or 'position')
        """
        if not (bool(velocity) ^ bool(duration)):
            raise ValueError('Either velocity or duration must be provided (not both).')
        if not units in ('degrees', 'radians', 'position'):
            raise ValueError(f'Invalid argument for units {units}.'
                             + ' Possible values are "degrees", "radians",'
                             + ' and "position".')
        if units == 'degrees':
            if not self.pitch_lower_bound <= pitch <= self.pitch_upper_bound:
                raise ValueError(f'Invalid argument for pitch {pitch}'
                                 + 'with degree units')
            if not self.roll_lower_bound <= roll <= self.roll_upper_bound:
                raise ValueError(f'Invalid argument for roll {roll}'
                                 + 'with degree units')
            if not self.yaw_lower_bound <= yaw <= self.yaw_upper_bound:
                raise ValueError(f'Invalid argument for yaw {yaw}'
                                 + 'with degree units')
        elif units == 'radians':
            if not radians(self.pitch_lower_bound) <= pitch <= radians(self.pitch_upper_bound):
                raise ValueError(f'Invalid argument for pitch {pitch}'
                                 + 'with radian units')
            if not radians(self.roll_lower_bound) <= roll <= radians(self.roll_upper_bound):
                raise ValueError(f'Invalid argument for roll {roll}'
                                 + 'with radian units')
            if not radians(self.yaw_lower_bound) <= yaw <= radians(self.yaw_upper_bound):
                raise ValueError(f'Invalid argument for yaw {yaw}'
                                 + 'with radian units')
        else:
            if not -5 <= pitch <= 5:
                raise ValueError(f'Invalid argument for pitch {pitch}'
                                 + 'with radian units')
            if not -5 <= roll <= 5: 
                raise ValueError(f'Invalid argument for roll {roll}'
                                 + 'with radian units')
            if not -5 <= yaw <= 5:
                raise ValueError(f'Invalid argument for yaw {yaw}'
                                 + 'with radian units')

        endpoint = 'head'
        params = {
            'Pitch': pitch,
            'Roll': roll,
            'Yaw': yaw,
            'Velocity': velocity,
            'Duration': duration,
            'Units': units
        }
        self.wrapper_post(endpoint, params)

class Arm(ActuatorMixin):
    """Provide an interface to either of Misty's arms.

    Position value getters are in degrees.
    """

    position_lower_bound = -29
    position_upper_bound = 90

    def __init__(self, which_arm: str, api_url, api_uri):
        if not which_arm in ('left', 'right'):
            raise ValueError(f'Invalid value for which_arm {which_arm}')
        self.which_arm = which_arm
        self.api_url = api_url
        self.api_uri = api_uri
        self.websockets = {}

    @property
    def position(self):
        if self.which_arm == 'left':
            return self.position_getter('leftArm', 'Actuator_LeftArm')
        elif self.which_arm == 'right':
            return self.position_getter('rightArm', 'Actuator_RightArm')

    @position.setter
    def position(self, new_pos):
        self.move(new_pos)

    def move(self, position: float, velocity: float = 10,
             units: str = 'degrees'):
        """Move either of Misty's arms.

            Parameters
                position (float): the new position to move the arm to
                velocity (float, default 10): value from 0 to 100 to specify speed of movement
                units (str, default 'degrees'): either 'degrees', 'radians' or 'position'

            Valid ranges for position
                degrees: -29 (up) to 90 (down)
                radians: -0.50614 (up) to 1.570796 (down)
                position: -5 (up) to 5 (down)
        """
        if not units in ('degrees', 'radians', 'position'):
            raise ValueError(f'Invalid value for units {units}')
        if not 0 <= velocity <= 100:
            raise ValueError(f'Invalid value for velocity {velocity}')

        valid_position = True
        if units == 'degrees':
            if not self.position_lower_bound <= position <= self.position_upper_bound:
                valid_position = False
        elif units == 'radians':
            if not radians(self.position_lower_bound) <= position <= radians(self.position_upper_bound):
                valid_position = False
        else:
            if not -5 <= position <= 5:
                valid_position = False
        if not valid_position:
            raise ValueError(f'Invalid value for position {position} with given units {units}')

        endpoint = 'arms'
        params = {
            'Arm': self.which_arm,
            'Position': position,
            'Velocity': velocity,
            'Units': units,
        }
        self.wrapper_post(endpoint, params=params)

class BothArms(ApiWrapperMixin):
    """Provide an interface to both of Misty's arms.

    All position getters are in degrees.

    """
    def __init__(self, api_url, api_uri):
        self.api_url = api_url
        self.api_uri = api_uri
        self.left = Arm('left', api_url, api_uri)
        self.right = Arm('right', api_url, api_uri)

    @property
    def position(self):
        left_pos = self.left.position
        right_pos = self.right.position
        return {'left': left_pos, 'right': right_pos}

    def move(self,
             left_pos: float = None,
             right_pos: float = None,
             left_velocity: float = None,
             right_velocity: float = None,
             units: str = 'degrees'):
        """Move one or both of Misty's arms.

            Parameters
                left_pos (float, default None): the new position to move the left arm to
                right_pos (float, default None): the new position to move the right arm to
                left_velocity (float, default None): value from 0 to 100 to specify speed of left movement
                right_velocity (float, default None): value from 0 to 100 to specify speed of right movement
                units (str, default 'degrees'): either 'degrees', 'radians' or 'position'

            Valid ranges for left_pos and right_pos
                degrees: -29 (up) to 90 (down)
                radians: -0.50614 (up) to 1.570796 (down)
                position: -5 (up) to 5 (down)
        """
        if not units in ('degrees', 'radians', 'position'):
            raise ValueError(f'Invalid value for units {units}')
        if left_velocity and not 0 <= left_velocity <= 100:
            raise ValueError(f'Invalid value for velocity {left_velocity}')
        if right_velocity and not 0 <= right_velocity <= 100:
            raise ValueError(f'Invalid value for velocity {right_velocity}')

        if left_pos:
            valid_left = True
            if units == 'degrees':
                if not -29 <= left_pos <= 90:
                    valid_left = False
            elif units == 'radians':
                if not -0.50614 <= left_pos <= 1.570796:
                    valid_left = False
            else:
                if not -5 <= left_pos <= 5:
                    valid_left = False
            if not valid_left:
                raise ValueError(f'Invalid value for left position {left_pos} with given units {units}')

        if right_pos:
            valid_right = True
            if units == 'degrees':
                if not -29 <= right_pos <= 90:
                    valid_right = False
            elif units == 'radians':
                if not -0.50614 <= right_pos <= 1.570796:
                    valid_right = False
            else:
                if not -5 <= right_pos <= 5:
                    valid_right = False
            if not valid_right:
                raise ValueError(f'Invalid value for right position {right_pos} with given units {units}')

        endpoint = 'arms/set'
        params = {
            'LeftArmPosition': left_pos,
            'RightArmPosition': right_pos,
            'LeftArmVelocity': left_velocity,
            'RightArmVelocity': right_velocity,
            'Units': units,
        }
        self.wrapper_post(endpoint, params)

