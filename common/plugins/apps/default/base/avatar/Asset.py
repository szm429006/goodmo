# -*- coding: utf-8 -*-
import settings
import KBEngine
from kbe.protocol import Property, Volatile, Type, Base, BaseMethod, BaseMethodExposed, Client, ClientMethod
from common.utils import Bytes
from common.dispatcher import receiver
from kbe.utils import LockAsset
from default.signals import avatar_common_login_post, avatar_consume
from CORE import python_client


class Asset(LockAsset("gold")):
    base = Base(
        reqSyncData=BaseMethodExposed(),
    )

    client = Client(
        onSyncData=ClientMethod(),
        onOperate=ClientMethod(Type.UNICODE, Type.UNICODE, Type.PYTHON),
    )

    name = Property(
        Type=Type.UNICODE,
        Flags=Property.Flags.BASE_AND_CLIENT,
        # Index=Property.Index.UNIQUE,
        DatabaseLength=settings.Avatar.nameLengthUpLimit,
        Persistent=Property.Persistent.true
    )

    gold = Property(
        Type=Type.GOLD_X,
        Flags=Property.Flags.BASE_AND_CLIENT,
        Persistent=Property.Persistent.true
    )

    avatarUrl = Property(
        Type=Type.UNICODE,
        Flags=Property.Flags.BASE_AND_CLIENT,
        Persistent=Property.Persistent.true
    )

    def __init__(self):
        super().__init__()
        self.transactionSet = set()

    def reqSyncData(self):
        self.syncData()

    def syncData(self):
        def callback(orderID, dbID, success, datas):
            if uid != orderID:
                return
            data = Bytes(datas)
            dataList = data.get("x", [])
            self.consumeData(dataList)
            if self.client:
                self.client.onSyncData()
            self.release()

        self.addRef()
        uid = str(KBEngine.genUUID64())
        KBEngine.charge(uid, self.databaseID,
                        Bytes(interface="syncData", pk=self.pk).dumps(), callback)

    def interfaceOperate(self, operate, t, d, c=None):
        def callback(orderID, dbid, success, datas):
            if uid != orderID:
                return
            data = Bytes(datas)
            if c:
                c(self, data)
            if self.client:
                self.client.onOperate(operate, t, python_client(data))
            self.release()

        self.addRef()
        uid = str(KBEngine.genUUID64())
        KBEngine.charge(uid, self.databaseID,
                        Bytes(interface="operate", operate=operate, type=t, data=d).dumps(), callback)

    def consumeData(self, dataList):
        for data in dataList:
            handler = getattr(self, "%s%sConsumeData" % (data["pay_type"], data["attach"]["type"]))
            handler(data["attach"])
            avatar_consume.send(self, data=data)

    def modifyName(self, changed):
        name = self.name
        self.name = changed
        self.onModifyAttr("name", changed, name)

    def modifyAvatarUrl(self, newUrl):
        url = self.avatarUrl
        self.avatarUrl = newUrl
        self.onModifyAttr("avatarUrl", newUrl, url)


@receiver(avatar_common_login_post)
def login(signal, avatar):
    data = Bytes(avatar.getClientDatas()[0])
    consume_data = data.get("consume_data")
    if consume_data:
        data_list = consume_data.get("x")
        if data_list:
            d_list = []
            for d in data_list:
                transaction = "%s:%s" % (d["pay_type"], d["transaction_id"])
                if transaction not in avatar.transactionSet:
                    avatar.transactionSet.add(transaction)
                    d_list.append(d)
            if d_list:
                avatar.consumeData(d_list)
