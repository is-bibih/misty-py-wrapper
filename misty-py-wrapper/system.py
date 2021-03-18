from .api_wrappers import ApiWrapperMixin

class SystemMixin(ApiWrapperMixin):
    def __init__(self, ip):
        super().__init__(ip)

    def set_default_volume(self, volume: int = 100):
        """Sets new default volume for system audio in range [0, 100]"""
        endpoint = 'audio/volume'
        params = {'Volume': volume}
        self.wrapper_post(endpoint, params=params)

