"""
This module ties together all the commands default Character objects have
available (i.e. IC commands). Note that some commands, such as
communication-commands are instead put on the player level, in the
Player cmdset. Player commands remain available also to Characters.
"""
from src.commands.cmdset import CmdSet
from src.commands.default import general, help, admin, system
from src.commands.default import building
from src.commands.default import batchprocess

from game.gamesrc.commands import default_exits

from game.gamesrc.commands.drop import CmdDrop
from game.gamesrc.commands.get import CmdGet
from game.gamesrc.commands.give import CmdGive
from game.gamesrc.commands.inventory import CmdInventory
from game.gamesrc.commands.say import CmdSay, CmdSayTo
from game.gamesrc.commands.open import CmdOpen
from game.gamesrc.commands.close import CmdClose
from game.gamesrc.commands.time import CmdTime
from game.gamesrc.commands.weather import CmdWeather
from game.gamesrc.commands.emote import CmdEmote
from game.gamesrc.commands.map import CmdMap
from game.gamesrc.commands.attack import CmdAttack

from game.gamesrc.commands.admin.dig import CmdDig
from game.gamesrc.commands.admin.scriptattr import CmdScriptattr
from game.gamesrc.commands.admin.script import CmdScript
from game.gamesrc.commands.admin.create import CmdCreate
from game.gamesrc.commands.admin.db import CmdDb
from game.gamesrc.commands.admin.tag import CmdTag
from game.gamesrc.commands.admin.attr import CmdAttr
from game.gamesrc.commands.admin.generate import CmdGenerate
from game.gamesrc.commands.admin.area import CmdArea
from game.gamesrc.commands.admin.room import CmdRoom

class CharacterCmdSet(CmdSet):
    """
    Implements the default command set.
    """
    key = "DefaultCharacter"
    priority = 0

    def at_cmdset_creation(self):
        "Populates the cmdset"

        # Fix for error message when walking in invalid direction
        self.add(default_exits.CmdNorth())
        self.add(default_exits.CmdNortheast())
        self.add(default_exits.CmdEast())
        self.add(default_exits.CmdSoutheast())
        self.add(default_exits.CmdSouth())
        self.add(default_exits.CmdSouthwest())
        self.add(default_exits.CmdWest())
        self.add(default_exits.CmdNorthwest())
        self.add(default_exits.CmdUp())
        self.add(default_exits.CmdDown())
        
        # The general commands
        self.add(CmdGet())
        self.add(CmdDrop())
        self.add(CmdGive())
        self.add(CmdInventory())
        self.add(CmdSay())
        self.add(CmdSayTo())
        self.add(CmdOpen())
        self.add(CmdClose())
        self.add(CmdTime())
        self.add(CmdWeather())
        self.add(CmdEmote())
        self.add(CmdMap())
        self.add(CmdAttack())
        self.add(general.CmdLook())
        #self.add(general.CmdPose())
        self.add(general.CmdNick())
        self.add(general.CmdHome())
        self.add(general.CmdAccess())

        # The help system
        self.add(help.CmdHelp())
        self.add(help.CmdSetHelp())


        # Admin commands
        self.add(admin.CmdBoot())
        self.add(admin.CmdBan())
        self.add(admin.CmdUnban())
        self.add(admin.CmdEmit())
        self.add(admin.CmdPerm())
        self.add(admin.CmdWall())

        # Building and world manipulation
        self.add(CmdDig())
        self.add(CmdScriptattr())
        self.add(CmdScript())
        self.add(CmdCreate())
        self.add(CmdDb())
        self.add(CmdTag())
        self.add(CmdAttr())
        self.add(CmdGenerate())
        self.add(CmdArea())
        self.add(CmdRoom())
        self.add(building.CmdCreate())
        self.add(building.CmdTeleport())
        self.add(building.CmdSetObjAlias())
        self.add(building.CmdListCmdSets())
        self.add(building.CmdWipe())
        #self.add(building.CmdSetAttribute())
        self.add(building.CmdName())
        self.add(building.CmdDesc())
        self.add(building.CmdCpAttr())
        self.add(building.CmdMvAttr())
        self.add(building.CmdCopy())
        self.add(building.CmdFind())
        self.add(building.CmdOpen())
        self.add(building.CmdLink())
        self.add(building.CmdUnLink())
        self.add(building.CmdDig())
        self.add(building.CmdDestroy())
        self.add(building.CmdExamine())
        self.add(building.CmdTypeclass())
        self.add(building.CmdLock())
        self.add(building.CmdSetHome())
        #self.add(building.CmdTag())

        # Batchprocessor commands
        self.add(batchprocess.CmdBatchCommands())
        self.add(batchprocess.CmdBatchCode())
