from agileservices.versionmanager import VersionManager
from .plugin import ServiceInstaller


class Version(VersionManager):
    all = {
        'v1' : ServiceInstaller
    }