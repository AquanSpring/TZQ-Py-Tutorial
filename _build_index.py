# -*- coding: utf-8 -*-
"""
TZQ-Py-Tutorial 构建脚本（多篇章版）。

用法：python -X utf8 _build_index.py
- 每个"篇章"是一个 md 文件夹（如 python基础篇），文件名格式：（00）xxx.md、（01）xxx.md …
  序号补零到两位，这样在任何工具里都能正确排序（脚本本身按数字排序，不依赖文件名顺序）
- 篇章在下方 VOLUMES 里注册；文件夹不存在或没有 md 时自动跳过、主页不显示入口——
  以后添加进阶篇/实战篇：新建文件夹、放入 md、重跑本脚本即可，无需改任何代码。

【写 md 时注意：本转换器不支持下面这几种写法】
  1. 引用块（>）里不能放代码围栏——围栏会被当成普通文本原样输出；
  2. 只支持 **粗体**，不支持 *斜体*，写单星号会原样显示出来；粗体两星内侧不能贴空格
     （** x ** 会原样显示），这样正文里的 2 ** 3 这类幂运算才不会被误认成粗体；
  3. 标题最多到 ###，#### 会退化成普通段落；
  4. 代码块内部的 markdown 一律原样显示（比如 # 注释里写 **粗体**，读者会看到星号本身）；
  5. 不支持 --- 水平线和 *** 粗斜体/星号线。

1、3、5 以及单星号斜体写超了，构建时会由 lint_md 自动拦下，报错退出、不出页面，
不会静默出错；2 的贴空格粗体和 4 不报错，但会按上面的方式原样显示。
"""
import html
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))   # 本脚本所在目录，换台电脑也能直接跑
OUT = os.path.join(BASE, "index.html")

# ---------------- 篇章注册表（加新篇章只动这里 / 直接建文件夹） ----------------
VOLUMES = [
    {"slug": "basics", "name": "基础篇", "folder": "python基础篇",
     "desc": "环境搭建 → 语法规则 → 流程控制 → 数据容器 → 函数与模块 → 异常与文件 → 面向对象入门。",
     "groups": [("开始之前", [0]), ("认识 Python", [1, 2, 3]), ("基础语法", [4, 5, 6, 7, 8, 9]),
                ("数据结构", [10, 11, 12]), ("代码组织", [13, 14]),
                ("健壮与持久", [15, 16]), ("收官", [17, 18])]},
    {"slug": "advanced", "name": "进阶篇", "folder": "python进阶篇",
     "desc": "更深入的语法特性与工程实践。", "groups": []},
    {"slug": "practice", "name": "实战篇", "folder": "python实战篇",
     "desc": "完整的小项目实战演练。", "groups": []},
]

# ---------------- 行内转换 ----------------

