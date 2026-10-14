# -*- coding: utf-8 -*-
"""
TZQ-Py-Tutorial 示例代码校验（CI 用）。

做两类检查，任何一处不合格就以非零码退出：

1. 【运行】把每个篇章的 examples/ 复制到临时目录，逐个脚本跑一遍，要求退出码为 0。
   复制到临时目录有两个好处：ch16 这类会写文件的示例把产物留在临时目录里，
   不污染仓库；同时也能验证脚本不依赖“从哪个目录运行”。

2. 【核对】把 print(...) 行末注释里声称的“值”抽出来，要求它确实作为一整行
   出现在同一源码行的 print 输出里；函数或循环中同一行可产生多个结果，至少命中一次。
   注释里带中文说明的（如 `# [1, 2] —— 筛选结果`）只取
   说明之前的部分；认不出是纯值的注释直接跳过——宁可漏检，也不误报。

除了 examples/，正文 md 里的 ```python 代码块也按章拼接后跑一遍并核对注释，
这样“正文写错了但示例是对的”也能被拦下来。

用法：python -X utf8 _check_examples.py
"""
import builtins
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))

# 交互式代码要喂进去的输入。默认这组能同时满足第 9 章示例（姓名/年龄/身高/体重）；
# 个别章节的正文假设了特定输入（如第 12 章的“假如用户输入：3 5”），单独列出。
DEFAULT_FEED = "小明\n18\n1.75\n65\n" + "n\n" * 10
CHAPTER_FEED = {
    "（12）": "yes\n3 5\n",          # 先答“同意吗”，再给“3 5”
}

# 作业段落（## 本章挑战作业）里的代码是“给读者的用法示意”，
# 引用的类或函数要读者自己写，本就不该独立运行——不纳入校验。
HOMEWORK = "## 本章挑战作业"

# 只认“纯值”注释：数字 / 布尔 / None / type() 输出 / 列表 / 元组 / 字典 / 字符串
VALUE = re.compile(r"""
    ^(?:
        -?\d+(?:\.\d+)?
      | True | False | None
      | <class '[^']*'>
      | \[[^\[\]]*\]
      | \([^()]*\)
      | \{[^{}]*\}
      | '[^']*' | "[^"]*"
    )$""", re.X)

PRINT = re.compile(r"^\s*print\(")
FENCE = re.compile(r"```python\s*\n(.*?)```", re.S)
CHAPTER = re.compile(r"（\d+）")


def claimed_value(line):
    """取出 print 行末注释声称的输出值；不是纯值就返回 None。"""
    m = re.search(r"#\s*(.+?)\s*$", line)
    if not m:
        return None
    # 去掉 “—— 说明” / “：说明” 的尾巴，再去掉包裹的反引号
    claim = re.split(r"——|：", m.group(1))[0].strip().strip("`").strip()
    if not claim or "..." in claim:
        return None
    return claim if VALUE.match(claim) else None


def capture_output(filename, output_path):
    """子进程入口：记录目标脚本各源码行的 print 输出，并保持正常输出与输入。"""
    target = os.path.abspath(filename)
    outputs = {}
    original_print = builtins.print

    def recorded_print(*args, **kwargs):
        caller = sys._getframe(1)
        stream = kwargs.get("file")
        if caller.f_code.co_filename != target or (stream is not None and stream is not sys.stdout):
            return original_print(*args, **kwargs)
        buffer = io.StringIO()
        original_print(*args, **dict(kwargs, file=buffer))
        text = buffer.getvalue()
        sys.stdout.write(text)
        if kwargs.get("flush"):
            sys.stdout.flush()
        outputs.setdefault(str(caller.f_lineno), []).extend(
            line.strip() for line in text.splitlines() if line.strip())

    sys.path.insert(0, os.path.dirname(target))
    sys.argv = [filename]
    builtins.print = recorded_print
    try:
        runpy.run_path(target, run_name="__main__")
    finally:
        builtins.print = original_print
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(outputs, f, ensure_ascii=False)


