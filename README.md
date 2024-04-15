<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>
<div align="center">

# nonebot_plugin_clovers

<img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="python">
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/KarisAya/nonebot_plugin_clovers.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot_plugin_clovers">
  <img src="https://img.shields.io/pypi/v/nonebot_plugin_clovers.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot_plugin_clovers">
  <img src="https://img.shields.io/pypi/dm/nonebot_plugin_clovers" alt="pypi download">
</a>
</div>

## 💿 安装

<details open>
<summary>推荐使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot_plugin_clovers
```

</details>

<details>
  <summary>使用包管理器安装</summary>
<details>
<summary>pip</summary>

```bash
pip install nonebot_plugin_clovers
```

</details>

<details>
<summary>poetry</summary>
```bash
poetry add nonebot_plugin_clovers
```
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_clovers"
]
```

</details>

## ⚙️ 配置

`clovers_config_file` clovers 框架配置文件路径

```properties
"clovers_config_file" = "clovers.toml"
```

插件位置

## 🎉 使用

详见[clovers](https://github.com/KarisAya/clovers) 自定义的聊天平台异步机器人指令-响应插件框架

在你定义的 clovers 框架配置文件文件中添加下面的配置

```toml
[nonebot_plugin_clovers]
plugins_path = "./clovers_library"
plugins_list = []
```

`plugins_path` 加载本地插件位置
`plugins_list` 加载插件列表

已完成的[适配器方法](https://github.com/KarisAya/nonebot_plugin_clovers/tree/master/nonebot_plugin_clovers/adapters)

## 📞 联系

如有建议，bug 反馈等可以加群

机器人 bug 研究中心（闲聊群） 744751179

永恒之城（测试群） 724024810

![群号](https://github.com/KarisAya/clovers/blob/master/%E9%99%84%E4%BB%B6/qrcode_1676538742221.jpg)

## 💡 鸣谢

- [nonebot2](https://github.com/nonebot/nonebot2) 跨平台 Python 异步聊天机器人框架
