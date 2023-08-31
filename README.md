# WebScan



## 工具描述

一个信息收集超超超级缝合工具，目前集成OneForAll,FScan,Xray,Xpoc,VulMap,EnScan,AfRog,FOFA-Api。



## 工具优势

1. OneForAll扫描文件自动ip和域名去重。
2. 无需打开多个终端，一个web解决大部分信息收集问题。
3. 不影响工具原生命令，只做了适配。
4. 支持文件上传和文件查看。
5. 适合红队信息收集，团队可以实时查看扫描结果。



## 使用说明

1. 所有工具使用方式跟原本工具一模一样，如不知如何使用，请在github搜索对应工具名称。
2. 文件都默认存放在/results下



## 运行程序

安装相应工具的模块

如：pip install -r ./plugin/oneforall/requirements.txt

如果报错no module xxx，请执行pip install xxx，xxx为对应的模块名称

运行程序

```shell
python app.py
```



## 添加工具

/config.json

```
{
    "scan_types": {
        "oneforall": {
            "path_suffix": "/oneforall.py",
            "args": ["python"],
            "update_args": []
        },
        "fscan": {
            "path_suffix": "/fscan.exe",
            "args": [],
            "update_args": ["-hf", "-o", "-uf"]
        },
        "工具目录": {
            "path_suffix": "/运行文件名",
            "args": ["如果是python这里填python，exe就为空"],
            "update_args": [适配文件位置，比如fscan的-o输出文件位置，-hf扫描ip文件]
        },
    }
}
```



## 工具缺陷

1. 不能多个命令同时执行。
2. 不支持二级目录文件查看。
3. fscan使用时尽量带上-no -nobr -nopoc，-no不输出文件，-nobr不进行爆破，-nopoc不扫描poc，根据实际情况来使用，不然会扫描很长时间。




## 工具列表

OneForAall：https://github.com/shmilylty/OneForAll

FScan：https://github.com/shadow1ng/fscan

Xray：https://github.com/chaitin/xray

Xpoc：https://github.com/chaitin/xpoc

VulMap：https://github.com/zhzyker/vulmap

EnScan：https://github.com/wgpsec/ENScan_GO

AfRog：https://github.com/zan8in/afrog

FOFA-API：忘记地址了。



## 开源支持

本程序有很多不足，欢迎大家二开优化本程序，如果有优化意见也可以提个issues。