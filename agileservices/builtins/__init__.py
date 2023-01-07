from collections import OrderedDict


@property
def allow_install():
    return OrderedDict([
        ('serviceinstaller', 'v1')
    ])