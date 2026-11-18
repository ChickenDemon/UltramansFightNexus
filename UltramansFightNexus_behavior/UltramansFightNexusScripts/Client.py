# -*- coding: utf-8 -*-
from . import MOD_NAME
from .QuModLibs.Client import *
from .ui.NexusUI import NexusUI

uiName = 'nexusUI'
_skillUI = None
_playerTempVarManager = None
_skillUIName = None


@Listen(Events.UiInitFinished)
def OnUIInitFinished(args):
    clientApi.RegisterUI(MOD_NAME, uiName,
                         'UltramansFightNexusScripts.ui.NexusUI.NexusUI',
                         'nexusUI.nexusUI')


@AllowCall
def OpenSkillUI(args):
    global _skillUI, _playerTempVarManager, _skillUIName

    frontModule = clientApi.ImportModule('FrontUltramansFightScripts')
    _playerTempVarManager = getattr(frontModule, 'playerTempVarManager')
    _skillUIName = getattr(frontModule, 'SKILL_UI_NAME')
    clientApi.ImportModule('FrontUltramansFightScripts.Client').CloseSkillUIInClient({})

    _skillUI = clientApi.GetUI(MOD_NAME, uiName)
    if _skillUI:
        if not _skillUI._uiSuspended:
            _skillUI.suspendForTransform()
        _skillUI.resumeForTransform(int(args.get('formIndex', 0)))
    else:
        _skillUI = clientApi.CreateUI(
            MOD_NAME, uiName, {'isHud': 1, 'formIndex': int(args.get('formIndex', 0))})

    _playerTempVarManager.setPlayerVar(playerId, _skillUIName, _skillUI)


@AllowCall
def RefreshSkillUI(args):
    frontModule = clientApi.ImportModule('FrontUltramansFightScripts')
    varManager = getattr(frontModule, 'playerTempVarManager')
    uiKey = getattr(frontModule, 'SKILL_UI_NAME')
    uiNode = varManager.getPlayerVar(playerId, uiKey)

    if uiNode and getattr(uiNode, 'heroKey', None) == 'nexus':
        uiNode.refreshBtnsPos()


@AllowCall
def CloseSkillUI(args):
    global _skillUI

    if _skillUI:
        _skillUI.suspendForTransform()

        if _playerTempVarManager and _skillUIName and \
                _playerTempVarManager.getPlayerVar(playerId, _skillUIName) is _skillUI:
            _playerTempVarManager.setPlayerVar(playerId, _skillUIName, None)

        _skillUI = None
