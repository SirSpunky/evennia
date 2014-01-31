Evennia
-----------------------
*Evennia* is an open-source Python-based MUD/MU\* server/codebase using modern technologies. Evennia allows creators to design and flesh out text-based massively-multiplayer online games with great freedom.

http://www.evennia.com is the main hub tracking all things Evennia. The documentation wiki is found [here](https://github.com/evennia/evennia/wiki).

SirSpunky's MUD
-----------------------
Heavily based on the Evennia codebase, *SirSpunky's [MUD](http://en.wikipedia.org/wiki/MUD)* aims to provide a complete text-based game engine in a fantasy setting with powerful in-game building tools for building the game world and objects.

Screenshots: http://imgur.com/a/uN5mB#0

**Feature list**
* Rooms
    * Exits optimized for north, east, south, west, up and down for easier orientation.
    * Coordinates (x, y and z) have been added to rooms for extra functionality.
    * In-game map using the "map" command.
    * Custom formatting of room descriptions when using the "look" command, including an optional mini-map.
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

**Todo:** A lot.

Installation
-----------------------
Follow the instructions at https://github.com/evennia/evennia/wiki/Getting-Started but use "SirSpunky/evennia.git" instead of "evennia/evennia.git". The settings file is already included, but you should change the secret key to something unique.

Attributes & tags
-----------------------
**Attributes**
* desc: Description
* weight: Base weight in kg. Used by all objects. Defaults to 0, which means transparent or infinite, i.e. can never be picked up. Total weight is automatically calculated based on weight and its contents weight.
* max_contents_weight: Max contents weight in kg. If > 0, is a container. For characters, this sets their inventory size.
* *Rooms*
    * x, y and z: These three attributes decide the position of the room, and makes commands like ".dig" easier to use. Should be set to 0, 0, 0 on the initial room and is then updated automatically. Is required for the "map" command to work.
* *Scripts*
    * random_messages: A list of random messages. Use "/" to execute command instead, e.g. "/say Hello!" to make a character speak at random. The string "$random_character" will be replaced by the name of a random character in the room.
    * random_message_rate: 0-1. Higher means messages will appear more often.
    * random_movement_rate: 0-1. If > 0, object will move around randomly. Higher means it will move more often.
    * speech: Speech keywords mapped to answers triggered by using "sayto <character> <keyword>". Example: (('hello', 'Hello there!'), ('bye', 'Good bye, my friend.'))

**Tags**
* can_open: Object can be opened or closed. Mainly for objects and exits.
* *Rooms*
    * outdoors: Room is outdoors, so commands like "weather" and "time" can be used.
* *Characters*
    * hide_on_unpuppet: Character is hidden when player logs out/unpuppets it. Used on player-created characters.
