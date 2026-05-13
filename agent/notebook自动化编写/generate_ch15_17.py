#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from novel_agent import NovelWritingAgent

def main():
    agent = NovelWritingAgent(
        novel_title="工作摸鱼，竟穿越回修仙世界",
        description="都市打工人陆桢，因薪资微薄而选择躺平摸鱼。一次加班熬夜后，他意外穿越到了修仙世界，获得了「摸鱼修仙系统」。从此，他开始了一边摸鱼一边修仙的奇妙之旅。系统可以将摸鱼行为转化为修仙资源，让他在修仙路上事半功倍。",
        genre="现代都市+古风修仙",
        protagonist_name="陆桢",
        words_per_chapter=6000,
        total_chapters=500,
        model_name="deepseek-v4-pro"
    )
    
    agent.set_reference_style("凡人修仙传")
    
    chapters = [
        {"number": 15, "title": "坊市之行"},
        {"number": 16, "title": "炼气三层"},
        {"number": 17, "title": "外门弟子的心思"},
    ]
    
    for ch in chapters:
        print(f"\n正在生成第{ch['number']}章「{ch['title']}」（含修仙系统）...")
        result = agent.generate_chapter(chapter_num=ch["number"], chapter_title=ch["title"])
        print(f"第{ch['number']}章完成，约{len(result['content'])}字")
    
    agent.save_metadata()
    agent.list_chapters()

if __name__ == "__main__":
    main()
