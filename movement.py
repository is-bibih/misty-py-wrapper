
class Head:
    def __init__(self):
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.move_head(0, 0, 0)

    def move_head(self, pitch: float, roll: float, yaw: float,
                  velocity: float = 10, duration: float = None,
                  units: str = 'degrees'):
        """Moves Misty's head to the given position.

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
            if not -40 < pitch < 26:
                raise ValueError(f'Invalid argument for pitch {pitch}'
                                 + 'with degree units')
            if not -40 < roll < 40:
                raise ValueError(f'Invalid argument for roll {roll}'
                                 + 'with degree units')
            if not -81 < yaw < 81:
                raise ValueError(f'Invalid argument for yaw {yaw}'
                                 + 'with degree units')
        elif units == 'radians':
            if not -0.1662 < pitch < 0.6094:
                raise ValueError(f'Invalid argument for pitch {pitch}'
                                 + 'with radian units')
            if not -0.75 < roll < 0.75:
                raise ValueError(f'Invalid argument for roll {roll}'
                                 + 'with radian units')
            if not -1.57 < yaw < 1.57:
                raise ValueError(f'Invalid argument for yaw {yaw}'
                                 + 'with radian units')
        else:
            if not -5 < pitch < 5:
                raise ValueError(f'Invalid argument for pitch {pitch}'
                                 + 'with radian units')
            if not -5 < roll < 5: 
                raise ValueError(f'Invalid argument for roll {roll}'
                                 + 'with radian units')
            if not -5 < yaw < 5:
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