def run_script(work, filename, code_text, problems, where, feed=DEFAULT_FEED):
    """在 work 目录下运行代码，返回源码行到输出的映射；出错时记入 problems。"""
    path = os.path.join(work, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code_text)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    env.pop("PYTHONUTF8", None)          # 让子进程用真实的系统默认编码
    output_path = os.path.join(work, "_print_output.json")
    try:
        p = subprocess.run([sys.executable, os.path.abspath(__file__),
                            "--capture-output", filename, output_path], input=feed,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=work, env=env, timeout=180)
    except subprocess.TimeoutExpired:
        problems.append("%s：运行超时（可能是死循环在等输入）" % where)
        return None
    if p.returncode != 0:
        tail = (p.stderr or "").strip().splitlines()[-6:]
        problems.append("%s：退出码 %d\n      %s" % (where, p.returncode, "\n      ".join(tail)))
        return None
    with open(output_path, encoding="utf-8") as f:
        return json.load(f)


def check_source(source, out_lines, problems, where):
    """核对源码里 print 行的注释声称值。"""
    checked = 0
    for i, line in enumerate(source.splitlines(), 1):
        if "❌" in line or not PRINT.match(line):
            continue
        claim = claimed_value(line)
        if claim is None:
            continue
        checked += 1
        if claim not in out_lines.get(str(i), []):
            problems.append("%s:%d：注释声称 %s，但该行 print 的实际输出中没有这个值"
                            % (where, i, claim))
    return checked


def main():
    volumes = []
    for entry in sorted(os.listdir(BASE)):
        exdir = os.path.join(BASE, entry, "examples")
        if os.path.isdir(exdir):
            volumes.append((entry, os.path.join(BASE, entry), exdir))

    if not volumes:
        raise SystemExit("没找到任何 */examples 目录——构建脚本或目录结构变了吗？")

    problems, ran, checked = [], 0, 0

    for vol, voldir, exdir in volumes:
        tmp = tempfile.mkdtemp(prefix="tzq-check-")
        try:
            work = os.path.join(tmp, "examples")
            shutil.copytree(exdir, work)

            # ---- 1. 逐个示例脚本 ----
            for name in sorted(os.listdir(work)):
                if not (name.startswith("ch") and name.endswith(".py")):
                    continue
                src = open(os.path.join(work, name), encoding="utf-8").read()
                out = run_script(work, name, src, problems,
                                 "%s/examples/%s" % (vol, name))
                ran += 1
                if out is not None:
                    checked += check_source(src, out, problems,
                                            "%s/examples/%s" % (vol, name))

            # ---- 2. 正文 md 的 python 代码块（按章拼接） ----
            for name in sorted(os.listdir(voldir)):
                if not name.endswith(".md") or not CHAPTER.search(name):
                    continue
                text = open(os.path.join(voldir, name), encoding="utf-8").read()
                text = text.split(HOMEWORK)[0]       # 作业段落只作示意，不参与
                blocks = [b for b in FENCE.findall(text) if "❌" not in b]
                if not blocks:
                    continue
                code = "\n\n".join(blocks)
                label = "%s/%s（正文代码块）" % (vol, name)
                feed = DEFAULT_FEED
                for key, val in CHAPTER_FEED.items():
                    if key in name:
                        feed = val
                out = run_script(work, "_md_blocks.py", code, problems, label, feed)
                if out is not None:
                    checked += check_source(code, out, problems, label)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    if problems:
        print("示例校验未通过（共 %d 处）：\n" % len(problems))
        for x in problems:
            print("  - " + x)
        return 1

    print("示例校验通过：运行 %d 个脚本，核对 %d 处注释输出，全部一致。"
          % (ran, checked))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--capture-output":
        capture_output(sys.argv[2], sys.argv[3])
    else:
        sys.exit(main())
