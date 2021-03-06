__third_package__ = (
    "xlrd", "tornado==4.5.2", "yapf", "aioredis==0.3.5", "redis", "pymongo==3.5.0", "pymysql", "motor==1.1",
    "dicttoxml", "oscrypto", "simplejson", "sortedcontainers"
)

__kbengine_xml_default__ = dict(
    gameUpdateHertz=60,
    originCid=10000,
    publish=dict(
        state=0
    ),
    dbmgr=dict(
        databaseInterfaces=dict(
            default=dict(
                host="localhost",
                port=3306,
                auth=dict(
                    username="root",
                    password="123456",
                    encrypt="true"
                ),
                databaseName=""
            )
        )
    ),
    loginapp=dict(
        externalAddress=""
    ),
    baseapp=dict(
        externalAddress="",
        backupPeriod=500,
        externalPorts_min=20015,
        externalPorts_max=20035
    ),
    bots=dict(
        account_infos=dict(
            account_name_prefix="bot_",
            account_name_suffix_inc=1,
            account_password="O5LCJ3uotGCqOwDf"
        )
    )
)

__kbengine_xml__ = dict(
    gameUpdateHertz=60,
    publish=dict(
        state=0,
        script_version="0.1.0"
    ),
    dbmgr=dict(
        databaseInterfaces=dict(
            default=dict(
                numConnections=10,
                host="localhost",
                port=3306,
                auth=dict(
                    username="root",
                    password="123456",
                    encrypt="true"
                ),
                databaseName=""
            )
        ),
        account_system=dict(
            account_registration=dict(
                enable="true",
                loginAutoCreate="true"
            )
        )
    ),
    interfaces=dict(
    ),
    loginapp=dict(
        externalAddress=""
    ),
    logger=dict(
    ),
    baseapp=dict(
        externalAddress="",
        archivePeriod=1,
        backupPeriod=500
    ),
    cellapp=dict(
        coordinate_system=dict(
            enable="false",
            rangemgr_y="false",
            entity_posdir_additional_updates=5
        )
    ),
    bots=dict(
        defaultAddBots=dict(
            totalCount=0
        ),
        account_infos=dict(
            account_name_prefix="bot_",
            account_name_suffix_inc=1
        )
    )
)
