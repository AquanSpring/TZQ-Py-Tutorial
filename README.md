# TZQ-Py-Tutorial

[![CI](https://github.com/AquanSpring/TZQ-Py-Tutorial/actions/workflows/ci.yml/badge.svg)](https://github.com/AquanSpring/TZQ-Py-Tutorial/actions/workflows/ci.yml)

写给初学者的 Python 图文教程。

- 在线阅读：<https://aquanspring.github.io/TZQ-Py-Tutorial/>
- 当前进度：Python 基础篇 · 初版（共 19 章）
- 本项目基于 [MIT 许可证](LICENSE) 开源，可自由使用、修改和再分发。

## 本地构建

站点是单文件 index.html，由 [_build_index.py](_build_index.py) 从各篇章文件夹的 Markdown 生成：

```bash
python -X utf8 _build_index.py
```

- **新增章节**：把 md 按「（数字）标题.md」命名放进篇章文件夹（如 `python基础篇/`），重跑脚本即可；
- **写作限制**：转换器不支持 *斜体*、#### 及更深层标题、引用块内代码围栏，写错会在构建时直接报错；
- **提交前**：改了 md 或构建脚本后必须重新生成 index.html 并一并提交，CI 会校验两者是否一致。
