# -*- coding: utf-8 -*-
from .QuModLibs.Server import *


def OpenSkillUIApi(args):
    Call(args['playerId'], 'OpenSkillUI', {'formIndex': int(args.get('formIndex', 0))})


def RefreshSkillUIPosApi(args):
    Call(args['playerId'], 'RefreshSkillUI', {})


def CloseSkillUIApi(args):
    Call(args['playerId'], 'CloseSkillUI', {})