def inline(s):
    codes = []

    def stash(m):
        content = m.group(1).replace("\\|", "|")
        codes.append(content)
        return "\x00" + str(len(codes) - 1) + "\x00"

    def make_link(url, text):
        # 走到这里 &、<、> 已经转义，唯独双引号还裸着——不补上就能逃出 href 属性
        url = url.replace('"', "&quot;")
        return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, text)

    s = re.sub(r"`([^`]+)`", stash, s)
    s = html.escape(s, quote=False)
    # 粗体两星内侧不许贴空格：正文里的 2 ** 3 这类幂运算才不会被误认成粗体
    s = re.sub(r"\*\*(?=\S)([^*]+?)(?<=\S)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: make_link(m.group(2), m.group(1)), s)
    # <网址> 自动链接：匹配到转义后的 &gt; 为止，URL 里的 &amp;（原文 &）才不会被截断
    s = re.sub(r"&lt;(https?://(?:(?!&gt;)\S)+)&gt;",
               lambda m: make_link(m.group(1), m.group(1)), s)

    def unstash(m):
        return "<code>" + html.escape(codes[int(m.group(1))], quote=False) + "</code>"

    return re.sub(r"\x00(\d+)\x00", unstash, s)

# ---------------- 代码高亮 ----------------

HL = re.compile(
    r'(?P<comment>#[^\n]*)'
    r'|(?P<string>f?"""[\s\S]*?"""'          # 三引号字符串可跨行，放在单引号前面优先匹配
    r'|f?\'\'\'[\s\S]*?\'\'\''
    r'|f?"[^"\n]*"|f?\'[^\'\n]*\')'
    r'|(?P<number>\b\d+(?:\.\d+)?\b)'
    r'|(?P<kw>\b(?:False|None|True|and|as|assert|break|class|continue|def|del|elif|else'
    r'|except|finally|for|from|global|if|import|in|is|lambda|not|or|pass|raise|return'
    r'|try|while|with|yield)\b)'
    r'|(?P<bi>\b(?:print|input|len|int|str|float|bool|type|range|sum|max|min'
    r'|sorted|open|list|dict|set|tuple|enumerate|zip|reversed|abs|any|all'
    r'|round|map|filter)\b)'
)
CLASSES = {"comment": "cm", "string": "st", "number": "nu", "kw": "kw", "bi": "bi"}


def highlight_py(code):
    out, pos = [], 0
    for m in HL.finditer(code):
        out.append(html.escape(code[pos:m.start()], quote=False))
        out.append('<span class="%s">%s</span>' % (CLASSES[m.lastgroup], html.escape(m.group(), quote=False)))
        pos = m.end()
    out.append(html.escape(code[pos:], quote=False))
    return "".join(out)


def render_code(code, lang):
    if lang == "python":
        body = highlight_py(code)
    else:
        body = html.escape(code, quote=False)
    return "<pre><code>%s</code></pre>" % body

# ---------------- 块级转换 ----------------

def parse_row(line):
    cells = line.strip().strip("|").replace("\\|", "\x01").split("|")
    return [c.replace("\x01", "|").strip() for c in cells]


def render_table(header, rows):
    th = "".join("<th>%s</th>" % inline(c) for c in header)
    body = "".join(
        "<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>" for r in rows)
    return ('<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody>'
            '</table></div>') % (th, body)


def render_list(items):
    # 缩进栈支持任意层级嵌套：新列表永远开在上一层尚未闭合的 <li> 里，
    # 所以 <li> 要等确认后面没有更深层（来了同级新项，或该层收尾）才补 </li>
    parts, stack = [], []   # stack: 从外到内依次打开的 (缩进, 标签)，stack[0] 是顶层
    for indent, marker, text in items:
        tag = "ol" if marker == "1." else "ul"
        while stack and indent < stack[-1][0]:      # 缩进退回：逐层闭合嵌套列表
            parts.append("</li></%s>" % stack.pop()[1])
        if not stack or indent > stack[-1][0]:      # 开新列表（顶层，或更深一层）
            stack.append((indent, tag))
            parts.append("<%s><li>%s" % (tag, inline(text)))
        elif stack[-1][1] == tag:                   # 同级同标签：接一个新列表项
            parts.append("</li><li>%s" % inline(text))
        else:                                       # 同级换标签：闭旧开新，仍在上一层 <li> 里
            parts.append("</li></%s>" % stack.pop()[1])
            stack.append((indent, tag))
            parts.append("<%s><li>%s" % (tag, inline(text)))
    while stack:                                    # 收尾：从最内层逐层闭合
        parts.append("</li></%s>" % stack.pop()[1])
    return "".join(parts)


def convert_md(text):
    lines = text.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            lang = line[3:].strip()
            i += 1
            code = []
            while i < n and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append(render_code("\n".join(code), lang))
            continue
        m = re.match(r"^(#{1,3}) (.+)$", line)
        if m:
            lv = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lv, inline(m.group(2).strip()), lv))
            i += 1
            continue
        if line.startswith(">"):
            quote = []
            while i < n and lines[i].startswith(">"):
                quote.append(lines[i].lstrip("> ").strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>"
                       % "<br>".join(inline(q) for q in quote if q))
            continue
        if line.lstrip().startswith("|") and i + 1 < n \
                and re.match(r"^\s*\|[\s:|-]+\|?\s*$", lines[i + 1]):
            header = parse_row(lines[i])
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append(parse_row(lines[i]))
                i += 1
            out.append(render_table(header, rows))
            continue
        if re.match(r"^\s*([-*]|\d+\.) ", line):
            items = []
            while i < n and re.match(r"^\s*([-*]|\d+\.) ", lines[i]):
                indent = len(lines[i]) - len(lines[i].lstrip())
                marker = "1." if re.match(r"^\s*\d+\. ", lines[i]) else "-"
                items.append((indent, marker,
                              re.sub(r"^\s*([-*]|\d+\.) ", "", lines[i]).strip()))
                i += 1
            out.append(render_list(items))
            continue
        if not line.strip():
            i += 1
            continue
        para = []
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,3} |>|```|\||\s*([-*]|\d+\.) )", lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline("".join(para)))
    return "\n".join(out)

# ---------------- 写作规范检查 ----------------
# 转换器支持的 md 是个受控子集，写超了会“静默地原样输出”。构建时在这里拦下，
# 把脚本头部声明的限制从口头约定变成机器检查，错误一处不修就不出页面。

def lint_md(text, where):
    errors = []
    plain, in_code = [], False
    for line in text.splitlines():
        if line.startswith("```"):          # 围栏内外规则不同：代码里的 *、# 不是排版符号
            in_code = not in_code
            continue
        if not in_code:
            plain.append(line)
    if in_code:
        errors.append("代码围栏不配对：有一处 ``` 没有闭合，它之后的内容都不会被转换")
    outside = "\n".join(plain)
    if re.search(r"(?m)^#{4,} ", outside):
        errors.append("出现了 #### 及更深的标题——转换器最多支持 ###，请降一级或改用粗体")
    # 行内代码里的 * 不是排版符号，先整体挖掉再查斜体；* 前后贴空格的是乘号不是斜体
    no_code = re.sub(r"`[^`\n]*`", "", outside)
    m = re.search(r"(?<!\*)\*(?!\s|\*)[^*\n]+?(?<!\s)\*(?!\*)", no_code)
    if m:
        errors.append("出现了单星号斜体（如 %s）——转换器只支持 **粗体**，单星号会原样显示"
                      % m.group(0)[:20])
    # 三连星要查挖代码之前的原文：**`x`** 这种“粗体包行内代码”挖掉代码后
    # 会拼出假的三连星；而三连星本身只可能是粗斜体/分隔线，星号在代码里则无关排版
    if "***" in outside:
        errors.append("出现了连续三个星号 ***——转换器不支持粗斜体/星号分隔线，请只用 **粗体**")
    if re.search(r"(?m)^\s*>?\s*-{3,}\s*$", outside):
        errors.append("出现了 --- 水平线——转换器不支持，会原样输出成一段文本，请改用标题或空行分隔")
    if re.search(r"(?m)^>\s*```", outside):
        errors.append("引用块里放了代码围栏——不会被解析，代码会原样显示，请把代码块移出引用块")
    return ["%s：%s" % (where, e) for e in errors]

