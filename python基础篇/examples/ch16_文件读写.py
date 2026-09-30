# -*- coding: utf-8 -*-
"""第 16 章 文件读写 —— 章节示例（不含「本章挑战作业」的答案）

把本章正文里出现过的代码按顺序整理在一起，可以直接运行对照。
用法：python ch16_文件读写.py

说明：运行后会在【当前目录】生成 diary.txt 和 scores.txt —— 这正是本章
      要演示的效果（数据落到磁盘上，程序关了也还在）。想清理的话，
      手动删掉这两个文件即可。最后一段“文件被写到哪儿”还会往脚本所在
      目录写一次 diary.txt（从脚本目录运行时，就是同一个文件）。

      另外补了一段正文里没有的演示：“不写 encoding 会怎样”。它会把
      系统默认编码的真实读取结果打出来 —— 在某些机器上就是乱码或
      UnicodeDecodeError。两种结果都在代码里接住了，不算报错。
"""

# ---------------------------------------------------------------
# 写文件与读文件
# ---------------------------------------------------------------

# 写：模式 "w" 是 write
with open("diary.txt", "w", encoding="utf-8") as f:
    f.write("第一天：学了变量\n")
    f.write("第二天：学了循环\n")

# 读：模式 "r" 是 read
with open("diary.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)


# ---------------------------------------------------------------
# 逐行读取
# ---------------------------------------------------------------

# 文件很大时，f.read() 一次读完可能吃力，更常用逐行遍历
with open("diary.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line, end="")     # line 自带换行符，end="" 避免双重换行


# ---------------------------------------------------------------
# 追加模式 "a"：在末尾续写，不清空
# ---------------------------------------------------------------

# 常见事故：想给文件“补充”几行却用了 "w" 模式，旧内容会被全部清空。
with open("diary.txt", "a", encoding="utf-8") as f:
    f.write("第三天：学了文件读写\n")

with open("diary.txt", "r", encoding="utf-8") as f:
    print(f.read())            # 三天的内容都在，前两行没被清掉


# ---------------------------------------------------------------
# 为什么总要写 encoding="utf-8"
# ---------------------------------------------------------------

# 不写 encoding 时，Python 用的是“系统默认编码”，它并不统一：
# Windows 中文环境常见是 GBK，macOS / Linux 通常是 UTF-8。
# 下面这份文件是按 utf-8 写进去的，再故意用系统默认编码读一次看看。
with open("diary.txt", "w", encoding="utf-8") as f:
    f.write("中文内容\n")

try:
    with open("diary.txt", "r") as f:          # 故意不写 encoding
        text = f.read().strip()
    print("用系统默认编码读出来是：", text)
    print("（和上一行原文一致，说明本机默认编码恰好也是 UTF-8；不一致就是乱码）")
except UnicodeDecodeError:
    print("用系统默认编码读取直接失败：UnicodeDecodeError")
    print("这就是不写 encoding 的风险 —— 换台电脑可能乱码或报错")

# 结论：只要 open()，就顺手写上 encoding="utf-8"
with open("diary.txt", "w", encoding="utf-8") as f:
    f.write("第一天：学了变量\n")
    f.write("第二天：学了循环\n")
    f.write("第三天：学了文件读写\n")


# ---------------------------------------------------------------
# 和异常处理配合
# ---------------------------------------------------------------

try:
    with open("notes.txt", "r", encoding="utf-8") as f:
        print(f.read())
except FileNotFoundError:
    print("文件不存在，先创建它吧")


# ---------------------------------------------------------------
# 动手：成绩存档
# ---------------------------------------------------------------

scores = [90, 85, 77, 100, 66]

# 写：文件里只能放文本，先转字符串
with open("scores.txt", "w", encoding="utf-8") as f:
    for s in scores:
        f.write(str(s) + "\n")

# 读：去掉换行符再转回整数
with open("scores.txt", "r", encoding="utf-8") as f:
    total = 0
    count = 0
    for line in f:
        total += int(line.strip())
        count += 1

print(f"共 {count} 条成绩，总分 {total}，平均分 {total / count:.1f}")


# ---------------------------------------------------------------
# 选学：更省心的路径写法（pathlib）
# ---------------------------------------------------------------

from pathlib import Path

p = Path("data") / "diary.txt"     # 用 / 拼路径，比手写字符串清楚
print(p)                            # data\diary.txt（Windows；macOS/Linux 上是 data/diary.txt）

print(p.exists())                   # False —— 文件在不在，一句话就能问
print(p.name)                       # diary.txt —— 只要文件名
print(p.suffix)                     # .txt —— 只要扩展名


# ---------------------------------------------------------------
# 选学：文件到底被写到哪儿了
# ---------------------------------------------------------------

# 相对路径相对的是“运行程序时的当前目录”，不是脚本所在目录 —— 新手最容易困惑的点
print("当前工作目录:", Path.cwd())

here = Path(__file__).parent        # 本脚本所在目录，与从哪儿运行无关
target = here / "diary.txt"
print("脚本所在目录:", here)
print("要在脚本旁边写文件，就用这个路径:", target)

# 把它交给 open()，文件就一定落在脚本旁边，不会因为从哪儿运行而跑掉
with open(target, "w", encoding="utf-8") as f:
    f.write("这次一定写在脚本旁边\n")

# 找不到自己刚写的文件时，先看 Path.cwd() 指的是哪儿 —— 不要靠猜，去看真实的值
