"""Provide an interface to Misty's REST API and WebSockets.

The `Robot` object from the `misty` module provides attributes that make it 
possible to programmatically interact with the Misty API. Functionality 
is divided into modules, each of which correspond to the categories in Misty's 
documentation (https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference).
The modules provide mixin classes for the `Robot` object (to make the 
code more maintainable). The following modules have been implemented:

* Asset (in progress)
* Movement
* Navigation
* System (in progress)
* Skill management

These are still pending:

* Backpack
* Event
* Expression
* External requests
* Perception

Additionally, the module provides wrappers for GET, POST and DELETE
requests to Misty.

"""