# ---------------- 逐篇章构建 ----------------

chapters_all = {}      # (slug) -> {num: (title, body)}
ch_titles_all = {}     # (slug) -> {num: 短标题}
lint_errors = []       # 所有篇章的写作规范问题，攒齐了一次性报出
available = []

for vol in VOLUMES:
    folder = os.path.join(BASE, vol["folder"])
    if not os.path.isdir(folder):
        continue
    md_files = [f for f in os.listdir(folder) if f.endswith(".md")]

    # 只认「（数字）标题.md」。不符合命名的文件跳过并提示——
    # 不要因为有人往章节目录里丢了个 README.md，就让整个构建崩掉。
    numbered, skipped = [], []
    for f in md_files:
        m = re.search(r"（(\d+)）", f)
        if m:
            numbered.append((int(m.group(1)), f))
        else:
            skipped.append(f)
    for f in skipped:
        print("  [跳过] %s/%s —— 文件名里没有（数字），不参与构建" % (vol["name"], f))
    if not numbered:
        if skipped:
            raise SystemExit(
                "篇章「%s」里的 md 都不符合「（数字）标题.md」命名，无法确定章节顺序：%s"
                % (vol["name"], "、".join(sorted(skipped))))
        continue

    numbered.sort()
    seen = {}
    for num, fname in numbered:
        if num in seen:
            raise SystemExit(
                "篇章「%s」里有两章编号相同（第 %d 章）：%s 和 %s，请改成不同编号"
                % (vol["name"], num, seen[num], fname))
        seen[num] = fname

    chapters, titles = {}, {}
    for num, fname in numbered:
        text = open(os.path.join(folder, fname), encoding="utf-8").read()
        lint_errors.extend(lint_md(text, "%s/%s" % (vol["folder"], fname)))
        tm = re.search(r"(?m)^# (.+)$", text)
        if not tm:
            raise SystemExit(
                "篇章「%s」的 %s 里找不到一级标题（## 之前那行 `# 标题`），无法确定章节名"
                % (vol["name"], fname))
        title = tm.group(1).strip()
        titles[num] = title.split("：")[0]
        body = convert_md(text)
        body = re.sub(r"<h1>.+?</h1>", "", body, count=1)
        chapters[num] = (title, body)
    chapters_all[vol["slug"]] = chapters
    ch_titles_all[vol["slug"]] = titles
    available.append(vol)

if not available:
    raise SystemExit("没有任何篇章可构建：请先在篇章文件夹中放入 md 文件。")

if lint_errors:
    raise SystemExit("md 写作规范检查未通过，请先修正：\n" + "\n".join(lint_errors))

# 每卷：章节 section（含翻页器）+ 侧边栏导航 + 章节胶囊
sections_all, nav_all, cards = [], [], []

for vol in available:
    slug, name = vol["slug"], vol["name"]
    chapters = chapters_all[slug]
    titles = ch_titles_all[slug]
    nums = sorted(chapters)

    for num in nums:
        title, body = chapters[num]
        parts = []
        if num - 1 in chapters:
            parts.append('<a class="pg" href="#%s-ch%d">← 第 %d 章 · %s</a>'
                         % (slug, num - 1, num - 1, html.escape(titles[num - 1], quote=False)))
        else:
            parts.append('<a class="pg home" href="#home">⌂ 返回主页</a>')
        if num + 1 in chapters:
            parts.append('<a class="pg next" href="#%s-ch%d">第 %d 章 · %s →</a>'
                         % (slug, num + 1, num + 1, html.escape(titles[num + 1], quote=False)))
        else:
            parts.append('<a class="pg next home" href="#home">返回主页 ⌂</a>')
        pager = '<div class="pager">%s</div>' % "".join(parts)
        sections_all.append(
            '<section class="chapter" id="%s-ch%d" data-vol="%s">\n'
            '<div class="chapter-badge">%s · 第 %d 章</div>\n'
            '<h1>%s</h1>\n%s\n%s\n</section>'
            % (slug, num, slug, name, num, inline(title), body, pager))

    groups = vol["groups"] or [("章节", nums)]
    group_html = []
    for gname, gnums in groups:
        gnums = [n for n in gnums if n in chapters]
        if not gnums:
            continue
        links = "".join(
            '<a class="item" href="#%s-ch%d" data-ch="%d"><span class="n">%d</span>'
            '<span class="t">%s</span></a>'
            % (slug, n, n, n, html.escape(titles[n], quote=False)) for n in gnums)
        group_html.append('<div class="nav-group">%s</div>%s' % (gname, links))
    if not group_html:
        group_html.append('<div class="nav-group">%s</div>' % name)
        group_html.append("".join(
            '<a class="item" href="#%s-ch%d" data-ch="%d"><span class="n">%d</span>'
            '<span class="t">%s</span></a>'
            % (slug, n, n, n, html.escape(titles[n], quote=False)) for n in nums))
    nav_all.append('<div class="vol-nav" data-vol="%s">%s</div>' % (slug, "".join(group_html)))

    pills = "".join('<a class="pill" href="#%s-ch%d">第 %d 章 · %s</a>'
                    % (slug, n, n, html.escape(titles[n], quote=False)) for n in nums)
    cards.append(
        '<div class="enter-card">'
        '<div><h2>Python %s</h2><p class="desc">%s</p>'
        '<div class="pills-wrap">%s</div></div>'
        '<a class="btn btn-primary" href="#%s-ch%d">进入%s →</a>'
        '</div>' % (name, vol["desc"], pills, slug, nums[0], name))

