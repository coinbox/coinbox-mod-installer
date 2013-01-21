import os, zipfile, shutil
import ConfigParser
import time

import cbpos

class ModuleManager(object):
    
    def enable(self, mod_names, enable=True):
        disabled_str = cbpos.config['mod', 'disabled_modules']
        disabled_set = set(disabled_str.split(',')) if disabled_str != '' else set()
        if type(mod_names) == str:
            mod_names = [mod_names]
        
        if enable:
            for mod_name in mod_names:
                disabled_set.discard(mod_name)
        elif enable is None:
            for mod_name in mod_names:
                if mod_name in disabled_set:
                    disabled_set.discard(mod_name)
                else:
                    disabled_set.add(mod_name)
        else:
            for mod_name in mod_names:
                disabled_set.add(mod_name)
        
        cbpos.config['mod', 'disabled_modules'] = ','.join(disabled_set)
        cbpos.config.save()
    
    disable = lambda self, mod_names: self.enable(mod_names, enable=False)
    toggle = lambda self, mod_names: self.enable(mod_names, enable=None)

    def installer_info(self, target):
        z = zipfile.ZipFile(target, 'r')
    
        if 'install.cfg' not in z.namelist() or \
            all(name.startswith('mod/') or name.startswith('res/') \
                for name in z.namelist()):
            return False
        
        config_file = z.open('install.cfg', 'r')
        config = ConfigParser.SafeConfigParser()
        config.readfp(config_file)
        
        base_name, name, version = config.get('info', 'base_name'), config.get('info', 'name'), config.get('info', 'version')
        z.close()
        return (base_name, name, version)

    def install(self, target, info=None, replace=False):
        raise NotImplemetedError, 'This feature does not work yet'
        if info is None:
            info = self.installer_info(target)
            if not info:
                return False
        elif not info:
            return False
        
        installed = cbpos.modules.is_installed(info[0])
        if not replace and installed:
            return False
        elif replace and installed:
            base_name, name, version = installed
            self.uninstall(base_name, remove_resources=False)
        
        z = zipfile.ZipFile(target, 'r')
        
        members = z.namelist()
        members.remove('install.cfg')
        z.extractall(members=members)
        z.close()
        # TODO: add the module to the module list in cbpos.mod as disabled

    def uninstall(self, mod_name, remove_resources=True):
        raise NotImplemetedError, 'This feature does not work yet'
        self.enable(mod_name)
        mod = cbpos.modules.by_name(mod_name)
        shutil.rmtree(mod.path)
        if remove_resources:
            shutil.rmtree(mod.res_path())
        # TODO: remove the module from the module list in cbpos.mod
        return True

    def export(self, mod, target, export_source=False):
        raise NotImplemetedError, 'This feature does not work yet'
        z = zipfile.PyZipFile(target, 'w')
    
        config_filename = cbpos.res.installer('modconfig/%s.cfg' % (mod.name,))
        config_file = open(config_filename, 'w')
        
        config = ConfigParser.SafeConfigParser()
        config.add_section('info')
        config.set('info', 'base_name', str(mod.name))
        config.set('info', 'name', str(mod.loader.name))
        config.set('info', 'version', str(mod.loader.version))
        
        config.write(config_file)
        config_file.close()
        
        z.write(config_filename, 'install.cfg')
        
        if export_source:
            os.path.walk(mod.path, lambda *args: self.__zipdirectory(*args, ignore_hidden=True), z)
        else:
            z.writepy(mod.path, 'mod')
        os.path.walk(mod.res_path(), self.__zipdirectory, z)
        z.close()

    def __zipdirectory(self, z, dirname, filenames, ignore_hidden=True):
        if ignore_hidden:
            [filenames.remove(fname) for fname in filenames[:] if fname.startswith('.')] 
        if len(filenames) == 0:
            now = time.localtime(time.time())[:6]
            info = zipfile.ZipInfo(dirname+os.path.sep)
            info.date_time = now
            info.compress_type = zipfile.ZIP_STORED
            z.writestr(info, '')
        else:
            for fname in filenames:
                path = os.path.join(dirname, fname)
                if os.path.isdir(path): continue
                z.write(path, path)
