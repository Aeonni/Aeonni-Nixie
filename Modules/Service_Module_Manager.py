__version__ = '0.0.1'
moduleName = 'ModuleManager'

from Modules.Aeonni_Nixie_Module import AN_Module

print('loading...Service_Module_Manager ver. ', __version__)

blank_proc = dict(
    name = 'blank_proc',
    ver = '0.0.0',
    port = '0',
    stcmd = 'None',
    logo = 'None',
    visiable = 'None',
    state = 'Unknown',
    ps = '',
    qstring = 'ls',
    close = '',
    url = '#',
    colors = dict(
        bg = '#fff',
        line = '#ddd',
        logo = '#8f82bc'
    ),
    checkstr = 'NONE'
)

class ModuleManager(AN_Module):
    def __init__(self, mdict):
        self.mdict = mdict
        AN_Module.__init__(self, moduleName, __version__)
        self.state = 'Running'
    def get_modules_list(self):
        m_infos = [self.getinfo()]
        for each in self.mdict:
            try:
                m_infos.append(self.mdict[each].getinfo())
            except:
                pass

        if len(m_infos) % 2 == 0:
            pass
        else:
            m_infos.append(blank_proc)

        li = []
        for i in range(int(len(m_infos)/2)):
            li.append(m_infos[i*2:i*2+2])
        return li
    def open_module(self, name):
        return self.mdict[name].module_open()
    def close_module(self, name):
        return self.mdict[name].module_close()