volnames = {v["slug"]: v["name"] for v in available}

# 篇章切换芯片：只有一个篇章时不显示，两个及以上自动出现
if len(available) > 1:
    vol_chips = "".join(
        '<a class="vol-chip" data-vol="%s" href="#%s-ch%d">%s</a>'
        % (v["slug"], v["slug"], min(chapters_all[v["slug"]]), v["name"])
        for v in available)
else:
    vol_chips = ""

SAMPLE = (
    'import random\n'
    '\n'
    'secret = random.randint(1, 100)\n'
    'guess = int(input("你猜："))\n'
    '\n'
    'if guess > secret:\n'
    '    print("大了")\n'
    'elif guess < secret:\n'
    '    print("小了")\n'
    'else:\n'
    '    print(f"猜对了！答案是 {secret}")')
hero_code = highlight_py(SAMPLE)

# ---------------- 页面模板 ----------------

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- 页面本身就是深色主题：声明 color-scheme 后，浏览器的“强制深色/夜间模式”
     不会再对页面改色——否则渐变文字（background-clip:text）会被当成浅色背景压暗 -->
<meta name="color-scheme" content="dark">
<meta name="description" content="TZQ-Py-Tutorial —— 写给初学者的 Python 基础教程">
<title>TZQ-Py-Tutorial</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🐍</text></svg>">
<style>
:root{--accent:#4B8BBE;--gold:#FFD43B;--bg:#0b1220;--card:#111a2c;--card2:#0d1526;
--text:#dbe4f0;--muted:#8aa0b8;--border:#1e293b;--code-bg:#0a1020;color-scheme:dark}
*{box-sizing:border-box}
html{scrollbar-width:thin;scrollbar-color:#223047 transparent}
body{margin:0;font-family:"Segoe UI","Microsoft YaHei","PingFang SC",sans-serif;
background:radial-gradient(1100px 480px at 75% -8%,rgba(75,139,190,.16),transparent),var(--bg);
color:var(--text);line-height:1.9;font-size:16px;-webkit-tap-highlight-color:transparent}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#223047;border-radius:8px;border:2px solid #0b1220}
::-webkit-scrollbar-thumb:hover{background:#2c3e5d}
[hidden]{display:none!important}
#progress{position:fixed;top:0;left:0;height:3px;width:0;z-index:70;
background:linear-gradient(90deg,var(--accent),var(--gold))}
header.topbar{position:fixed;top:0;left:0;right:0;height:62px;background:rgba(10,16,32,.92);
-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);transform:translateZ(0);
border-bottom:1px solid var(--border);display:flex;
align-items:center;gap:14px;padding:0 22px;z-index:50}
#overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(2,6,17,.55);
z-index:54;display:none}
body.drawer-open #overlay{display:block}
body.drawer-open{overflow:hidden}
.logo{font-weight:700;font-size:19px;letter-spacing:.5px;white-space:nowrap;
color:#f1f5f9;text-decoration:none}
.logo .py{color:var(--gold)}
.sub{color:var(--muted);font-size:13.5px;white-space:nowrap}
.topbar .right{margin-left:auto;display:flex;gap:10px;align-items:center}
.home-btn,.gh{color:#cbd5e1;font-size:13.5px;text-decoration:none;
border:1px solid #2c3e5d;padding:5px 13px;border-radius:8px;white-space:nowrap}
.home-btn:hover,.gh:hover{border-color:var(--gold);color:var(--gold)}
.menu-btn{display:none;background:none;border:none;color:#fff;font-size:20px;cursor:pointer}
#sidebar{position:fixed;top:62px;left:0;bottom:0;width:288px;background:#0d1524;
border-right:1px solid var(--border);overflow-y:auto;overscroll-behavior:contain;
padding:14px 12px 24px;z-index:55}
.nav-brand{display:flex;align-items:center;gap:8px;color:#f1f5f9;font-weight:700;
padding:6px 10px 12px;font-size:15px;border-bottom:1px solid var(--border);margin-bottom:10px}
.vol-chips{display:flex;gap:8px;padding:2px 10px 12px;flex-wrap:wrap}
.vol-chip{padding:4px 12px;border-radius:999px;background:#1b2942;color:#9fb3cc;
font-size:12.5px;text-decoration:none;border:1px solid #24344f}
.vol-chip.active{background:var(--gold);color:#0f172a;border-color:var(--gold);font-weight:700}
#searchWrap{padding:0 10px 10px}
#searchBox{width:100%;box-sizing:border-box;background:#0f1930;border:1px solid #24344f;
color:#dbe4f0;border-radius:9px;padding:7px 10px;font-size:13.5px;outline:none;
font-family:inherit}
#searchBox::placeholder{color:#5b7290}
#searchBox:focus{border-color:var(--gold)}
#searchResults{padding:2px 0 8px}
#searchResults .hit-ctx{display:block;color:#5b7290;font-size:11.5px;line-height:1.5;
margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#searchResults .hit-vol{color:#7dd3fc;font-size:11px;margin-right:4px}
mark{background:rgba(255,212,59,.24);color:#ffe58a;border-radius:3px;padding:0 2px}
#searchEmpty{color:#5b7290;font-size:12.5px;padding:10px}
.nav-group{color:#5b7290;font-size:11.5px;letter-spacing:2.5px;padding:14px 10px 6px}
#sidebar a.item{display:flex;align-items:center;gap:10px;padding:7px 10px;border-radius:9px;
color:#b9c9dd;text-decoration:none;font-size:14px;line-height:1.5;border-left:3px solid transparent}
#sidebar a.item .n{flex:none;width:23px;height:23px;border-radius:7px;background:#1b2942;
color:#7dd3fc;font-size:12px;display:grid;place-items:center;font-family:Consolas,monospace}
#sidebar a.item:hover{background:#16223a;color:#fff}
#sidebar a.item.active{background:rgba(255,212,59,.1);border-left-color:var(--gold)}
#sidebar a.item.active .n{background:var(--gold);color:#0f172a;font-weight:700}
#sidebar a.item.active .t{color:var(--gold)}
#sidebar .foot{margin-top:16px;padding:12px 10px 0;border-top:1px solid var(--border);
font-size:12px;color:#5b7290;line-height:1.7}
#sidebar .foot a{color:#7d93ad;text-decoration:none}
#sidebar .foot a:hover{color:var(--gold)}
main{margin-left:288px;padding:88px 40px 60px;max-width:1000px}
/* 章节顶部位于 main 的 88px 顶栏留白之下。有了 scroll-margin，浏览器的原生锚点
   滚动（比如直接带 #章节 链接打开页面时的补滚）会正好落在页面顶部，
   而不是把页面往下顶 88px——和 route() 的归位不再打架 */
section.chapter{display:none;background:var(--card);border:1px solid var(--border);
border-radius:16px;padding:34px 42px;margin-bottom:32px;box-shadow:0 8px 24px rgba(2,6,17,.35);
scroll-margin-top:88px}
section.chapter.current{display:block}
.chapter-badge{display:inline-block;background:linear-gradient(135deg,#306998,#4B8BBE);
color:#fff;font-size:12.5px;padding:3px 13px;border-radius:999px;margin-bottom:8px;letter-spacing:1px}
h1{font-size:27px;margin:6px 0 22px;color:#f8fafc}
h2{font-size:21px;margin:34px 0 14px;padding-bottom:8px;border-bottom:1px solid #1e293b;color:#f1f5f9}
h3{font-size:17.5px;margin:24px 0 10px;color:#e2e8f0}
p{margin:10px 0}
strong{color:#f1f5f9}
a{color:#7dd3fc}
blockquote{margin:16px 0;padding:12px 18px;background:rgba(125,211,252,.06);
border-left:4px solid var(--accent);border-radius:0 10px 10px 0;color:#b9c9dd}
blockquote p{margin:0}
code{background:#1b2942;border:1px solid #24344f;padding:1px 6px;border-radius:5px;
font-family:Consolas,"Courier New",monospace;font-size:.88em;color:#7dd3fc}
pre{position:relative;background:var(--code-bg);color:#dbe4f0;border:1px solid #1e293b;
padding:16px 18px;border-radius:12px;overflow-x:auto;margin:14px 0;font-size:14px;
line-height:1.75;font-family:Consolas,"Courier New",monospace}
pre code{background:none;border:none;color:inherit;padding:0;font-size:inherit}
pre .cm{color:#64748b}
pre .kw{color:#93c5fd}
pre .bi{color:#7dd3fc}
pre .st{color:#fbbf24}
pre .nu{color:#f472b6}
.copy-btn{position:absolute;top:8px;right:8px;background:#16223a;color:#8aa0b8;
border:1px solid #2c3e5d;border-radius:6px;font-size:12px;padding:3px 10px;cursor:pointer}
.copy-btn:hover{color:var(--gold);border-color:var(--gold)}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14.5px;background:#0f1930}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
th,td{border:1px solid #223047;padding:8px 12px;text-align:left;vertical-align:top}
th{background:#16213a;color:#e2e8f0}
tr:nth-child(even) td{background:#0d1728}
ul,ol{padding-left:26px;margin:10px 0}
li{margin:4px 0}
.pager{display:flex;gap:12px;margin-top:30px;padding-top:18px;border-top:1px solid var(--border)}
.pager a{flex:1;padding:12px 16px;border:1px solid #2c3e5d;border-radius:10px;color:#cbd5e1;
text-decoration:none;font-size:14px;line-height:1.5}
.pager a:hover{border-color:var(--gold);color:var(--gold)}
.pager a.next{text-align:right;margin-left:auto}
.pager a.home{flex:0 0 auto}
footer.page-foot{color:var(--muted);font-size:13.5px;text-align:center;padding:10px 0 34px}
footer.page-foot a{color:#7dd3fc}
#backtop{position:fixed;right:26px;bottom:26px;width:44px;height:44px;border-radius:50%;
background:var(--accent);color:#fff;border:none;font-size:18px;cursor:pointer;display:none;
box-shadow:0 4px 14px rgba(2,6,17,.5);z-index:60}
#backtop.show{display:block}
#backtop:hover{background:#306998}
/* ---------- 主页 ---------- */
.hero{padding:110px 32px 70px;
background:radial-gradient(800px 420px at 18% 10%,rgba(75,139,190,.28),transparent),
linear-gradient(180deg,#0d1830 0%,var(--bg) 88%)}
.hero-inner{max-width:1140px;margin:0 auto;display:grid;
grid-template-columns:1.05fr .95fr;gap:52px;align-items:center}
.hero-tag{color:#7dd3fc;letter-spacing:3px;font-size:13px;margin-bottom:14px}
.hero h1{font-size:46px;line-height:1.25;margin:0 0 16px;color:#f8fafc;
background:linear-gradient(95deg,#f8fafc 30%,var(--gold));
-webkit-background-clip:text;background-clip:text;
/* 用 text-fill-color 而不是 color:transparent：不支持裁剪的浏览器显示纯色回退，
   强制深色模式改写 color 时也动不到填充色，渐变文字不会被压灰 */
-webkit-text-fill-color:transparent}
.hero-sub{color:#9fb3cc;font-size:17px;margin:0 0 26px}
.hero-btns{display:flex;gap:14px;flex-wrap:wrap}
.btn{display:inline-block;padding:12px 28px;border-radius:11px;font-size:16px;
font-weight:600;text-decoration:none;transition:.2s}
.btn-primary{background:linear-gradient(135deg,#306998,#4B8BBE);color:#fff;
box-shadow:0 8px 24px rgba(48,105,152,.4)}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(48,105,152,.55)}
.btn-ghost{border:1px solid #2c3e5d;color:#cbd5e1}
.btn-ghost:hover{border-color:var(--gold);color:var(--gold)}
.code-card{background:var(--code-bg);border:1px solid var(--border);border-radius:16px;
overflow:hidden;box-shadow:0 24px 60px rgba(2,6,17,.55)}
.code-card .dots{padding:11px 15px;background:#0d1526;display:flex;gap:6px;
border-bottom:1px solid var(--border)}
.code-card .dots i{width:11px;height:11px;border-radius:50%}
.code-card .dots i:nth-child(1){background:#ff5f56}
.code-card .dots i:nth-child(2){background:#ffbd2e}
.code-card .dots i:nth-child(3){background:#27c93f}
.code-card pre{margin:0;border:none;border-radius:0;background:transparent;
padding:16px 20px 20px;font-size:13.5px}
.vols{max-width:1140px;margin:20px auto 70px;padding:0 32px;display:grid;gap:22px}
.enter-card{background:linear-gradient(135deg,#13253f,#0f1a2e);border:1px solid #24344f;
border-radius:18px;padding:38px 42px;display:flex;justify-content:space-between;
align-items:center;gap:34px;flex-wrap:wrap}
.enter-card h2{margin:0 0 8px;font-size:23px;color:#f8fafc;border:none;padding:0}
.enter-card .desc{color:#9fb3cc;margin:0 0 16px;font-size:14.5px}
.pills-wrap{max-width:820px}
.pill{display:inline-block;margin:4px 6px 0 0;padding:4px 12px;border-radius:999px;
background:#0d1526;border:1px solid #24344f;color:#9fb3cc;font-size:12.5px;
text-decoration:none;transition:.15s}
.pill:hover{border-color:var(--gold);color:var(--gold)}
footer.page-foot{color:var(--muted);font-size:13.5px;text-align:center;padding:10px 0 34px}
footer.page-foot a{color:#7dd3fc}
#backtop:hover{background:#306998}
@media(max-width:1080px){.hero-inner{grid-template-columns:1fr;gap:38px}}
@media(max-width:960px){
#sidebar{transform:translateX(-105%);transition:transform .25s}
#sidebar.open{transform:none}
main{margin-left:0;padding:84px 14px 50px}
section.chapter{padding:24px 18px}
/* 主页有自己的篇章卡片导航，抽屉按钮只在教程页出现，避免点了只出遮罩不出抽屉 */
body:not(.on-home) .menu-btn{display:block}
.sub{display:none}
.hero{padding:90px 20px 50px}
.hero h1{font-size:34px}
.vols{padding:0 20px}
.enter-card{padding:28px 24px}
}
@media(max-width:640px){
.home-btn{display:none}
.gh{padding:5px 10px}
}
</style>
</head>
<body>
<div id="progress"></div>
<div id="overlay"></div>
<header class="topbar">
<button class="menu-btn" id="menuBtn">☰</button>
<a class="logo" href="#home">TZQ<span class="py">-Py</span>-Tutorial</a>
<span class="sub" id="topbarSub">从零开始的 Python 之旅</span>
<span class="right">
<a class="home-btn" href="https://github.com/AquanSpring" target="_blank" rel="noopener">GitHub 主页</a>
<a class="gh" href="https://github.com/AquanSpring/TZQ-Py-Tutorial" target="_blank" rel="noopener">GitHub 仓库</a>
</span>
</header>

<div id="home" class="view">
<section class="hero">
<div class="hero-inner">
<div class="hero-text">
<div class="hero-tag">🐍 PYTHON TUTORIAL</div>
<h1>TZQ-Py-Tutorial</h1>
<p class="hero-sub">写给初学者的 Python 基础教程——<br>把每一条语法讲透，再配一道“跳一跳才够得着”的作业。</p>
<div class="hero-btns">
<a class="btn btn-primary" href="#@@FIRST_SLUG@@-ch@@FIRST_NUM@@">开始学习 →</a>
<a class="btn btn-ghost" href="https://github.com/AquanSpring/TZQ-Py-Tutorial" target="_blank" rel="noopener">GitHub 仓库</a>
</div>
</div>
<div class="hero-code">
<div class="code-card">
<div class="dots"><i></i><i></i><i></i></div>
<pre><code>@@HEROCODE@@</code></pre>
</div>
</div>
</div>
</section>
<section class="vols">
@@VOLCARDS@@
</section>
<footer class="page-foot">TZQ-Py-Tutorial · <a href="https://github.com/AquanSpring/TZQ-Py-Tutorial" target="_blank" rel="noopener">GitHub 仓库</a> · <a href="https://github.com/AquanSpring" target="_blank" rel="noopener">作者主页 @AquanSpring</a></footer>
</div>

<div id="tutorial" class="view" hidden>
<nav id="sidebar" data-vol="@@FIRST_SLUG@@">
<div class="nav-brand">🐍 TZQ-Py-Tutorial</div>
<div id="searchWrap"><input id="searchBox" type="search" autocomplete="off"
placeholder="搜索章节标题或正文…"></div>
<div id="searchResults" hidden></div>
@@VOLCHIPS@@
@@NAV@@
<div class="foot">TZQ-Py-Tutorial · 初版<br>作者主页：<a href="https://github.com/AquanSpring" target="_blank" rel="noopener">github.com/AquanSpring</a></div>
</nav>
<main>
@@CONTENT@@
<footer class="page-foot">TZQ-Py-Tutorial · <a href="https://github.com/AquanSpring/TZQ-Py-Tutorial" target="_blank" rel="noopener">GitHub 仓库</a> · <a href="https://github.com/AquanSpring" target="_blank" rel="noopener">作者主页 @AquanSpring</a></footer>
</main>
</div>

<button id="backtop" title="回到顶部">↑</button>
<script>
const VOLNAMES=@@VOLNAMES@@;
const sidebar=document.getElementById("sidebar");
const menuBtn=document.getElementById("menuBtn");
const home=document.getElementById("home");
const tut=document.getElementById("tutorial");
const sub=document.getElementById("topbarSub");
const progress=document.getElementById("progress");
const backtop=document.getElementById("backtop");
const links=[...document.querySelectorAll('#sidebar a.item')];
const chapters=[...document.querySelectorAll("section.chapter")];
const overlay=document.getElementById("overlay");
function closeDrawer(){
sidebar.classList.remove("open");
document.body.classList.remove("drawer-open");}
menuBtn.addEventListener("click",()=>{
const open=!sidebar.classList.contains("open");
sidebar.classList.toggle("open");
document.body.classList.toggle("drawer-open",open);});
overlay.addEventListener("click",closeDrawer);
document.querySelectorAll('#sidebar a[href^="#"]').forEach(a=>{
a.addEventListener("click",closeDrawer);});
/* ---------- 侧边栏搜索：跨篇章搜标题和正文 ---------- */
const searchBox=document.getElementById("searchBox");
const searchResults=document.getElementById("searchResults");
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function escRe(s){return s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");}
/* 先把关键词包进 <mark>：两边都走 esc()，偏移量才一致 */
function hl(text,q){
const e=esc(text);
if(!q)return e;
try{return e.replace(new RegExp(escRe(esc(q)),"gi"),m=>"<mark>"+m+"</mark>");}
catch(err){return e;}
}
function clearSearch(){
searchBox.value="";
searchResults.hidden=true;
searchResults.innerHTML="";
document.querySelectorAll(".vol-nav").forEach(v=>v.hidden=(v.dataset.vol!==sidebar.dataset.vol));
}
function searchHits(q){
const hits=[];
chapters.forEach(sec=>{
const h1=sec.querySelector("h1");
const title=h1?h1.textContent.trim():"";
if(sec._txt===undefined){
const clone=sec.cloneNode(true);
clone.querySelectorAll(".pager,.chapter-badge").forEach(n=>n.remove());
sec._txt=clone.textContent.replace(/\s+/g," ");
}
const text=sec._txt;
const inTitle=title.toLowerCase().indexOf(q)>=0;
const i=text.toLowerCase().indexOf(q);
if(!inTitle&&i<0)return;
let ctx="";
if(i>=0){const s=Math.max(0,i-16);ctx=(s>0?"…":"")+text.substr(s,54).trim()+"…";}
const mt=sec.id.match(/-ch(\d+)$/);
hits.push({vol:sec.dataset.vol,num:mt?mt[1]:"",title:title,ctx:ctx});
});
return hits;
}
function runSearch(){
const q=searchBox.value.trim().toLowerCase();
if(!q){clearSearch();return;}
document.querySelectorAll(".vol-nav").forEach(v=>v.hidden=true);
const hits=searchHits(q);
if(!hits.length){
searchResults.innerHTML='<div id="searchEmpty">没有匹配的章节</div>';
searchResults.hidden=false;
return;
}
searchResults.innerHTML=hits.map(h=>
'<a class="item" href="#'+h.vol+'-ch'+h.num+'"><span class="n">'+h.num+'</span>'+
'<span class="t">'+hl(h.title,q)+
'<span class="hit-ctx"><span class="hit-vol">'+esc(VOLNAMES[h.vol]||"")+'</span>'+
hl(h.ctx,q)+'</span></span></a>').join("");
searchResults.hidden=false;
}
searchBox.addEventListener("input",runSearch);
searchBox.addEventListener("keydown",e=>{
if(e.key==="Escape"){clearSearch();searchBox.blur();}});
/* 搜索结果里的链接是动态生成的，用事件委托关抽屉 */
sidebar.addEventListener("click",e=>{
if(e.target.closest&&e.target.closest('a[href^="#"]'))closeDrawer();});
/* ---------- 接管站内锚点：掐掉浏览器原生的“滚动到章节”行为 ---------- */
/* 章节定位全靠 route() 控制，原生锚点滚动只会捣乱：
   - 点击 hash 与当前相同的链接不会触发 hashchange，浏览器却会把页面滚到那一章的
     顶部（在顶栏之下几十像素处）——表现为“再点一下同一章，页面莫名下滑一小段”；
   - 即使 hash 变了，部分浏览器也会在章节显示后补一次原生滚动，把 route() 的归位盖掉。
   所以一律 preventDefault，改为手动路由：同 hash 直接重跑 route()，不同 hash 用
   pushState 改地址（不触发原生滚动）再调 route()。 */
document.addEventListener("click",e=>{
if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
const a=e.target.closest&&e.target.closest('a[href^="#"]');
if(!a||a.target==="_blank")return;
const h=a.getAttribute("href");
if(!h||h==="#")return;
e.preventDefault();
if(location.hash===h){route();}
else{history.pushState(null,"",h);route();}
});
/* 回到顶部要连压三次：浏览器对带锚点的 URL 有可能延后补一次原生滚动
   （比如直接带着 #章节 打开页面时），单次 scrollTo 会被它盖回去 */
function forceTop(){
window.scrollTo(0,0);
requestAnimationFrame(()=>window.scrollTo(0,0));
setTimeout(()=>window.scrollTo(0,0),60);}
function route(){
const m=location.hash.match(/^#([a-z]+)-ch(\d+)$/);
/* 主页/教程页状态挂到 body 上：抽屉按钮只应在教程页出现 */
document.body.classList.toggle("on-home",!(m&&VOLNAMES[m[1]]));
if(m&&VOLNAMES[m[1]]){
home.hidden=true;tut.hidden=false;
sub.textContent="Python "+VOLNAMES[m[1]];
const vol=m[1],id=vol+"-ch"+m[2];
sidebar.dataset.vol=vol;
clearSearch();
chapters.forEach(s=>s.classList.toggle("current",s.id===id));
links.forEach(l=>l.classList.toggle("active",l.getAttribute("href")==="#"+id));
document.querySelectorAll(".vol-nav").forEach(v=>v.hidden=(v.dataset.vol!==vol));
document.querySelectorAll(".vol-chip").forEach(c=>c.classList.toggle("active",c.dataset.vol===vol));
forceTop();
closeDrawer();
}else{
tut.hidden=true;home.hidden=false;
sub.textContent="从零开始的 Python 之旅";
progress.style.width="0";
clearSearch();
forceTop();
}
}
window.addEventListener("hashchange",route);
window.addEventListener("load",route);
route();
window.addEventListener("scroll",()=>{
if(tut.hidden){progress.style.width="0";backtop.classList.remove("show");return;}
const h=document.documentElement;
progress.style.width=(h.scrollTop/(h.scrollHeight-h.clientHeight)*100)+"%";
backtop.classList.toggle("show",h.scrollTop>600);});
backtop.addEventListener("click",()=>window.scrollTo({top:0,behavior:"smooth"}));
document.querySelectorAll("#tutorial pre").forEach(pre=>{
const btn=document.createElement("button");
btn.className="copy-btn";btn.textContent="复制";
btn.addEventListener("click",async()=>{
const t=pre.innerText.replace(/\n$/,"");
try{await navigator.clipboard.writeText(t);}
catch(err){
const ta=document.createElement("textarea");ta.value=t;
document.body.appendChild(ta);ta.select();
document.execCommand("copy");ta.remove();}
btn.textContent="已复制 ✓";setTimeout(()=>btn.textContent="复制",1500);});
pre.appendChild(btn);});
</script>
</body>
</html>
"""

first = available[0]
page = (TEMPLATE
        .replace("@@NAV@@", "\n".join(nav_all))
        .replace("@@CONTENT@@", "\n".join(sections_all))
        .replace("@@VOLCARDS@@", "\n".join(cards))
        .replace("@@VOLCHIPS@@", vol_chips)
        .replace("@@VOLNAMES@@", json.dumps(volnames, ensure_ascii=False))
        .replace("@@HEROCODE@@", hero_code)
        .replace("@@FIRST_SLUG@@", first["slug"])
        .replace("@@FIRST_NUM@@", str(min(chapters_all[first["slug"]]))))

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(page)

print("篇章:", ", ".join("%s(%d章)" % (v["name"], len(chapters_all[v["slug"]])) for v in available))
print("章节 section:", page.count('<section class="chapter"'),
      " 导航项:", page.count('data-ch="'),
      " 表格:", page.count("<table>"),
      " 代码块:", page.count("<pre>"),
      " 翻页器:", page.count('class="pager"'))
print("搜索框:", page.count('id="searchBox"'), " 搜索结果容器:", page.count('id="searchResults"'))
print("未还原占位符:", page.count("\x00"), " 残留围栏:", page.count("```"))
print("输出:", OUT, "大小:", os.path.getsize(OUT), "字节")
