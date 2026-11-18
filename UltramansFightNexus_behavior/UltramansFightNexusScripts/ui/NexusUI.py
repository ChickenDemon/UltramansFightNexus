# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

from .. import (CLIENT_HEROS_DATA_KEY, FIGHT_INFO_UI_NAME, FRONT_SCRIPTS_NAME,
                HERO_KEY, PERSON_HEROS_DATA_KEY, PERSON_POS_DATA_KEY)
from ..QuModLibs.Client import Call, compFactory, levelId, playerId
from ..QuModLibs.Modules.UI.EnhancedUI import QEScreenNode

compFactory = clientApi.GetEngineCompFactory()


class _InactiveSkillSlot(object):
    """Index-preserving placeholder; creates no widget, key binding, or visible button."""
    def __init__(self):
        self.cdCount = '0.0'

    def resetForUIReuse(self):
        self.cdCount = '0.0'

    def setVisible(self, visible):
        pass

    def setSize(self, size):
        pass

    def setPosition(self, pos):
        pass

    def Update(self):
        pass


class NexusUI(QEScreenNode):
    def __init__(self, namespace, name, param):
        QEScreenNode.__init__(self, namespace, name, param)
        self.UIName = 'nexusUI'
        self.heroKey = HERO_KEY
        self.selectedFormIndex = 0
        self.skillsCtrl = None
        self.screenPanelCtrl = None
        self.skillsList = []
        self.skillsData = []
        self.selectedHeroData = None
        self.myKeyboardDict = {}
        self.keyboardDict = None
        self.playerTempVarManager = None
        self.uiUtil = None
        self.frontClient = None
        self.wrappedExtraKey = None
        self.isShowingBtn = False
        self._uiSuspended = False
        self._uiSession = 0
        self._primaryInputDown = False
        self._layoutSize = None
        self.serverSetting = None
        self.inputDeadzone = 0.001
        self.hasFeatherSkill = False
        self._rescueDown = False
        self.hasRescueSkill = False
        self.hasPalmSkill = False
        self.hasShieldSkill = False
        self.hasPhantomSkill = False
        self.hasSpinKickSkill = False
        self.hasCrossStorm = False
        self.hasParrySkill = False
        self._palmInputDown = False

    def Create(self):
        QEScreenNode.Create(self)
        frontModule = clientApi.ImportModule(FRONT_SCRIPTS_NAME)
        self.playerTempVarManager = getattr(frontModule, 'playerTempVarManager')
        self.keyboardDict = getattr(frontModule, 'keyboardDict')
        self.wrappedExtraKey = getattr(frontModule, 'wrappedExtraKey')
        self.uiUtil = clientApi.ImportModule(FRONT_SCRIPTS_NAME + '.ClientUtil')
        fightInfoModule = clientApi.ImportModule(FRONT_SCRIPTS_NAME + '.ui.FightInfoUI')
        self.inputDeadzone = getattr(fightInfoModule, 'FLIGHT_SPRINT_INPUT_EPSILON')
        self.frontClient = clientApi.ImportModule(FRONT_SCRIPTS_NAME + '.QuModLibs.Client')
        self.skillsCtrl = self.GetBaseUIControl('/skills')
        self.screenPanelCtrl = self.GetBaseUIControl('/screenPanel')
        self.loadTransformSkills()

    def loadTransformSkills(self):
        for oldButton in self.skillsList:
            destroy = getattr(oldButton, 'Destroy', None)
            if destroy:
                destroy()
        self.skillsList = []
        self.myKeyboardDict = {}
        self.isShowingBtn = False
        self._primaryInputDown = False
        self.hasFeatherSkill = False
        self.hasRescueSkill = False
        self.hasPalmSkill = False
        self.hasShieldSkill = False
        self.hasPhantomSkill = False
        self.hasSpinKickSkill = False
        self.hasCrossStorm = False
        self.hasParrySkill = False
        self._palmInputDown = False
        self._loadSelectedSkillData()
        if not self.skillsData or not self.skillsCtrl:
            return
        commonSkillBtnModule = clientApi.ImportModule(FRONT_SCRIPTS_NAME + '.ui.CommonSkillBtn')
        CommonSkillBtn = getattr(commonSkillBtnModule, 'CommonSkillBtn')
        activeIndexes = self._getActiveSkillIndexes()
        self._createSkillButtons(CommonSkillBtn, activeIndexes)
        self.uiUtil.updateDefaultSkillLayout(self, True)
        gameComp = compFactory.CreateGame(levelId)
        gameComp.AddTimer(0.5, self.uiUtil.activeTransformCallback(self, self.showBtns))

    def _loadSelectedSkillData(self):
        configComp = compFactory.CreateConfigClient(levelId)
        data = configComp.GetConfigData(
            self.wrappedExtraKey(PERSON_HEROS_DATA_KEY), True) if configComp else None
        heroes = data.get(CLIENT_HEROS_DATA_KEY, []) if isinstance(data, dict) else []
        for hero in heroes:
            if hero.get('key') == self.heroKey:
                self.selectedHeroData = hero
                forms = hero.get('forms', [])
                if forms:
                    self.skillsData = forms[0].get('skills', [])
                break

    def _getActiveSkillIndexes(self):
        activeIndexes = set((0, 5))
        palmData = self.skillsData[6] if len(self.skillsData) > 6 else None
        if isinstance(palmData, dict) and palmData.get('key') == 'skill6':
            activeIndexes.add(6)
            self.hasPalmSkill = True
        featherData = self.skillsData[7] if len(self.skillsData) > 7 else None
        if isinstance(featherData, dict) and featherData.get('key') == 'skill7':
            activeIndexes.add(7)
            self.hasFeatherSkill = True
        shieldData = self.skillsData[8] if len(self.skillsData) > 8 else None
        if isinstance(shieldData, dict) and shieldData.get('key') == 'skill8':
            activeIndexes.add(8)
            self.hasShieldSkill = True
        phantomData = self.skillsData[9] if len(self.skillsData) > 9 else None
        if isinstance(phantomData, dict) and phantomData.get('key') == 'skill9':
            activeIndexes.add(9)
            self.hasPhantomSkill = True
        parryData = self.skillsData[10] if len(self.skillsData) > 10 else None
        if isinstance(parryData, dict) and parryData.get('key') == 'skill10':
            activeIndexes.add(10)
            self.hasParrySkill = True
        spinKickData = self.skillsData[11] if len(self.skillsData) > 11 else None
        if isinstance(spinKickData, dict) and spinKickData.get('key') == 'skill11':
            activeIndexes.add(11)
            self.hasSpinKickSkill = True
        rescueData = self.skillsData[12] if len(self.skillsData) > 12 else None
        if isinstance(rescueData, dict) and rescueData.get('key') == 'skill12':
            activeIndexes.add(12)
            self.hasRescueSkill = True
        self.hasCrossStorm = len(self.skillsData) > 13 and self.skillsData[13].get('key') == 'skill13'
        if self.hasCrossStorm:
            activeIndexes.add(13)
        return activeIndexes

    def _createSkillButtons(self, CommonSkillBtn, activeIndexes):
        for index, data in enumerate(self.skillsData[:14]):
            if index not in activeIndexes and index not in (1, 2, 3, 4, 5):
                self.skillsList.append(_InactiveSkillSlot())
                continue

            btn = CommonSkillBtn()
            btn.create('skill{}'.format(index), self.skillsCtrl, self, index, False,
                       index not in (1, 2, 3, 4))
            btn.childSkillsData = []
            btn.canRotationViewAngle = (index == 5)
            # 捕获时服务端已开启冷却，第二次点击仍需送达；只有服务器可决定进入拉拽或掌劈。
            btn.canLongPressInCD = index in (9, 12)
            btn.setVisible(index == 0)
            btn.setKeyboardVisible(False)
            keyboard = data.get('keyboard')
            if index in activeIndexes and keyboard is not None:
                self.myKeyboardDict[str(keyboard)] = index

            if index in activeIndexes:
                pos, size = self.uiUtil.resolveSkillButtonLayout(self, index)
                btn.setPosition(pos)
                btn.setSize(size)
                btn.setOpacity(data.get('opacity', 1.0))
                image = data.get('imgPath')
                if image:
                    btn.setImg(image)

                if self.isPC() and keyboard is not None and self.keyboardDict:
                    label = self.keyboardDict.get(str(keyboard), {}).get('label')
                    btn.setKeyboard(label or '')
                btn.setLayer(200 if index == 0 else 150)
            else:
                btn.setVisible(False)
                btn.setSize((0, 0))

            self.skillsList.append(btn)

    def currentSkillList(self):
        return self.skillsList

    def suspendForTransform(self):
        self._releaseRescue(cancel=True, source='suspendForTransform')

        self.uiUtil.suspendTransformSkills(self)

    def resumeForTransform(self, formIndex=0):
        self.selectedFormIndex = 0
        self._uiSuspended = False
        self._uiSession += 1
        self.SetScreenVisible(True)
        self.selectedHeroData = None
        self.skillsData = []
        self.loadTransformSkills()

    def beforeClosing(self):
        self._cancelPrimaryInput()
        self.hideBtns()

    def Destroy(self):
        self._releaseRescue(cancel=True, source='Destroy')

        if not self._uiSuspended:
            self.beforeClosing()
        self._uiSuspended = True
        self._uiSession += 1
        QEScreenNode.Destroy(self)

    def isPC(self):
        return clientApi.GetPlatform() == 0

    def isMobile(self):
        return clientApi.GetPlatform() != 0

    def _sendPrimaryAction(self, action):
        intent = {'playerId': playerId, 'action': action}
        if action == 'press':
            camera = compFactory.CreateCamera(levelId)
            origin = self.uiUtil.getCameraAimOrigin(camera) if camera else None
            forward = camera.GetForward() if camera else None
            if origin is not None and forward is not None:
                intent.update(aimCameraPos=origin, aimCameraForward=forward)

        self.frontClient.Call('NexusCombatInput', intent)

    def _sendPalmAction(self, action):
        self.frontClient.Call('NexusPalmInput',
                              {'playerId': playerId, 'action': action})

    def _cancelPalmInput(self):
        if self._palmInputDown:
            self._palmInputDown = False
            self._sendPalmAction('cancel')

    def _featherDirection(self):
        """Map the live (left/right, forward/back) movement vector to the server enum."""
        motionComp = compFactory.CreateActorMotion(playerId)
        inputVec = motionComp.GetInputVector() if motionComp else None
        if not isinstance(inputVec, (tuple, list)) or len(inputVec) < 2:
            return 0
        side = float(inputVec[0])
        forward = float(inputVec[1])
        # Match shared flight/roll input deadzone; dominant axis resolves diagonals.
        deadzone = float(self.inputDeadzone)
        if abs(side) <= deadzone and abs(forward) <= deadzone:
            return 0
        if abs(forward) >= abs(side):
            return 1 if forward > deadzone else 2
        return 3 if side > deadzone else 4

    def _sendFeather(self):
        self.frontClient.Call('NexusFeatherInput', {
            'playerId': playerId,
            'direction': int(self._featherDirection()),
        })

    def _releasePrimaryInput(self):
        if self._primaryInputDown:
            self._primaryInputDown = False
            self._sendPrimaryAction('release')

    def _cancelPrimaryInput(self):
        if self._primaryInputDown:
            self._primaryInputDown = False
            self._sendPrimaryAction('cancel')
        self._cancelPalmInput()

    def _sampleRescueAim(self):
        camera = compFactory.CreateCamera(levelId)
        origin = self.uiUtil.getCameraAimOrigin(camera) if camera else None
        forward = camera.GetForward() if camera else None
        if origin is not None and forward is not None:
            self.frontClient.Call('UpdateSkillMoveAim', dict(playerId=playerId, aimCameraPos=origin,
                                                            aimCameraForward=forward))

    def _releaseRescue(self, cancel=False, source='release'):
        if self._rescueDown:
            self._rescueDown = False
            if not cancel:
                self._sampleRescueAim()
            print '[NEXUS-RESCUE-INPUT] phase=end cancel={} source={}'.format(cancel,source)
            self.frontClient.Call('NexusCombatInput', {'playerId': playerId, 'action': 'rescue_cancel' if cancel else 'rescue_release'})

    def touchDownCommonSkillBtn(self, index):
        if index == 12 and self.hasRescueSkill and not self._uiSuspended and not self._rescueDown:
            self._rescueDown = True
            self._sampleRescueAim()
            print '[NEXUS-RESCUE-INPUT] phase=down'
            self.frontClient.Call('NexusCombatInput', {'playerId': playerId, 'action': 'rescue'})
            return

        if index == 5 and not self._uiSuspended and not self._primaryInputDown:
            self._primaryInputDown = True
            self._sendPrimaryAction('press')
        elif index == 6 and self.hasPalmSkill and not self._uiSuspended and not self._palmInputDown:
            self._palmInputDown = True
            self._sendPalmAction('press')

    def touchUpCommonSkillBtn(self, index):
        if self._uiSuspended:
            return
        if index == 0:
            button = self.skillsList[0] if self.skillsList else None
            if button and float(button.cdCount) <= 0:
                button.setSkillCDStart('0.2', False)
                if self.isShowingBtn:
                    self.hideBtns()
                else:
                    self.showBtns()
            return
        if index == 5:
            self._releasePrimaryInput()
            return
        if index == 6:
            if self._palmInputDown:
                self._palmInputDown = False
                self._sendPalmAction('release')
            return
        if index == 7 and self.hasFeatherSkill:
            self._sendFeather()
        if index == 8 and self.hasShieldSkill:
            self.frontClient.Call('NexusCombatInput', {'playerId': playerId, 'action': 'shield'})
        if index == 9 and self.hasPhantomSkill:
            self.frontClient.Call('NexusCombatInput', {'playerId': playerId, 'action': 'phantom'})
        if index == 10 and self.hasParrySkill:
            self.frontClient.Call('NexusCombatInput', {'playerId': playerId, 'action': 'parry'})
        if index == 11 and self.hasSpinKickSkill:
            print '[NEXUS-SPIN] phase=button_release entity={}'.format(playerId)
            self.frontClient.Call('NexusCombatInput', {'playerId': playerId, 'action': 'spin_kick'})
        if index == 13 and self.hasCrossStorm:
            self.frontClient.Call('NexusCombatInput', {'playerId': playerId, 'action': 'cross_storm'})
        if index == 12:
            self._releaseRescue()

    def touchCancelCommonSkillBtn(self, index):
        if index == 12:
            self._releaseRescue(cancel=True, source='touchCancelCommonSkillBtn')

        if index == 5:
            self._cancelPrimaryInput()
        elif index == 6:
            self._cancelPalmInput()

    def pressedEndCommonSkillBtn(self, index):
        if index == 12:
            self._releaseRescue(cancel=True, source='pressedEndCommonSkillBtn')

    def longPressedStartCommonSkillBtn(self, index):
        pass

    def dragStartCommonSkillBtn(self, index):
        pass

    def isPressingCommonSkillBtn(self, index):
        pass

    @QEScreenNode.Listen('OnKeyPressInGame')
    def OnKeyPressInGame(self, args):
        if self._rescueDown and str(args.get('isDown')) == '0' and self.myKeyboardDict.get(str(args.get('key'))) == 12:
            self._releaseRescue(cancel=self._uiSuspended or clientApi.GetTopUI() != 'hud_screen')
        if self._uiSuspended or clientApi.GetTopUI() != 'hud_screen' or not self.skillsList:
            return
        if args.get('screenName') != 'hud_screen':
            return
        btnIndex = self.myKeyboardDict.get(str(args.get('key')))
        if btnIndex not in (0, 5, 6, 7, 8, 9, 10, 11, 12, 13) or (btnIndex in (5, 6, 7, 8, 9, 10, 11, 12, 13) and not self.isShowingBtn):
            return
        button = self.skillsList[btnIndex]
        if str(args.get('isDown')) == '1':
            button.touchDownCommonSkillBtn({})
        elif str(args.get('isDown')) == '0':
            button.touchUpCommonSkillBtn({})

    def showBtns(self):
        if self._uiSuspended or not self.skillsData or len(self.skillsList) <= 5:
            return
        self.isShowingBtn = True
        fightInfoUI = self.playerTempVarManager.getPlayerVar(playerId, FIGHT_INFO_UI_NAME)
        if fightInfoUI:
            fightInfoUI.showCommonBtns(True)
        primaryBtn = self.skillsList[5]
        primaryBtn.setVisible(True)
        pos, size = self.uiUtil.resolveSkillButtonLayout(self, 5)
        primaryBtn.setPosition(pos)
        primaryBtn.setSize(size)
        if self.isPC():
            primaryBtn.setKeyboardVisible(True)
        for index, enabled in ((6, self.hasPalmSkill), (8, self.hasShieldSkill),
                               (9, self.hasPhantomSkill), (10, self.hasParrySkill),
                               (11, self.hasSpinKickSkill), (13, self.hasCrossStorm)):
            if not enabled:
                continue
            button = self.skillsList[index]
            button.setVisible(True)
            pos, size = self.uiUtil.resolveSkillButtonLayout(self, index)
            button.setPosition(pos)
            button.setSize(size)
            if self.isPC():
                button.setKeyboardVisible(True)
        if self.hasFeatherSkill and len(self.skillsList) > 7 and hasattr(self.skillsList[7], 'setVisible'):
            featherBtn = self.skillsList[7]
            featherBtn.setVisible(True)
            pos, size = self.uiUtil.resolveSkillButtonLayout(self, 7)
            featherBtn.setPosition(pos)
            featherBtn.setSize(size)
            if self.isPC():
                featherBtn.setKeyboardVisible(True)
        if self.hasRescueSkill and len(self.skillsList) > 12:
            rescueBtn = self.skillsList[12]
            rescueBtn.setVisible(True)
            pos, size = self.uiUtil.resolveSkillButtonLayout(self, 12)
            rescueBtn.setPosition(pos)
            rescueBtn.setSize(size)
            if self.isPC():
                rescueBtn.setKeyboardVisible(True)

    def hideBtns(self):
        self._releaseRescue(cancel=True, source='hideBtns')

        self._cancelPrimaryInput()
        wasShowing = self.isShowingBtn
        self.isShowingBtn = False
        if self.skillsList and len(self.skillsList) > 5:
            primaryBtn = self.skillsList[5]
            primaryBtn.setVisible(False)
            if self.isPC():
                primaryBtn.setKeyboardVisible(False)
            pos, size = self.uiUtil.resolveSkillButtonLayout(self, 0)
            primarySize = primaryBtn.getSize()
            collapsed = (pos[0] + (size[0] - primarySize[0]) / 2.0,
                         pos[1] + (size[1] - primarySize[1]) / 2.0)
            primaryBtn.setPosition(collapsed)
        if self.hasFeatherSkill and len(self.skillsList) > 7 and hasattr(self.skillsList[7], 'setVisible'):
            featherBtn = self.skillsList[7]
            featherBtn.setVisible(False)
            if self.isPC():
                featherBtn.setKeyboardVisible(False)
            if self.uiUtil:
                pos, size = self.uiUtil.resolveSkillButtonLayout(self, 0)
                btnSize = featherBtn.getSize()
                featherBtn.setPosition((pos[0] + (size[0] - btnSize[0]) / 2.0,
                                        pos[1] + (size[1] - btnSize[1]) / 2.0))
        if self.hasRescueSkill and len(self.skillsList) > 12:
            rescueBtn = self.skillsList[12]
            rescueBtn.setVisible(False)
            if self.isPC():
                rescueBtn.setKeyboardVisible(False)
            pos, size = self.uiUtil.resolveSkillButtonLayout(self, 0)
            btnSize = rescueBtn.getSize()
            rescueBtn.setPosition((pos[0] + (size[0] - btnSize[0]) / 2.0,
                                   pos[1] + (size[1] - btnSize[1]) / 2.0))
        for index, enabled in ((6, self.hasPalmSkill), (8, self.hasShieldSkill),
                               (9, self.hasPhantomSkill), (10, self.hasParrySkill),
                               (11, self.hasSpinKickSkill), (13, self.hasCrossStorm)):
            if not enabled:
                continue
            button = self.skillsList[index]
            button.setVisible(False)
            if self.isPC():
                button.setKeyboardVisible(False)
            pos, size = self.uiUtil.resolveSkillButtonLayout(self, 0)
            btnSize = button.getSize()
            button.setPosition((pos[0] + (size[0] - btnSize[0]) / 2.0,
                                pos[1] + (size[1] - btnSize[1]) / 2.0))
        fightInfoUI = self.playerTempVarManager.getPlayerVar(playerId, FIGHT_INFO_UI_NAME)
        if wasShowing and fightInfoUI:
            fightInfoUI.showCommonBtns(False)

    def refreshBtnsPos(self):
        if not self.skillsList or len(self.skillsList) <= 5:
            return
        self.uiUtil.updateDefaultSkillLayout(self, True)
        self.skillsList[0].setPosition(self.uiUtil.resolveSkillButtonLayout(self, 0)[0])
        self.skillsList[5].setSize(self.uiUtil.resolveSkillButtonLayout(self, 5)[1])
        if self.hasFeatherSkill and len(self.skillsList) > 7 and hasattr(self.skillsList[7], 'setSize'):
            self.skillsList[7].setSize(self.uiUtil.resolveSkillButtonLayout(self, 7)[1])
        if self.hasRescueSkill and len(self.skillsList) > 12:
            self.skillsList[12].setSize(self.uiUtil.resolveSkillButtonLayout(self, 12)[1])
        for index, enabled in ((6, self.hasPalmSkill), (8, self.hasShieldSkill),
                               (9, self.hasPhantomSkill), (10, self.hasParrySkill),
                               (11, self.hasSpinKickSkill), (13, self.hasCrossStorm)):
            if enabled and len(self.skillsList) > index:
                self.skillsList[index].setSize(self.uiUtil.resolveSkillButtonLayout(self, index)[1])
        if self.isShowingBtn:
            self.skillsList[5].setPosition(self.uiUtil.resolveSkillButtonLayout(self, 5)[0])
            if self.hasFeatherSkill and len(self.skillsList) > 7 and hasattr(self.skillsList[7], 'setPosition'):
                self.skillsList[7].setPosition(self.uiUtil.resolveSkillButtonLayout(self, 7)[0])
            if self.hasRescueSkill and len(self.skillsList) > 12:
                self.skillsList[12].setPosition(self.uiUtil.resolveSkillButtonLayout(self, 12)[0])
            for index, enabled in ((6, self.hasPalmSkill), (8, self.hasShieldSkill),
                                   (9, self.hasPhantomSkill), (10, self.hasParrySkill),
                                   (11, self.hasSpinKickSkill), (13, self.hasCrossStorm)):
                if enabled and len(self.skillsList) > index:
                    self.skillsList[index].setPosition(self.uiUtil.resolveSkillButtonLayout(self, index)[0])
        else:
            self.hideBtns()

    def setSkillCD(self, button, cd):
        if self.serverSetting and self.serverSetting.get('skillNoCooldown'):
            button.setSkillCDStart(0)
            return
        button.setSkillCDStart(str(cd))

    def setSkillBtnCooldownNoCondition(self, index, cd):
        if isinstance(index, int) and 0 <= index < len(self.skillsList):
            self.setSkillCD(self.skillsList[index], cd)

    def Update(self):
        if self._uiSuspended:
            return
        QEScreenNode.Update(self)
        for button in self.skillsList:
            button.Update()

        signature = self.skillsCtrl.GetSize() if self.skillsCtrl else None
        if signature != self._layoutSize:
            self._layoutSize = signature
            self.refreshBtnsPos()
