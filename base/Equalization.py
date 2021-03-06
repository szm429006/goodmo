# -*- coding: utf-8 -*-
import importlib
import KBEngine
import settings
import plugins
from functools import partial
from common.dispatcher import receiver
from kbe.utils import DatabaseBaseMixin, TimerProxy
from kbe.core import Equalization as Equalization_
from kbe.protocol import Type, Base, BaseMethod
from kbe.signals import baseapp_ready, global_data_change, global_data_del, entity_auto_load_completed
from kbe.log import ERROR_MSG


class Equalization(KBEngine.Entity, TimerProxy):
    base = Base(
        addEntity=BaseMethod(Type.UNICODE, Type.PY_LIST, Type.ENTITYCALL),
        addAutoLoaded=BaseMethod(Type.UNICODE, Type.DBID),
    )

    class EqualizationBase:
        def __init__(self):
            super().__init__()
            if not Equalization_.isCompleted():
                KBEngine.globalData["EqualizationEntity"].addEntity(self.__class__.__name__, self.equalizationPath,
                                                                    self)

    class DatabaseBase(KBEngine.Entity, DatabaseBaseMixin):
        def writeToDB(self, callback=None, shouldAutoLoad=False):
            super().writeToDB(callback, False, self.dbInterfaceName)

        @classmethod
        def executeRawDatabaseCommand(cls, command, callback=None, threadID=-1):
            KBEngine.executeRawDatabaseCommand(command, callback, threadID, cls.dbInterfaceName)

    @classmethod
    def markAll(cls):
        for name in Equalization_.memEntities:
            m = importlib.import_module(name)
            ec = getattr(m, name)
            c = type(ec.__name__, (ec, cls.EqualizationBase), {})
            setattr(m, name, c)
            plugins.plugins.entities[name] = c

    @classmethod
    def databaseAll(cls):
        for name in list(plugins.plugins.entities):
            v = getattr(settings, name, None)
            mm = importlib.import_module(name)
            ec = getattr(mm, name)
            if not issubclass(ec, KBEngine.Entity):
                continue
            n = (getattr(v, "database", None) if v else None) or "default"
            if v:
                setattr(v, "database", n)
            c = type(ec.__name__, (cls.DatabaseBase, ec), dict(dbInterfaceName=n))
            setattr(mm, name, c)
            plugins.plugins.entities[name] = c

    @classmethod
    def discover(cls):
        cls.markAll()
        cls.databaseAll()

    def __init__(self):
        super().__init__()
        self.entities = {}
        self.autoLoadedIDMap = {}
        self.runInNextFrame(self.init)

    def destroy(self, deleteFromDB=False, writeToDB=True):
        self.clearTimerProxy()
        super().destroy(deleteFromDB, writeToDB)

    def init(self):
        KBEngine.globalData["EqualizationEntity"] = self
        KBEngine.BaseApp.onGlobalData("EqualizationEntity", self)

    def addEntity(self, name, path, entity):
        self.entities[name + "_%s" * len(path) % tuple(path)] = entity
        self.checkMemEntityCompleted()

    def checkMemEntityCompleted(self):
        for path in Equalization_.getAllPath():
            if "_".join([str(i) for i in path]) not in self.entities:
                return
        self.onMemEntityCompleted()

    def onMemEntityCompleted(self):
        KBEngine.globalData["Equalization"] = self.entities
        KBEngine.BaseApp.onGlobalData("Equalization", self.entities)

    def addAutoLoaded(self, name, dbid):
        if name:
            m = self.autoLoadedIDMap.setdefault(name, [])
            if dbid:
                m.append(dbid)
        self.checkAutoLoadedCompleted()

    def checkAutoLoadedCompleted(self):
        for name, idList in Equalization_.autoLoadedIDMap.items():
            if name not in self.autoLoadedIDMap or set(self.autoLoadedIDMap[name]) != set(idList):
                return
        self.onAutoLoadedCompleted()

    def onAutoLoadedCompleted(self):
        del KBEngine.globalData["EqualizationEntity"]
        KBEngine.BaseApp.onGlobalDataDel("EqualizationEntity")
        entity_auto_load_completed.send(self)
        self.destroy()


@receiver(baseapp_ready)
def baseappReady(signal, sender):
    if sender.groupIndex == 1:
        KBEngine.createEntityLocally('Equalization', dict())


@receiver(global_data_change)
def equalization_change(signal, sender, key, value):
    def callback():
        def callback(name, baseRef, dbid, wasActive):
            if wasActive:
                ERROR_MSG("equalization::callback: this equalization obj is online! %s, %s, %s, %s" % (
                    name, baseRef, dbid, wasActive))
                return
            if baseRef is None:
                ERROR_MSG(
                    "equalization::callback: the equalization obj you wanted to created is not exist! %s, %s, %s, %s" %
                    (name, baseRef, dbid, wasActive))
                return
            KBEngine.globalData["EqualizationEntity"].addAutoLoaded(name, dbid)

        need_created = []
        for name, idList in Equalization_.autoLoadedIDMap.items():
            for i in range(index - 1, len(idList), settings.BaseApp.equalizationBaseappAmount):
                KBEngine.createEntityFromDBID(name, idList[i], partial(callback, name))
            if not idList:
                if settings.get(name).autoLoadedOrCreate:
                    need_created.append(name)
                elif sender.groupIndex == 1:
                    KBEngine.globalData["EqualizationEntity"].addAutoLoaded(name, 0)

        need_created.sort()
        for i in range(index - 1, len(need_created), settings.BaseApp.equalizationBaseappAmount):
            name = need_created[i]
            KBEngine.createEntityLocally(name, dict(entityNeedSave=True))
            KBEngine.globalData["EqualizationEntity"].addAutoLoaded(name, 0)

        if not Equalization_.autoLoadedIDMap and sender.groupIndex == 1:
            KBEngine.globalData["EqualizationEntity"].addAutoLoaded("", 0)

    index = sender.groupIndex
    if index <= settings.BaseApp.equalizationBaseappAmount:
        if key == "EqualizationEntity":
            Equalization_.createBaseLocally()
        elif key == "Equalization":
            Equalization_.loadEntities(callback)
    else:
        signal.disconnect(equalization_change)


@receiver(global_data_del)
def equalization_del(signal, sender, key):
    index = sender.groupIndex
    if index <= settings.BaseApp.equalizationBaseappAmount:
        if key == "EqualizationEntity":
            global_data_change.disconnect(equalization_change)
            signal.disconnect(equalization_del)
    else:
        signal.disconnect(equalization_del)
