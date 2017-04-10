from plugins.conf import SettingsNode, SettingsEntity, EqualizationMixin


class PlayerManager(SettingsEntity, EqualizationMixin):
    equalization__mod_base = 1

    def equalization_list(self):
        return [[i] for i in range(self.equalization__mod_base)]

    def equalization(self, guarantee_id):
        return [self.mod(guarantee_id, self.equalization__mod_base)]


class Account(SettingsEntity):
    avatarTotalLimit = 1
    type = ("tourist", "email", "phone", "weixin", "qq", "weibo",)
    url = SettingsNode(
        authUser=r"http://127.0.0.1:8000/game/auth_user/"
    )


class Avatar(SettingsEntity):
    namePrefix = "玩家"
    nameIndexRadix = 15682357
    delayDestroySeconds = 5 * 60
    newbieData = SettingsNode(gold=0)


class Guarantee(SettingsEntity):
    delayDestroySeconds = 5 * 60
