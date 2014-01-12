import cbpos
from cbpos.modules import BaseModuleMetadata

class ModuleMetadata(BaseModuleMetadata):
    base_name = 'installer'
    version = '0.1.0'
    display_name = 'Module Installer and Manager'
    dependencies = (
        ('base', '0.1'),
    )
    config_defaults = tuple()
