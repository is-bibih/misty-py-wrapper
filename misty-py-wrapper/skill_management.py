"""Programmatically upload, delete and run skills on Misty.
The corresponding documentation for the Misty API is at 
https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#skill-management

"""

from api_wrappers import ApiWrapperMixin

class SkillMixin(ApiWrapperMixin):
    """ Supply skill management functions. """

    def cancel_skill(self, skill: str = None):
        """Stops a specified running skill (or all running skills if no name is specified).

        Parameters
        ----------
        skill: str, default None
            Unique identifier for the skill. It is found in the `UniqueId` parameter from
            the skill's JSON meta file. If `None`, all running skills are canceled.

        """
        endpoint = 'skills/cancel'
        params = {'Skill': skill}
        self.wrapper_post(endpoint, params=params)

    def delete_skill(self, skill: str):
        """Removes the code, meta, and asset files for a skill from Misty's memory.

        Parameters
        ----------
        skill: str
            Unique identifier for the skill. It is found in the `UniqueId` parameter from
            the skill's JSON meta file.

        """
        endpoint = f'skills?Skill={skill}'
        self.wrapper_delete(endpoint)

    def get_running_skills(self):
        """Obtains a list of the skills currently running on Misty.

        Returns
        -------
        result: list
            List of dictionaries with information about the skills currently running on the
            robot. If no skills are running, the function returns an empty array. Each
            dictionary has the following key-value pairs.

            - `description`: `str` description of the skill as it appears in the meta file
            - `name`: `str` name of the skill as it appears in the meta file
            - `startupArguments`: `dict` with key-value pairs for each startup argument in
              the meta file
            - `uniqueId`: `str` unique id of the skill as it appears in the meta file

        """
        endpoint = 'skills/running'
        return self.wrapper_get(endpoint)

    def get_skills(self):
        """Obtains a list of the skills currently uploaded onto the robot.

        Returns
        -------
        result: list
            List of dictionaries with information about the skills on the
            robot. If no skills are running, the function returns an empty array. Each
            dictionary has the following key-value pairs.

            - `description`: `str` description of the skill as it appears in the meta file
            - `name`: `str` name of the skill as it appears in the meta file
            - `startupArguments`: `dict` with key-value pairs for each startup argument in
              the meta file
            - `uniqueId`: `str` unique id of the skill as it appears in the meta file

        """
        endpoint = 'skills'
        return self.wrapper_get(endpoint)

    def load_skill(self, skill: str):
        """Makes a previously uploaded skill available for the robot to run and
        updates the skill for any changes that have been made.

        Parameters
        ----------
        skill: str
            Unique identifier for the skill. It is found in the `UniqueId` parameter from
            the skill's JSON meta file.

        """
        endpoint = 'skills/load'
        params = {'Skill': skill}
        self.wrapper_post(endpoint, params)

    def reload_skills(self):
        """Makes all previously uploaded skills available for the robot to run and
        updates any skills that have been edited.

        Notes
        -----
        This function runs immediately, but there may be a significant delay before
        all the skills are fully loaded if there are many to load.

        """
        endpoint = 'skills/reload'
        self.wrapper_post(endpoint)

    def run_skill(self, skill: str, method: str = None):
        """Runs an on-robot skill previously uploaded to Misty.

        Parameters
        ----------
        skill: str
            Unique identifier for the skill. It is found in the `UniqueId` parameter from
            the skill's JSON meta file.
        method: str, default None
            If specified, `run_skill` only runs this method within the skill. If `None`,
            the whole skill is run.

        """
        endpoint = 'skills/start'
        params = {'Skill': skill, 'Method': method}
        self.wrapper_post(endpoint, params)

    def save_skill_to_robot(self,
                            filepath: object,
                            immediately_apply: bool = False,
                            overwrite_existing: bool = False):
        """Uploads a skill to the robot and makes it immediately available for
        the robot to run.

        Parameters
        ----------
        filepath: path-like
            object with a path to the zipped file that contains the two skill
            files (JS and JSON), as well as any image or audio files to associate with the
            skill.
        immediately_apply: bool, default False
            If `True`, the Misty runs the skill immediately after uploading. If `False`, the
            skill is loaded.
        overwrite_existing: bool, default False
            If `True`, any existing skill of the same name is overwritten.

        """
        endpoint = 'skills'
        params = {'ImmediatelyApply': immediately_apply, 'OverwriteExisting': overwrite_existing}
        file = open(filepath, 'rb')
        files = {'file': ('newskill.zip',
                          file,
                          'application/zip',
                          {'Expires': '0'})}
        self.wrapper_post(endpoint, params=params, files=files)
        file.close()

