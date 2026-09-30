# TZQ-Py-Tutorial

写给初学者的 Python 图文教程。

- 在线阅读：<https://aquanspring.github.io/TZQ-Py-Tutorial/>
- 当前进度：Python 基础篇 · 初版（共 19 章）

## 仓库结构

| 路径 | 说明 |
| --- | --- |
| `index.html` | 整站单文件，GitHub Pages 的入口（由构建脚本生成） |
| `python基础篇/` | 正文源文件：19 章 Markdown |
| `python基础篇/examples/` | 每章配套的可运行示例代码 |
| `_build_index.py` | 构建脚本：把 Markdown 合成单页 `index.html` |

## 本地构建

```cmd
python -X utf8 _build_index.py
```

会在仓库根目录重新生成 `index.html`。

## 说明

- 站点是零依赖单文件，用浏览器直接打开即可，离线也能看。
- 每章末尾的挑战作业**不提供参考答案**——这是有意为之：答案是你在自己敲出来的程序里找到的那个。
- 配套示例（`python基础篇/examples/`）只包含正文讲过的内容，同样**不含任何作业答案**。
