# -*- coding: utf-8 -*-
"""第 16 章 文件读写 —— 章节示例（不含「本章挑战作业」的答案）

把本章正文里出现过的代码按顺序整理在一起，可以直接运行对照。
用法：python ch16_文件读写.py

说明：运行后会在【当前目录】生成 diary.txt 和 scores.txt —— 这正是本章
      要演示的效果（数据落到磁盘上，程序关了也还在）。想清理的话，
      手动删掉这两个文件即可。
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
