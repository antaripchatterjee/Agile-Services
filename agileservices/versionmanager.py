class VersionManager(object):
    @classmethod
    def get_service(cls, version):
        plugin = cls.all.get(version)
        if not plugin:
            raise NotImplementedError(
                f'version "{version}" has not been implemented'
            )
        return plugin