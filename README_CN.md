# 项目简介
[English](README.md)

本项目是一个 Home Assistant 的自定义组件，它与 Nginx Proxy Manager 集成，支持通过 Home Assistant 的开关一键切换指定域名的 Access。此外，该组件还支持通过使用不同的 Access 配置文件来实现控制内外网访问。该组件的协议是基于 Apache 2.0 许可进行开源。

# 快速上手
## 安装
1. 下载本项目的代码并将其放置在 Home Assistant 的 custom_components 目录下。
2. 重启 Home Assistant。
## 配置
1. 在`const.py`里的 `DEFAULT_ACCESS_NAME_FOR_OFF` 配置开关处于关闭状态下对应的 access 名称
2. 添加 Nginx Proxy Manager Access 集成。
3. 输入主机、邮箱、密码等信息。
4. 将会自动创建名称为域名的开关
## 使用
使用 Home Assistant 的开关来切换 Access，从而实现内外网访问控制。

协议
本项目的协议是基于 Apache 2.0 许可进行开源。