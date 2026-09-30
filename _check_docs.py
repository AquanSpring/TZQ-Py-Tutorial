# -*- coding: utf-8 -*-
"""
TZQ-Py-Tutorial 正文一致性检查（CI 用）。

代码能不能跑、输出对不对由 _check_examples.py 管；这个脚本管“文字之间对不对得上”，
专治那些不会被执行、因此跑不出来的错误：

1. 【词典覆盖】正文里凡是“**中文（English）**”这种术语对照写法，English 必须在
   第 0 章的“小词典”里查得到——否则读者回来查会扑空。
2. 【章节引用】正文里所有“第 N 章”必须指向真实存在的章节，防止写成不存在的章号。
3. 【词典指引】正文里凡是说“第 0 章词典里就有 X”的地方，X 必须真的在词典里。

这三类问题都不会让程序报错，只能靠检查发现。任何一处不合格即以非零码退出。

用法：python -X utf8 _check_docs.py
"""
import glob
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
# 篇章注册表在构建脚本里，这里按同样规则自动发现。
VOLUMES = [d for d in sorted(os.listdir(BASE))
           if os.path.isdir(os.path.join(BASE, d, 'examples'))]

GLOSSARY_NAME = '（00）学前基础.md'

# 术语对照里的专有名词：不是普通词汇，不要求词典收录
PROPER_NOUNS = {'python', 'cpython', 'pypy', 'jython', 'pycharm', 'vs', 'code',
                'windows', 'macos', 'linux', 'github', 'bilibili', 'idle',
                'jupyter', 'pep', 'pvm'}

BOLD = re.compile(r'\*\*(.+?)\*\*', re.S)
CN_PAREN_EN = re.compile(r'（([A-Za-z][A-Za-z0-9 .\-/]*)）')
# 章号两种写法都要认：阿拉伯数字“第 11 章”，以及中文数字“第十一章”
CHAPTER_REF = re.compile(r'第\s*(\d+|[零〇一二三四五六七八九十]+)\s*章')
DICT_REF = re.compile(r'第\s*[0零〇]\s*章[^。\n]{0,6}词典')
INLINE_CODE = re.compile(r'`([^`\n]+)`')
WORD = re.compile(r'[A-Za-z][A-Za-z\-]+')

CN_DIGIT = {'零': 0, '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def to_number(s):
    """把“11”或“十一”这样的章号转成 int；认不出返回 None。"""
    if s.isdigit():
        return int(s)
    if '十' not in s:
        return CN_DIGIT.get(s)
    head, _, tail = s.partition('十')
    tens = CN_DIGIT.get(head, 1) if head else 1
    ones = CN_DIGIT.get(tail, 0) if tail else 0
    return tens * 10 + ones


def load_glossary(voldir):
    path = os.path.join(voldir, GLOSSARY_NAME)
    if not os.path.isfile(path):
        return None, None
    text = open(path, encoding='utf-8').read()
    return text, text.lower()


def in_glossary(term, gloss_lower):
    """term 是否被词典收录：整体命中，或它的每个实词都被收录。"""
    t = term.lower().strip()
    if not t:
        return True
    if re.search(r'(?<![a-z])' + re.escape(t) + r'(?![a-z])', gloss_lower):
        return True
    words = [w for w in re.split(r'[\s\-]+', t)
             if len(w) >= 3 and w not in PROPER_NOUNS]
    if not words:
        return True
    return all(re.search(r'(?<![a-z])' + re.escape(w) + r'(?![a-z])', gloss_lower)
               for w in words)


def check_volume(vol, voldir, problems):
    text, gloss = load_glossary(voldir)
    if gloss is None:
        problems.append('%s：找不到 %s，无法做词典检查' % (vol, GLOSSARY_NAME))
        return 0

    chapter_nums = set()
    for f in os.listdir(voldir):
        m = re.search(r'（(\d+)）', f)
        if m and f.endswith('.md'):
            chapter_nums.add(int(m.group(1)))

    checked = 0
    for path in sorted(glob.glob(os.path.join(voldir, '*.md'))):
        name = os.path.basename(path)
        if name == GLOSSARY_NAME:
            continue
        lines = open(path, encoding='utf-8').read().splitlines()
        where = '%s/%s' % (vol, name)

        for i, line in enumerate(lines, 1):
            # 1. 术语对照必须能在词典里查到
            for bold in BOLD.findall(line):
                for group in CN_PAREN_EN.findall(bold):
                    for part in re.split(r'[,，/]', group):
                        part = part.strip()
                        if len(part) < 2:
                            continue
                        checked += 1
                        if not in_glossary(part, gloss):
                            problems.append(
                                '%s:%d：术语对照“%s”在第 0 章词典里查不到'
                                % (where, i, part))

            # 2. “第 N 章”必须指向真实章节（阿拉伯数字与中文数字都查）
            for raw in CHAPTER_REF.findall(line):
                num = to_number(raw)
                if num is None or num not in chapter_nums:
                    problems.append(
                        '%s:%d：引用了不存在的“第 %s 章”（本篇章只有 0~%d 章）'
                        % (where, i, raw, max(chapter_nums)))
                else:
                    checked += 1

            # 3. “第 0 章词典里就有 X”里的 X 必须真在词典里
            if DICT_REF.search(line):
                tokens = set(INLINE_CODE.findall(line))
                for group in CN_PAREN_EN.findall(line):
                    tokens.update(re.split(r'[,，/]', group))
                for tok in tokens:
                    for w in WORD.findall(tok):
                        if len(w) < 3 or w.lower() in PROPER_NOUNS:
                            continue
                        checked += 1
                        if not in_glossary(w, gloss):
                            problems.append(
                                '%s:%d：说“第 0 章词典里就有”，但 %s 并不在词典里'
                                % (where, i, w))
    return checked


def main():
    if not VOLUMES:
        raise SystemExit('没找到任何篇章目录（含 examples/ 的文件夹）')

    problems, checked = [], 0
    for vol in VOLUMES:
        checked += check_volume(vol, os.path.join(BASE, vol), problems)

    if problems:
        print('正文一致性检查未通过（共 %d 处）：\n' % len(problems))
        for x in problems:
            print('  - ' + x)
        return 1

    print('正文一致性检查通过：核对 %d 处术语与引用，全部对得上。' % checked)
    return 0


if __name__ == '__main__':
    sys.exit(main())
