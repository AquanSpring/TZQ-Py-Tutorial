# TZQ-Py-Tutorial

[![CI](https://github.com/AquanSpring/TZQ-Py-Tutorial/actions/workflows/ci.yml/badge.svg)](https://github.com/AquanSpring/TZQ-Py-Tutorial/actions/workflows/ci.yml)

写给初学者的 Python 基础教程（纯文字 + 表格 + 代码，不含插图）。

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

## 质量校验

两个脚本，CI 都会执行；改完文章或示例请先在本地跑通它们。

### 代码：`_check_examples.py`

把 `examples/` 和正文里的 python 代码块都实际跑一遍：

```bash
python -X utf8 _check_examples.py
```

- **运行**：脚本复制到临时目录后逐个执行，要求退出码为 0（产物也留在临时目录，不污染仓库）；
- **核对**：`print(...)` 行末注释里声称的输出值，必须真的出现在实际输出中；
- **范围**：正文按章拼接代码块后运行；`❌` 标出的反面教材和「本章挑战作业」段落不参与（后者引用的类要读者自己写）。

### 文字：`_check_docs.py`

检查那些“不会报错、只会让读者扑空”的问题：

```bash
python -X utf8 _check_docs.py
```

- **词典覆盖**：正文里 `**中文（English）**` 这种术语对照，English 必须在第 0 章的“小词典”里查得到；
- **章节引用**：所有“第 N 章”（阿拉伯数字与中文数字都算）必须指向真实存在的章节；
- **词典指引**：凡是写“第 0 章词典里就有 X”的地方，X 必须真的在词典里。

新增术语时，记得同步补进 `（00）学前基础.md` 的对应表格，否则这一步会失败。
