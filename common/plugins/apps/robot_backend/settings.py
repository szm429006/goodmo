from plugins.conf import SettingsEntity, EqualizationMixin


class RobotBackendGenerator(SettingsEntity, EqualizationMixin):
    equalization__mod_base = 1

    def equalization_list(self):
        return [[i] for i in range(self.equalization__mod_base)]

    def equalization(self, any_id):
        return [self.mod(any_id, self.equalization__mod_base)]


class RobotBackendManager(SettingsEntity, EqualizationMixin):
    equalization__mod_base = 1

    def equalization_list(self):
        return [[0]]

    def equalization(self, *args):
        return [0]

    def redis(self):
        return dict(
            RobotSet=dict(host='localhost', port=6379, db=0),
        )
