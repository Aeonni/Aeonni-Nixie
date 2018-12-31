__version__ = '0.3.1'

print('loading...AdminPanel ver. ', __version__)

import time
import os
import random
import json
import base64
from werkzeug.routing import BaseConverter
from flask import Flask, render_template, Response, request, redirect, session
from multiprocessing import Value

admin = 'Aeonni-Nixie-Admin-'
passwd = "***"

admitted_id = Value('i', -1)

# class RegexConverter(BaseConverter):
#     def __init__(self, map, *args):
#         self.map = map
#         self.regex = args[0]

app = Flask(__name__)
app.secret_key = "aakjdlkasjfblkjaflknfjhkjnakf"
# app.url_map.converters['regex'] = RegexConverter

nfc_module = None
module_manager = None

icon_dict = dict(
    running = ["fa fa-toggle-on fa-2x", "color:lightgreen; vertical-align: middle"] ,
    Running = ["fa fa-toggle-on fa-2x", "color:lightgrey; vertical-align: middle"] ,
    stopped = ["fa fa-toggle-off fa-2x", "color:orange; vertical-align: middle"],
    Unknown = ['','']
)

@app.route('/', methods=['GET'])
def index():
    if not session.get('user_info'):
        return render_template("index.html", pwdERR=False, sid='%.6d'%nfc_module.generate_auth_id(), nfc=nfc_module.isrunning())
    if session.get('user_info') != admin+'%.6d'%admitted_id.value:
        # print(session.get('user_info'), admin+'%.6d'%admitted_id.value)
        session.clear()
        return render_template("index.html", pwdERR=False, sid='%.6d'%nfc_module.generate_auth_id(), nfc=nfc_module.isrunning())
    return render_template("manager.html", procs = module_manager.get_modules_list(), 
                                            user = session.get('user_info')[:-3]+'***', 
                                            time = time.asctime(), icon_dict = icon_dict)
    

@app.route('/', methods=['POST'])
def index_post():
    pwd = request.form.get('pwd')
    # print(pwd)
    if pwd == passwd:
        session['user_info'] = admin+request.form.get('sid')
        admitted_id.value = int(request.form.get('sid'))
        nfc_module.reset_dev_prio()
        nfc_module.cu_auth_id = -1
        # return redirect('/index')
        return redirect('/') #json.dumps({'login': True}) 
    else:
        if session.get('user_info') == admin+'%.6d'%admitted_id.value:
            return redirect('/')
        return render_template("index.html", pwdERR=True, sid='%.6d'%nfc_module.generate_auth_id(), nfc=nfc_module.isrunning())

@app.route('/if-jump', methods=['GET'])
def jump():
    s = '%.6d'%int(request.args['sid'])
    if nfc_module.do_auth(60, lambda x: True, int(s)):
        session['user_info'] = admin+s
        admitted_id.value = int(s)
        nfc_module.reset_dev_prio()
        nfc_module.cu_auth_id = -1
        return json.dumps({'login': True}) 
    return json.dumps({'login': False}) 

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')



def imageToStr(image):
    with open(image,'rb') as f:
        image_byte=base64.b64encode(f.read())
        # print(type(image_byte))
    image_str=image_byte.decode('ascii') #byte类型转换为str
    # print(type(image_str))
    return image_str


@app.route('/open', methods=['GET'])
def m_open():
    m_name = str(request.args['name'])
    print('open: ', m_name)
    r = module_manager.open_module(m_name)
    if r:
        return json.dumps({'success': True}) 
    else:
        time.sleep(1)
        s = imageToStr('/home/pi/Aeonni-Nixie/QR.png')
        # print('len: ',len(s))
        return json.dumps({'success': False, 'img': s}) 

@app.route('/close', methods=['GET'])
def m_close():
    m_name = str(request.args['name'])
    print('close: ', m_name)
    module_manager.close_module(m_name)
    return json.dumps({'success': True}) 

# if __name__ == '__main__':
def start():
    port = 2333
    app.run('0.0.0.0', port = port, debug=True, use_reloader=False)
    # os.popen('open http://127.0.0.1:%d'%port)