# -*- coding: utf-8 -*-
import asyncio
import KBEngine
from kbe.core import Equalization, Redis
from kbe.protocol import Base, BaseMethod, Property, Client, ClientMethod, Type
from common.dispatcher import receiver
from default.signals import avatar_created


class RobotBackendManager(KBEngine.Entity):
    base = Base(
        botCreated=BaseMethod(Type.DBID),
        queryBots=BaseMethod(Type.ENTITYCALL, Type.UINT32, Type.UNICODE),
    )

    redisCacheKey = "robotSet"

    def __init__(self):
        super().__init__()
        self.availableRobots = set()
        self.onInit()

    def onInit(self):
        def callback(r_list):
            self.availableRobots = set(int(dbid) for dbid in r_list)

        asyncio.async(robot_list_generation()).add_done_callback(lambda future: callback(future.result()))

    def botCreated(self, dbid):
        asyncio.async(robot_add_generation(dbid))

    def queryBots(self, entity, amount, order):
        take_list = []
        for dbid in self.availableRobots:
            if len(take_list) < amount:
                take_list.append(dbid)
            else:
                break
        if take_list:
            self.availableRobots.difference_update(take_list)
        entity.addExactBots(take_list, amount - len(take_list), order)


@receiver(avatar_created)
def created(signal, avatar):
    if avatar.robotMark:
        Equalization.RobotBackendManager.botCreated(avatar.accountID)


@asyncio.coroutine
def robot_add_generation(dbid):
    yield from Redis.RobotBackendManager.RobotSet.sadd(RobotBackendManager.redisCacheKey, dbid)


@asyncio.coroutine
def robot_list_generation():
    r_list = yield from Redis.RobotBackendManager.RobotSet.smembers(RobotBackendManager.redisCacheKey)
    return r_list
