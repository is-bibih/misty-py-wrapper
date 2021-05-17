"""Get, set and delete Misty's audio, video and image files. The corresponding documentation
for the API can be found at https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#asset
"""

from api_wrappers import ApiWrapperMixin
import base64
import json

class AssetMixin(ApiWrapperMixin):
    def __init__(self, ip):
        super().__init__(ip)

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
            ----------
            file_name: str
                The name Misty should use to save the file
            data: str, default None
				 Base 64 audio data passed as a string (either data or file must be passed, not both)
            file: file-like object, default None
				 Audio file; valid types are .wav, .mp3, .wma and .aac (either data or file must be passed, not both)
            immediately_apply: bool, default False
				 Indicates whether Misty should play the file immediately after saving it
            overwrite_existing: bool, default False
                Indicates whether the file should overwrite any existing files with the same name
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

