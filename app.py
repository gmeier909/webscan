import subprocess
import threading
import locale
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import time
import csv
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# 获取当前项目目录
def get_current_directory():
    return os.getcwd()

# 获取插件目录，传插件目录名称
def get_plugin_path(name):
    return os.getcwd() + "/plugin/" + name

# 获取oneforall的csv结果，把ip去重
def get_unique_ips(ipfile, iporurl):
    filepath = get_plugin_path("oneforall") + '/results/' + ipfile + '.csv'
    ip_set = set()
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if iporurl == "ip":
                ip = row[8]
            else:
                ip = row[4]
            if ',' in ip:
                ip_list = ip.split(',')
                for ip_entry in ip_list:
                    ip_set.add(ip_entry.strip())
            else:
                ip_set.add(ip.strip())
    return ip_set

# 去重后的ip写入文件
def write_ips_to_file(ipfile, ip_set, iporurl):
    if iporurl == "ip":
        ipfilepath = get_current_directory() + '/results/' + ipfile + '_ip.txt'
    else:
        ipfilepath = get_current_directory() + '/results/' + ipfile + '_url.txt'
    with open(ipfilepath, 'w', encoding='utf-8') as file:
        for ip_entry in ip_set:
            file.write(ip_entry + '\n')
    return ipfilepath

# ip去重写入文件
def gip_start(ipfile, iporurl):
    ip_set = get_unique_ips(ipfile, iporurl)
    filepath = write_ips_to_file(ipfile, ip_set, iporurl)
    return filepath

def update_argument(args, OtherArgv):
    # 循环其他参数
    for arg in OtherArgv:
        # 如果其他参数在传过来的args里，那么就获取这个其他参数的位置，返回目录
        if arg in args:
            index = OtherArgv.index(arg)
            OtherArgv[index + 1] = get_current_directory() + "/results/" + OtherArgv[index + 1]
    return OtherArgv

def load_config(filename):
    with open(filename, "r") as file:
        config = json.load(file)
    return config

def construct_command(ScanType, OtherArgv):
    config = load_config("config.json")
    scan_type_configs = config["scan_types"]
    
    # 如果ScanType不在配置文件key里
    if ScanType not in scan_type_configs:
        return "echo fuck your mother!"
    
    # 加载对应ScanType的配置
    config = scan_type_configs[ScanType]
    # 获取ScanType对应的路径
    path = get_plugin_path(ScanType)
    # update_args是需要修改目录的参数
    OtherArgv = update_argument(config['update_args'], OtherArgv)
    # args：判断是否需要加python前缀，path是插件目录，config['path_suffix]是插件文件名
    command = config['args'] + [f"{path}{config['path_suffix']}"] + OtherArgv
    
    return command








UPLOAD_FOLDER = 'results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_list(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
    
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['GET', 'POST'])
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('index'))

@app.route('/view/<filename>')
def view_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    return render_template('view.html', filename=filename, content=content)


@app.route('/')
def index():
    files = get_file_list(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@socketio.on('connect')
def handle_connect():
    user_sid = request.sid
    session['user_sid'] = request.sid
    print('有客户端连接到服务器' + user_sid)

@socketio.on('command')
def handle_command(command):
    print('收到命令:', command)
    
    argv = command.split(" ")
    OtherArgv = argv[1:]
    ScanType = argv[0]
    # 循环删除||,|,&&,&,or,and
    OtherArgv = [item.replace("||", "").replace("|", "").replace("&&", "").replace("&", "").replace("or", "").replace("and", "").replace("localhost", "fuck your mother") for item in OtherArgv]

    command = construct_command(ScanType, OtherArgv)
    print(command)
    
    def run_command(user_sid):
        with app.app_context():
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                output = process.stdout.readline()
                try:
                    output = output.decode('utf-8')
                except UnicodeDecodeError:
                    output = output.decode('gbk', errors='replace')
                if output == '' and process.poll() is not None:
                    break
                print(output)
                time.sleep(0.001)
                socketio.emit('output', output, room=user_sid)
                time.sleep(0.001)
            process.stdout.close()
        if ScanType == "oneforall":
            domain = argv[2].split(".")[-2:]
            domain = ".".join(domain).split(":")[0]
            gip_start(domain, "ip")
            gip_start(domain, "url")
            socketio.emit('output', "url文件生成到" + get_current_directory() + "\\result\\" + domain + "_url.txt")
            socketio.emit('output', "ip文件生成到" + get_current_directory() + "\\result\\" + domain + "_ip.txt")
            

    threading.Thread(target=run_command(session.get('user_sid'))).start()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
