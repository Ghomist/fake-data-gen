# Fake Data Generator

~~写一份 yaml，生成专属于你的假数据~~

本脚本仅够模拟数据，便于测试，以简化开发

## 环境

依赖于一些相当优秀的包：~~（因为觉得非常优秀所以内嵌引入了）~~

- faker（快速生成各种样式的假数据，并且支持 i18n ）
- xeger（反向 regex，通过正则表达式生成随机字符串）

```bash
pip install faker xeger
```

## 快速开始

克隆源码目录，然后将 scheme.yaml 复制一份并重命名，然后执行命令：

```bash
python main.py your-scheme.yaml
```

## Schema 文档

一个简单的[示例](./schema.yaml)

TODO
