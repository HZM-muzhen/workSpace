# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from novel_agent import NovelWritingAgent

script_dir = os.path.dirname(os.path.abspath(__file__))
novel_dir = os.path.join(script_dir, "novels", "工作摸鱼，竟穿越回修仙世界")

print("Step 1: 创建Agent")
agent = NovelWritingAgent(
    novel_title='工作摸鱼，竟穿越回修仙世界',
    genre='古风修仙',
    protagonist_name='陆桢',
    words_per_chapter=2500,
    total_chapters=500
)

print("Step 2: 设置小说目录")
agent.novel_dir = novel_dir

print("Step 3: 手动加载章节")
agent.chapters = []
skip_files = {"metadata.txt", "outline.txt", "characters.txt", "world_settings.txt", "reference_style.txt", "volumes.json", "小说思维导图.txt"}
chapter_files = sorted([f for f in os.listdir(novel_dir) if f.endswith(".txt") and f not in skip_files])

for file in chapter_files:
    if file.startswith("第"):
        parts = file.replace(".txt", "").split("_", 1)
        if len(parts) == 2:
            try:
                chapter_num = int(parts[0].replace("第", "").replace("章", ""))
                file_path = os.path.join(novel_dir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                agent.chapters.append({
                    "number": chapter_num,
                    "title": parts[1],
                    "content": content,
                    "file_path": file_path
                })
            except ValueError:
                continue

print(f"已加载 {len(agent.chapters)} 章")

# 加载volumes.json
import json
volumes_file = os.path.join(novel_dir, "volumes.json")
with open(volumes_file, "r", encoding="utf-8") as f:
    agent.volumes = json.load(f)

print("Step 4: 设置参考风格")
agent.set_reference_style('凡人修仙传')

print("Step 5: 检查第19章结尾")
prev_chapter = None
for ch in agent.chapters:
    if ch['number'] == 19:
        prev_chapter = ch
        break

if prev_chapter:
    print(f"第19章结尾: {prev_chapter['content'][-200:]}")

print("Step 6: 生成第20章")
chapter = agent.generate_chapter(chapter_num=20)

print(f"标题: {chapter['title']}")
print(f"字数: {len(chapter['content'])}")
print(f"文件路径: {chapter.get('file_path', '未保存')}")

# 直接保存文件
if 'file_path' in chapter:
    full_path = os.path.join(novel_dir, f"第20章_{chapter['title']}.txt")
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(f"第20章 {chapter['title']}\n")
        f.write("=" * 50 + "\n")
        f.write(f"创建时间：{chapter.get('created_at', '')}\n")
        f.write(f"字数：{len(chapter['content'])}\n")
        f.write("=" * 50 + "\n\n")
        f.write(chapter['content'])
    print(f"文件已手动保存到: {full_path}")