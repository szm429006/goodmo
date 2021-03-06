# -*- coding: utf-8 -*-
from kbe.protocol import Type, Base, BaseMethod


class RunObject:
    base = Base(
        run=BaseMethod(Type.CALL.array)
    )

    def run(self, callList):
        for call in callList:
            call(self)

    def modifyRun(self, *args):
        method, arg = args[0], args[1:]
        getattr(self, method)(*arg)
