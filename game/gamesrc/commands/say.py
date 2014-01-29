# -*- coding: utf-8 -*-
from django.conf import settings
from src.utils import utils, prettytable
from src.commands.default.muxcommand import MuxCommand

class CmdSay(MuxCommand):
    """
    say

    Usage:
      say <message>

    Talk to those in your current location.
    """

    key = "say"
    aliases = ['"', "'"]
    locks = "cmd:all()"

    def prepare_speech(self, speech):
        # Convert to unicode if necessary
        speech = str(speech) #.decode('utf-8')
        
        # Remove color codes
        color_codes = ['{r','{R','{g','{G','{y','{Y','{b','{B','{m','{M','{c','{C','{w','{W','{x','{X','{n']
        for code in color_codes:
            speech = speech.replace(code, "")
        
        # Upper-case first
        speech = speech[0].upper() + speech[1:]

        # Strip spaces in beginning and end
        speech = speech.strip()

        # Add period after sentence.
        chars = "abcdefghijklmnopqrstuvxyzåäö"
        if speech[-1:].lower() in chars:
            speech += "."
        
        return speech

    def func(self):
        "Run the say command"
        caller = self.caller

        if not self.args:
            caller.msg("Say what?")
            return

        speech = self.prepare_speech(self.args)
        
        # Decide action
        action = "say"
        action_others = "says"
        if speech[-1:] == '?':
            action = "ask"
            action_others = "asks"
        
        # calling the speech hook on the location
        speech = caller.location.at_say(caller, speech)

        # Feedback for the object doing the talking.
        caller.msg('You %s, "%s{n"' % (action, speech))

        # Build the string to emit to neighbors.
        emit_string = '%s %s, "%s{n"' % (str(caller.name_upper), action_others, speech) #caller.name_upper.encode('utf-8')
        caller.location.msg_contents(emit_string, exclude=caller)


class CmdSayTo(CmdSay):
    """
    sayto

    Usage:
      sayto <target> <message>
      sayto <target> = <message>

    Talk to those in your current location.
    """

    key = "sayto"
    #aliases = ['"', "'"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Say what to whom?")
            return

        if self.rhs:
            target = self.lhs
            speech = self.rhs
        else:
            # Parse input
            target = None
            speech = None
            if self.lhs:
                target = self.lhs.split(' ', 1)[0]
                if len(self.lhs.split(' ', 1)) > 1:
                    speech = self.lhs.split(' ', 1)[1]

        target_obj = self.caller.search(target, location=[self.caller, self.caller.location])
        
        if not target_obj:
            caller.msg("Could not find '%s'." % target)
            return
        
        if not speech:
            caller.msg("Say what?")
            return
        
        speech = self.prepare_speech(speech)
        
        # Decide action
        action = "say to"
        action_others = "says to"
        if speech[-1:] == '?':
            action = "ask"
            action_others = "asks"
        

        # Feedback for the object doing the talking.
        caller.msg('You %s %s, "%s{n"' % (action, str(target_obj.name), speech))

        # Build the string to emit to target.
        emit_string = '%s %s you, "%s{n"' % (str(caller.name_upper), action_others, speech) #caller.name_upper.encode('utf-8')
        target_obj.msg(emit_string)

        # Build the string to emit to neighbors.
        emit_string = '%s %s %s, "%s{n"' % (str(caller.name_upper), action_others, str(target_obj.name), speech) #caller.name_upper.encode('utf-8')
        caller.location.msg_contents(emit_string, exclude=[caller, target_obj])
        
        target_obj.at_sayto(caller, speech)
