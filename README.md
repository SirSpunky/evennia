Evennia
-----------------------
*Evennia* is an open-source Python-based MUD/MU\* server/codebase using modern technologies. Evennia allows creators to design and flesh out text-based massively-multiplayer online games with great freedom.

http://www.evennia.com is the main hub tracking all things Evennia. The documentation wiki is found [here](https://github.com/evennia/evennia/wiki).

SirSpunky's MUD
-----------------------
SirSpunky's MUD is heavily based on the Evennia code base. The goal is to build a complete text-based game engine in a fantasy setting with powerful in-game building tools for building the game world and objects.

Screenshots: http://imgur.com/a/B9sfo#0

Feature list:
* Rooms
    * Exits optimized for north, east, south, west, up and down for easier orientation.
    * Coordinates (x, y and z) have been added to rooms for additional functionality.
    * In-game map using the "map" command.
    * Custom formatting of room descriptions when using the "look" command, including a mini-map.
* Objects
    * Weight-based object and container system. Containers can contain any levels of sub-containers and objects, as long as they haven't reached their maximum contents weight.
    * Containers and exits support opening and closing, to create things like chests and doors.
* Global weather and time system with random levels of clouds density, wind speed and precipitation. Time is shown through descriptions of the sun position rather than by printing time.
* Commands
    * Prefix for admin commands changed to "." for easier typing.
* Building:
    * In-game object database for storing and spawning common objects and characters. See the ".db" command.
    * Random generation of whole areas using the ".generate" command. Random areas are setup through the ".area" command, using rooms defined with the ".room" command.
    * Common scripts such as random movement and random messages are configured through normal attributes on objects and characters.
    * Includes speech script triggered by keywords that can also be configured through attributes.
    * Common scripts can include keywords such as $random_character, which will automatically select a character in the same room by random, allowing your NPC:s to address or target random characters in speech or actions.

Todo:
A lot.
