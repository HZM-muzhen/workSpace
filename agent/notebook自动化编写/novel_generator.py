import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_deepseek import DeepSeekChat

class NovelGenerator:
    def __init__(self, novel_title: str, description: str = "", characters: str = ""):
        """
        初始化小说生成器
        
        :param novel_title: 小说标题
        :param description: 小说简介/背景设定
        :param characters: 人物设定
        """
        load_dotenv()
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("请在.env文件中设置DEEPSEEK_API_KEY")
        
        self.model = DeepSeekChat(
            model="deepseek-v4-chat",
            api_key=self.api_key,
            max_tokens=4096,
            temperature=0.7
        )
        
        self.novel_title = novel_title
        self.description = description
        self.characters = characters
        self.chapters = []
        
        # 创建小说目录
        self.novel_dir = os.path.join("novels", novel_title)
        os.makedirs(self.novel_dir, exist_ok=True)
        
        # 加载已有的章节
        self._load_existing_chapters()
    
    def _load_existing_chapters(self):
        """加载已存在的章节文件"""
        if os.path.exists(self.novel_dir):
            chapter_files = sorted([f for f in os.listdir(self.novel_dir) if f.endswith(".txt")])
            for file in chapter_files:
                chapter_num = int(file.split("_")[0])
                file_path = os.path.join(self.novel_dir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.chapters.append({
                    "number": chapter_num,
                    "title": file.replace(".txt", "").replace(f"{chapter_num}_", ""),
                    "content": content,
                    "file_path": file_path
                })
    
    def _generate_chapter_title(self, chapter_num: int, context: str) -> str:
        """生成章节标题"""
        prompt = f"""
你是一位专业的小说作家，请根据以下小说信息和上下文为第{chapter_num}章生成一个合适的章节标题：

小说标题：{self.novel_title}

小说简介：{self.description}

人物设定：{self.characters}

上下文摘要：{context}

请只返回章节标题，不需要额外解释。
"""
        response = self.model.invoke(prompt)
        return response.content.strip()
    
    def _generate_chapter_content(self, chapter_num: int, context: str) -> str:
        """生成章节内容"""
        prompt = f"""
你是一位专业的小说作家，擅长创作引人入胜的故事。请根据以下信息创作第{chapter_num}章的内容：

小说标题：{self.novel_title}

小说简介：{self.description}

人物设定：{self.characters}

之前章节的简要回顾：{context}

创作要求：
1. 章节长度适中，大约2000-3000字
2. 保持故事的连贯性和逻辑性
3. 情节要有起伏和发展
4. 人物性格要保持一致
5. 使用生动的描写和对话
6. 在章节结尾可以适当留下悬念

请直接返回章节内容，不需要额外说明。
"""
        response = self.model.invoke(prompt)
        return response.content.strip()
    
    def _get_context_summary(self) -> str:
        """获取历史章节的摘要作为上下文"""
        if not self.chapters:
            return "这是小说的第一章，没有之前的内容。"
        
        # 如果只有少数章节，返回全部内容
        if len(self.chapters) <= 3:
            context = "\n".join([f"第{ch['number']}章 {ch['title']}：{ch['content'][:500]}..." for ch in self.chapters])
            return context
        
        # 如果章节较多，只返回最近几章的摘要
        recent_chapters = self.chapters[-3:]
        context = "\n".join([f"第{ch['number']}章 {ch['title']}：{ch['content'][:500]}..." for ch in recent_chapters])
        return f"最近三章内容回顾：\n{context}"
    
    def generate_next_chapter(self) -> dict:
        """生成下一章"""
        chapter_num = len(self.chapters) + 1
        context = self._get_context_summary()
        
        print(f"正在生成第{chapter_num}章...")
        
        # 生成章节标题
        title = self._generate_chapter_title(chapter_num, context)
        print(f"章节标题：{title}")
        
        # 生成章节内容
        content = self._generate_chapter_content(chapter_num, context)
        
        # 创建章节信息
        chapter_info = {
            "number": chapter_num,
            "title": title,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存章节
        self._save_chapter(chapter_info)
        
        # 添加到章节列表
        self.chapters.append(chapter_info)
        
        print(f"第{chapter_num}章生成完成！")
        return chapter_info
    
    def _save_chapter(self, chapter_info: dict):
        """保存章节到文件"""
        # 格式化文件名：章节号_标题.txt
        safe_title = chapter_info["title"].replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = f"{chapter_info['number']}_{safe_title}.txt"
        filepath = os.path.join(self.novel_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"第{chapter_info['number']}章 {chapter_info['title']}\n")
            f.write("=" * 50 + "\n")
            f.write(f"创建时间：{chapter_info['created_at']}\n")
            f.write("=" * 50 + "\n\n")
            f.write(chapter_info["content"])
        
        chapter_info["file_path"] = filepath
    
    def get_chapter(self, chapter_num: int) -> dict:
        """获取指定章节"""
        for chapter in self.chapters:
            if chapter["number"] == chapter_num:
                return chapter
        return None
    
    def list_chapters(self):
        """列出所有章节"""
        if not self.chapters:
            print("暂无章节")
            return
        
        print(f"《{self.novel_title}》章节列表：")
        for chapter in self.chapters:
            print(f"第{chapter['number']}章：{chapter['title']}")
    
    def get_novel_summary(self) -> str:
        """获取小说摘要"""
        summary = f"小说标题：{self.novel_title}\n"
        summary += f"简介：{self.description}\n"
        summary += f"人物：{self.characters}\n"
        summary += f"章节数量：{len(self.chapters)}\n"
        if self.chapters:
            summary += f"最新章节：第{self.chapters[-1]['number']}章 {self.chapters[-1]['title']}"
        return summary

# 使用示例
if __name__ == "__main__":
    # 示例：创建一个穿越修仙小说生成器
    novel = NovelGenerator(
        novel_title="工作摸鱼，竟穿越回修仙世界",
        description="都市打工人陆桢，因薪资微薄而选择躺平摸鱼。一次上班摸鱼时，意外穿越到修仙世界，获得了独特的\"摸鱼修仙系统\"。从此，他以摸鱼之道修仙，将办公室摸鱼技巧融入修炼之中，开启了一段轻松诙谐又不失热血的修仙之旅。",
        characters="""
陆桢：男主角，24岁，从现代穿越而来的打工人，掌握摸鱼修仙之道。信奉"能躺则躺，能摸则摸"的人生哲学，拥有"摸鱼修仙系统"，可以将摸鱼行为转化为修仙资源。
楚无极：22岁，魔道年轻一辈里最能打的那个，性格乖张，亦正亦邪，与陆桢亦敌亦友。
苏晚晴：18岁，太虚仙门掌门独女，冰灵根天才，外表冷漠内心火热，对陆桢的"摸鱼修仙法"感到好奇。
墨渊：千年前的苍冥仙尊残魂，被困在玉简中千年，成为陆桢的引路人。
""")
    
    # 生成新章节
    novel.generate_next_chapter()
    
    # 列出所有章节
    novel.list_chapters()
    
    # 获取小说摘要
    print("\n小说摘要：")
    print(novel.get_novel_summary())
