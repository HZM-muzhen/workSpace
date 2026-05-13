import os
import json
import random
from datetime import datetime
from typing import Optional, List, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

REFERENCE_NOVELS = {
    "凡人修仙传": {
        "author": "忘语",
        "word_count": "747万",
        "chapters": "约2400章",
        "words_per_chapter": "2000-3000",
        "style": "凡人流开山之作，节奏沉稳，资源争夺写实，主角韩立谨慎低调，不圣母不冲动。修炼体系：炼气-筑基-结丹-元婴-化神-炼虚-合体-大乘-渡劫。核心：修仙界弱肉强食，资源有限，每一步升级都来之不易。战斗描写注重策略和道具配合，而非单纯拼修为。",
        "structure": "前期宗门生存→中期外出历练换地图→后期大世界争霸。每个地图都有完整的势力体系和资源争夺逻辑。",
        "opening_technique": "以凡人视角切入，先写主角在凡俗世界的困境，再引入修仙元素，形成强烈反差"
    },
    "仙逆": {
        "author": "耳根",
        "word_count": "651万",
        "chapters": "约2000章",
        "words_per_chapter": "2000-3500",
        "style": "逆修之道，情感浓烈。主角王林资质低微却心志如铁，'顺为凡，逆则仙'。化凡悟道段落极具哲学深度，战斗描写气势恢宏。善用意境和顿悟推动剧情。",
        "structure": "宗门起步→化凡悟道→逆天改命→仙界征战。情感线和修炼线交织，宿命感极强。",
        "opening_technique": "以悲剧开局，主角遭遇灭门之痛，仇恨驱动前行，后逐渐转向求道本心"
    },
    "遮天": {
        "author": "辰东",
        "word_count": "635万",
        "chapters": "约1800章",
        "words_per_chapter": "3000-4000",
        "style": "格局宏大，群像出色。大帝传说体系独树一帜，战斗场面气势磅礴如史诗。善写悲壮英雄和跨越万古的布局。语言有金石之气。",
        "structure": "地球开局→北斗星域→中州争霸→宇宙征战。每个大阶段都有标志性战役和人物。",
        "opening_technique": "以神秘事件（九龙拉棺）引入，将现代人与修仙世界连接，悬念极强"
    },
    "一念永恒": {
        "author": "耳根",
        "word_count": "369万",
        "chapters": "约1300章",
        "words_per_chapter": "2500-3000",
        "style": "轻松诙谐与热血并存，主角白小纯怕死又爱惹事，性格鲜明讨喜。炼丹炸炉、奇葩发明等桥段极具喜感，但关键时刻热血燃爆。",
        "structure": "宗门日常→区域争锋→大世界征伐。以搞笑日常和紧张战斗交替推进节奏。",
        "opening_technique": "以轻松搞笑的日常切入，主角的怕死性格立刻立住，读者快速产生好感"
    }
}

DEAI_WRITING_RULES = """
【去AI化写作规范——必须严格遵守】

你是一个有十年网文创作经验的老作者，不是AI助手。你的文字要有血有肉、有呼吸感。

一、语言层面：
- 禁止使用以下AI高频词：「目光如炬」「心中一震」「不禁」「缓缓」「微微」「淡淡」「仿佛」「宛如」「犹如」「恍若」「霎时」「须臾」「刹那」「蓦然」「陡然」「赫然」「竟」「居然」「竟然」——这些词出现一次就扣一分
- 用具体动作代替抽象感受：不要写"他心中一震"，写"他手里的碗差点没端住"；不要写"她不禁笑了"，写"她嘴角翘了一下，又赶紧绷住"
- 句子长短交错：短句制造紧张感，长句铺陈氛围。不要每句都差不多长
- 允许口语化表达和方言感：修仙世界的人不会说书面语，他们会说"这破事""得了吧""你扯什么"
- 破折号、省略号、感叹号要敢于用，标点也是节奏

二、叙事层面：
- 采用有限视角：主角不知道的事不要写出来，读者和主角一起发现
- 允许主角判断失误：人不是全知的，主角会看错人、会误判局势、会后悔
- 信息不要一次给完：留白，让读者自己推理，不要像百科全书一样解释设定
- 场景切换要有"断点"：不要每一段都承接得天衣无缝，留点缝隙让读者喘气

三、情感层面：
- 情绪要有过渡：人不会从平静直接跳到暴怒，中间有烦躁、忍耐、咬牙的过程
- 允许矛盾心理：主角可以又想又不想、又恨又心疼，这才是人
- 不要每段都煽情：日常对话可以无聊、可以废话、可以扯淡
- 幽默感很重要：紧张的时候来一句不靠谱的内心吐槽，比堆砌形容词强一百倍

四、结构层面：
- 章节开头不要总用环境描写，可以对话切入、动作切入、甚至直接冲突切入
- 章节结尾不要每次都留悬念，有时候平淡收尾反而更真实
- 不要每章都有高潮，有张有弛才是真节奏
- 允许"闲笔"：写点看似无关的细节，这才是生活的质感

五、修仙小说特有要求：
- 修炼体系要自洽，不要为了爽而随意加设定
- 战斗要有逻辑：为什么出这招、为什么不用那招、灵力消耗如何，要有交代
- 不要动不动就"天才""妖孽""万古无一"，标签贴多了就不值钱了
- 资源争夺要真实：修仙界不是慈善机构，没有无缘无故的好处
- 配角要有自己的逻辑：他们不是主角的NPC，有自己的利益和选择
"""

CULTIVATION_SYSTEM = """
修炼境界体系（参考凡人修仙传，有创新）：
1. 炼气期（一至九层）：感应天地灵气，引气入体，淬炼经脉
2. 筑基期（初、中、后期）：凝聚灵力筑道基，可御器飞行
3. 结丹期（初、中、后期）：灵力凝结金丹，寿元大增
4. 元婴期（初、中、后期）：元神出窍，可夺舍重生
5. 化神期（初、中、后期）：元婴化神，感悟天地法则
6. 炼虚期：炼化虚空，掌握空间之力
7. 合体期：元神与肉身合一，天人交感
8. 大乘期：道法大成，超脱凡俗
9. 渡劫期：渡天劫飞升，踏入仙道

每个大境界之间有巨大鸿沟，突破需要机缘、资源和悟性，不是闭关就能突破的。
"""


class NovelWritingAgent:
    def __init__(
        self,
        novel_title: str,
        description: str = "",
        genre: str = "古风修仙",
        target_audience: str = "网文读者",
        protagonist_name: str = "陆桢",
        words_per_chapter: int = 2500,
        total_chapters: int = 500,
        api_key: Optional[str] = None,
        model_name: str = "deepseek-v4-pro"
    ):
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("请在.env文件中设置DEEPSEEK_API_KEY")

        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0.85,
            max_tokens=8192
        )

        self.novel_title = novel_title
        self.description = description
        self.genre = genre
        self.target_audience = target_audience
        self.protagonist_name = protagonist_name
        self.words_per_chapter = words_per_chapter
        self.total_chapters = total_chapters
        self.volumes: List[Dict] = []
        self.characters: List[Dict] = []
        self.chapters: List[Dict] = []
        self.reference_style: Dict = {}
        self._reference_text: str = ""

        self.novel_dir = os.path.join("novels", novel_title.replace(" ", "_"))
        os.makedirs(self.novel_dir, exist_ok=True)

        self._load_existing_novel()

    def _load_existing_novel(self):
        metadata_file = os.path.join(self.novel_dir, "metadata.txt")
        if os.path.exists(metadata_file):
            with open(metadata_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "小说标题：" in content:
                    lines = content.split("\n")
                    for line in lines:
                        if line.startswith("小说标题："):
                            self.novel_title = line.replace("小说标题：", "").strip()
                        elif line.startswith("题材："):
                            self.genre = line.replace("题材：", "").strip()
                        elif line.startswith("主角："):
                            self.protagonist_name = line.replace("主角：", "").strip()
                        elif line.startswith("每章字数："):
                            try:
                                self.words_per_chapter = int(line.replace("每章字数：", "").strip())
                            except ValueError:
                                pass
                        elif line.startswith("总章节数："):
                            try:
                                self.total_chapters = int(line.replace("总章节数：", "").strip())
                            except ValueError:
                                pass

        volumes_file = os.path.join(self.novel_dir, "volumes.json")
        if os.path.exists(volumes_file):
            with open(volumes_file, "r", encoding="utf-8") as f:
                self.volumes = json.load(f)

        characters_file = os.path.join(self.novel_dir, "characters.txt")
        if os.path.exists(characters_file):
            with open(characters_file, "r", encoding="utf-8") as f:
                self.characters = self._parse_characters(f.read())

        self._load_existing_chapters()

    def _parse_characters(self, content: str) -> List[Dict]:
        characters = []
        for section in content.split("\n\n"):
            if ":" in section or "：" in section:
                lines = section.split("\n")
                name_line = lines[0].strip()
                if name_line:
                    sep = "：" if "：" in name_line else ":"
                    name = name_line.split(sep)[0].strip()
                    name = name.lstrip("#*-• ").strip()
                    desc = "\n".join(lines[1:]) if len(lines) > 1 else ""
                    characters.append({"name": name, "description": desc})
        return characters

    def _load_existing_chapters(self):
        if os.path.exists(self.novel_dir):
            skip_files = {"metadata.txt", "outline.txt", "characters.txt", "world_settings.txt", "reference_style.txt", "volumes.json"}
            chapter_files = sorted(
                [f for f in os.listdir(self.novel_dir) if f.endswith(".txt") and f not in skip_files]
            )
            for file in chapter_files:
                if file.startswith("第"):
                    parts = file.replace(".txt", "").split("_", 1)
                    if len(parts) == 2:
                        try:
                            chapter_num = int(parts[0].replace("第", "").replace("章", ""))
                        except ValueError:
                            continue
                        file_path = os.path.join(self.novel_dir, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        self.chapters.append({
                            "number": chapter_num,
                            "title": parts[1],
                            "content": content,
                            "file_path": file_path
                        })

    def _load_reference_file(self, novel_name: str) -> str:
        ref_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference")
        ref_file = os.path.join(ref_dir, f"{novel_name}_文风参考.txt")
        if os.path.exists(ref_file):
            with open(ref_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def set_reference_style(self, novel_name: str = "凡人修仙传") -> str:
        if novel_name in REFERENCE_NOVELS:
            self.reference_style = REFERENCE_NOVELS[novel_name]
        else:
            self.reference_style = REFERENCE_NOVELS["凡人修仙传"]

        self._reference_text = self._load_reference_file(novel_name)

        ref_file = os.path.join(self.novel_dir, "reference_style.txt")
        with open(ref_file, "w", encoding="utf-8") as f:
            f.write(f"参考作品：{novel_name}\n")
            for k, v in self.reference_style.items():
                f.write(f"{k}：{v}\n")

        print(f"已设定参考风格：{novel_name}（{self.reference_style.get('author', '')}）")
        return f"参考风格已设定为《{novel_name}》"

    def _get_reference_prompt_section(self) -> str:
        if not self.reference_style:
            self.set_reference_style("凡人修仙传")

        ref = self.reference_style
        ref_detail = self._reference_text

        result = f"""
【参考经典作品风格】
参考作品：《{ref.get('style', '凡人修仙传')}》
风格特点：{ref.get('style', '')}
结构特点：{ref.get('structure', '')}
开篇手法：{ref.get('opening_technique', '')}
每章字数参考：{ref.get('words_per_chapter', '2000-3000')}字
"""
        if ref_detail:
            result += f"""
【参考作品文风详解】
{ref_detail}
"""
        result += "\n注意：参考其节奏、结构和写作手法，但故事内容、人物、世界观必须原创创新，不要照搬情节。\n"
        return result

    def _get_system_prompt(self) -> str:
        return f"""你是一位写了十年修仙网文的老作者，笔名"墨沉"，作品累计千万字，擅长古风修仙题材。

{DEAI_WRITING_RULES}

{CULTIVATION_SYSTEM}

{self._get_reference_prompt_section()}

当前创作项目：
小说标题：《{self.novel_title}》
题材：{self.genre}
主角姓名：{self.protagonist_name}
目标读者：{self.target_audience}
小说简介：{self.description}
每章目标字数：{self.words_per_chapter}字左右
总规划：{self.total_chapters}章

你必须以老练网文作者的身份写作，文字要有烟火气、有呼吸感、有人的味道。"""

    def _get_volume_context(self, chapter_num: int) -> str:
        for vol in self.volumes:
            start = vol.get("start_chapter", 0)
            end = vol.get("end_chapter", 0)
            if start <= chapter_num <= end:
                return f"""当前所在卷：第{vol['volume_num']}卷「{vol['title']}」
卷概述：{vol['description']}
本卷修炼阶段：{vol.get('cultivation_stage', '')}
本卷核心冲突：{vol.get('core_conflict', '')}
本卷关键人物：{vol.get('key_characters', '')}
本卷章节范围：第{start}章 - 第{end}章"""
        return ""

    def _get_context_summary(self, chapter_num: int = 0) -> str:
        if not self.chapters:
            return "这是小说的开篇，没有之前的内容。"

        sorted_chapters = sorted(self.chapters, key=lambda x: x["number"])
        total = len(sorted_chapters)

        if total <= 5:
            context_parts = []
            for ch in sorted_chapters:
                snippet = ch['content'][:600] if len(ch['content']) > 600 else ch['content']
                context_parts.append(f"第{ch['number']}章「{ch['title']}」：{snippet}...")
            return "\n\n".join(context_parts)

        recent_count = min(5, total)
        recent_chapters = sorted_chapters[-recent_count:]
        older_chapters = sorted_chapters[:-recent_count]

        context_parts = []

        if older_chapters:
            phase_summaries = []
            phase_size = max(5, len(older_chapters) // 3)
            for i in range(0, len(older_chapters), phase_size):
                phase = older_chapters[i:i + phase_size]
                titles = "→".join([ch['title'] for ch in phase])
                last_in_phase = phase[-1]
                snippet = last_in_phase['content'][:300] if len(last_in_phase['content']) > 300 else last_in_phase['content']
                phase_summaries.append(f"第{phase[0]['number']}-{phase[-1]['number']}章（{titles}）：...{snippet[-200:]}")
            context_parts.append("【前文概要】\n" + "\n".join(phase_summaries))

        context_parts.append("\n【近期章节详情】")
        for ch in recent_chapters:
            snippet = ch['content'][:500] if len(ch['content']) > 500 else ch['content']
            context_parts.append(f"第{ch['number']}章「{ch['title']}」：{snippet}...")

        return "\n\n".join(context_parts)

    def _get_previous_chapter_ending(self, chapter_num: int) -> str:
        if chapter_num <= 1:
            return ""

        prev_chapter = None
        for ch in self.chapters:
            if ch["number"] == chapter_num - 1:
                prev_chapter = ch
                break

        if not prev_chapter:
            return ""

        content = prev_chapter["content"]
        last_500_chars = content[-500:] if len(content) > 500 else content

        return f"""【第{prev_chapter['number']}章结尾内容，必须自然衔接】
{last_500_chars}
请新章节从上述结尾自然过渡，保持场景、动作、情绪的连贯性。陆桢的最后动作是："""

    def _extract_last_action(self, chapter_num: int) -> str:
        prev_chapter = None
        for ch in self.chapters:
            if ch["number"] == chapter_num - 1:
                prev_chapter = ch
                break

        if not prev_chapter:
            return ""

        content = prev_chapter["content"]
        last_text = content[-300:] if len(content) > 300 else content
        lines = last_text.split("\n")
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line and len(line) > 10:
                return f"（上章结尾：{line}）"

        return ""

    def create_volumes(self, num_volumes: int = 10) -> List[Dict]:
        if not self.reference_style:
            self.set_reference_style("凡人修仙传")

        characters_text = ""
        if self.characters:
            characters_text = "\n".join([f"{c['name']}：{c['description'][:150]}" for c in self.characters[:10]])

        system_msg = f"""你是一位资深修仙网文总编，擅长规划长篇巨著。请为这部{self.total_chapters}章的修仙小说设计分卷架构。

{self._get_reference_prompt_section()}

{CULTIVATION_SYSTEM}

分卷设计要求：
1. 共{num_volumes}卷，总计约{self.total_chapters}章
2. 每卷约{self.total_chapters // num_volumes}章，但可以根据剧情需要灵活调整
3. 主角名叫{self.protagonist_name}，不要改名
4. 参考凡人修仙传的"换地图"节奏：每卷对应一个新地图/新阶段
5. 修炼进度要与卷数匹配：前几卷炼气筑基，中间结丹元婴，后期化神以上
6. 每卷要有独立的起承转合，同时是整体故事的一部分
7. 卷与卷之间要有过渡和伏笔

严格按以下JSON格式输出（不要输出其他内容）：
[{{"volume_num": 1, "title": "卷名", "start_chapter": 1, "end_chapter": 50, "cultivation_stage": "炼气期", "description": "本卷概述", "core_conflict": "核心矛盾", "key_characters": "关键人物", "setting": "场景地图"}}]"""

        human_msg = f"""小说标题：{self.novel_title}
小说简介：{self.description}
主角姓名：{self.protagonist_name}
总章节数：{self.total_chapters}
人物设定：{characters_text or f"{self.protagonist_name}：主角"}

请设计{num_volumes}卷的完整架构。"""

        from langchain_core.messages import SystemMessage, HumanMessage
        response = self.llm.invoke([
            SystemMessage(content=system_msg),
            HumanMessage(content=human_msg)
        ])
        result = response.content

        json_str = result
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        try:
            self.volumes = json.loads(json_str.strip())
        except json.JSONDecodeError:
            print("警告：卷架构JSON解析失败，尝试修复...")
            try:
                import re
                json_match = re.search(r'\[.*\]', json_str, re.DOTALL)
                if json_match:
                    self.volumes = json.loads(json_match.group())
            except Exception:
                print("错误：无法解析卷架构，请重新生成")
                return []

        volumes_file = os.path.join(self.novel_dir, "volumes.json")
        with open(volumes_file, "w", encoding="utf-8") as f:
            json.dump(self.volumes, f, ensure_ascii=False, indent=2)

        print(f"卷架构已生成并保存到：{volumes_file}")
        for vol in self.volumes:
            print(f"  第{vol['volume_num']}卷「{vol['title']}」：第{vol['start_chapter']}-{vol['end_chapter']}章（{vol['cultivation_stage']}）")

        return self.volumes

    def create_volume_outline(self, volume_num: int) -> str:
        if not self.volumes:
            print("请先创建卷架构（create_volumes）")
            return ""

        volume = None
        for v in self.volumes:
            if v["volume_num"] == volume_num:
                volume = v
                break

        if not volume:
            print(f"第{volume_num}卷不存在")
            return ""

        prev_volume_summary = ""
        if volume_num > 1:
            for v in self.volumes:
                if v["volume_num"] == volume_num - 1:
                    prev_volume_summary = f"上一卷（第{v['volume_num']}卷「{v['title']}」）概述：{v['description']}"
                    break

        characters_text = ""
        if self.characters:
            characters_text = "\n".join([f"{c['name']}：{c['description'][:150]}" for c in self.characters[:10]])

        num_chapters = volume["end_chapter"] - volume["start_chapter"] + 1

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""你是一位资深修仙网文编辑。请为以下卷设计详细的章节大纲。

{self._get_reference_prompt_section()}

{CULTIVATION_SYSTEM}

章节大纲要求：
1. 主角名叫{self.protagonist_name}
2. 本卷共{num_chapters}章（第{volume['start_chapter']}章 - 第{volume['end_chapter']}章）
3. 修炼阶段：{volume['cultivation_stage']}
4. 每章给出标题和一句话概括
5. 节奏参考凡人修仙传：日常→冲突→战斗→收获→日常（循环）
6. 不要每章都打斗，要有日常、修炼、探索、社交
7. 伏笔要埋，后面要收
8. 允许主角受挫，不要一路顺风

输出格式：
第{volume['start_chapter']}章：章节标题——一句话概括
第{volume['start_chapter']+1}章：章节标题——一句话概括
..."""),
            ("human", """小说标题：{title}
当前卷：第{volume_num}卷「{volume_title}」
卷概述：{volume_desc}
修炼阶段：{cultivation_stage}
核心冲突：{core_conflict}
关键人物：{key_characters}
场景设定：{setting}
{prev_volume}

人物设定：
{characters}

请设计本卷的详细章节大纲。""")
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "title": self.novel_title,
            "volume_num": volume_num,
            "volume_title": volume["title"],
            "volume_desc": volume["description"],
            "cultivation_stage": volume["cultivation_stage"],
            "core_conflict": volume.get("core_conflict", ""),
            "key_characters": volume.get("key_characters", ""),
            "setting": volume.get("setting", ""),
            "prev_volume": prev_volume_summary,
            "characters": characters_text or f"{self.protagonist_name}：主角"
        })

        outline_file = os.path.join(self.novel_dir, f"卷{volume_num}_outline.txt")
        with open(outline_file, "w", encoding="utf-8") as f:
            f.write(f"第{volume_num}卷「{volume['title']}」章节大纲\n")
            f.write("=" * 50 + "\n\n")
            f.write(result)

        print(f"第{volume_num}卷大纲已保存到：{outline_file}")
        return result

    def create_all_outlines(self) -> Dict[int, str]:
        if not self.volumes:
            print("请先创建卷架构（create_volumes）")
            return {}

        results = {}
        for vol in self.volumes:
            vol_num = vol["volume_num"]
            outline_file = os.path.join(self.novel_dir, f"卷{vol_num}_outline.txt")
            if os.path.exists(outline_file):
                print(f"第{vol_num}卷大纲已存在，跳过")
                with open(outline_file, "r", encoding="utf-8") as f:
                    results[vol_num] = f.read()
                continue

            print(f"\n正在生成第{vol_num}卷「{vol['title']}」大纲...")
            results[vol_num] = self.create_volume_outline(vol_num)

        return results

    def define_characters(self, characters_description: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""你是一位修仙小说人物设计师。请设计鲜活立体的人物，不要脸谱化。

{DEAI_WRITING_RULES}

小说标题：《{self.novel_title}》
小说简介：{self.description}
主角姓名：{self.protagonist_name}
总规划：{self.total_chapters}章的长篇修仙小说

人物设计要求：
1. 主角必须叫{self.protagonist_name}
2. 每个人物都要有缺点和矛盾，不要完美人设
3. 配角要有自己的目标和逻辑，不是主角的工具人
4. 人物关系要有张力：亦敌亦友、爱恨交织、利益捆绑
5. 用具体细节而非形容词堆砌：不要写"性格坚毅"，写"被打了也不吭声，第二天照常练功"
6. 因为是500章长篇，人物要有成长空间，不能一成不变

输出格式：
人物名：一句话定位
- 外貌：（2-3句具体描写，不要"眉目如画"这种空话）
- 性格：（用行为表现，不要形容词列表）
- 背景：（怎么走到今天这一步的）
- 执念：（最想要什么，最怕什么）
- 与{self.protagonist_name}的关系：（怎么认识的，什么立场）
- 成长弧线：（在500章故事中如何变化）"""),
            ("human", "{characters_input}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"characters_input": characters_description or f"请根据小说简介设计主要人物，主角叫{self.protagonist_name}"})

        characters_file = os.path.join(self.novel_dir, "characters.txt")
        with open(characters_file, "w", encoding="utf-8") as f:
            f.write(f"《{self.novel_title}》人物设定\n")
            f.write("=" * 50 + "\n\n")
            f.write(result)

        self.characters = self._parse_characters(result)
        print(f"人物设定已保存到：{characters_file}")
        return result

    def _get_chapter_title_from_outline(self, chapter_num: int) -> str:
        for vol in self.volumes:
            start = vol.get("start_chapter", 0)
            end = vol.get("end_chapter", 0)
            if start <= chapter_num <= end:
                outline_file = os.path.join(self.novel_dir, f"卷{vol['volume_num']}_outline.txt")
                if os.path.exists(outline_file):
                    with open(outline_file, "r", encoding="utf-8") as f:
                        for line in f:
                            clean = line.strip().strip("*").strip()
                            if clean.startswith(f"第{chapter_num}章") and ("：" in clean or ":" in clean):
                                for sep in ["：", ":"]:
                                    if sep in clean:
                                        parts = clean.split(sep, 1)
                                        if len(parts) == 2:
                                            title = parts[1].split("——")[0].strip()
                                            title = title.strip("*").strip()
                                            if title:
                                                return title
        return ""

    def _get_chapter_summary_from_outline(self, chapter_num: int) -> str:
        for vol in self.volumes:
            start = vol.get("start_chapter", 0)
            end = vol.get("end_chapter", 0)
            if start <= chapter_num <= end:
                outline_file = os.path.join(self.novel_dir, f"卷{vol['volume_num']}_outline.txt")
                if os.path.exists(outline_file):
                    with open(outline_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for i, line in enumerate(lines):
                        clean = line.strip().strip("*").strip()
                        if clean.startswith(f"第{chapter_num}章"):
                            summaries = []
                            for j in range(i + 1, min(i + 4, len(lines))):
                                next_line = lines[j].strip()
                                if not next_line or next_line.startswith("第") or next_line.startswith("#") or next_line.startswith("**第"):
                                    break
                                summaries.append(next_line)
                            return " ".join(summaries)
        return ""

    def _generate_chapter_with_context(self, chapter_num: int, chapter_title: str = "", specific_requirements: str = "") -> str:
        context = self._get_context_summary(chapter_num)
        volume_context = self._get_volume_context(chapter_num)

        if not chapter_title:
            chapter_title = self._get_chapter_title_from_outline(chapter_num)
        if not chapter_title:
            chapter_title = f"第{chapter_num}章"

        outline_summary = self._get_chapter_summary_from_outline(chapter_num)

        characters_hint = ""
        if self.characters:
            characters_hint = "\n".join([f"- {c['name']}：{c['description'][:200]}" for c in self.characters[:8]])

        rhythm_hints = [
            "这章节奏可以慢一点，写写日常和人物关系，别急着推剧情",
            "这章要有个小高潮，但不用大打出手，一个冲突或发现就够了",
            "这章可以写点轻松的，主角也需要喘口气",
            "这章要推进主线，但不要一口气把底牌全亮出来",
            "这章重点写人物内心，让读者看到主角的真实想法",
            "这章可以换个视角，写写配角在干什么",
            "这章写修炼和感悟，让读者感受修仙的艰辛和乐趣",
            "这章写一场战斗，但要有策略和转折，不是单纯的拼修为",
        ]
        rhythm = random.choice(rhythm_hints) if chapter_num > 1 else "开篇要稳，先让读者认识主角和世界，别急着炫设定"

        if chapter_num == 1:
            prompt = f"""{self._get_system_prompt()}

=== 第一章创作任务 ===
请创作《{self.novel_title}》的开篇章节。

参考经典修仙小说的开篇手法：{self.reference_style.get('opening_technique', '以凡人视角切入，先写困境再引入修仙元素')}

开篇要求：
- 不要一上来就大段世界观介绍，先让主角动起来
- 通过主角的处境和行动自然带出设定，不要百科全书式讲解
- 第一个场景就要有冲突或困境，让读者想看下去
- 主角{self.protagonist_name}的性格要在前几段就立住
- 章节结尾留个钩子，但不要刻意悬念

人物参考：
{characters_hint or f"主角{self.protagonist_name}，请根据简介自行设计"}

{specific_requirements if specific_requirements else ""}

节奏提示：{rhythm}

目标字数：{self.words_per_chapter}字左右

直接输出章节正文，不要标题，不要任何说明文字。"""

        else:
            outline_hint = ""
            if outline_summary:
                outline_hint = f"""
=== 大纲剧情指引 ===
本章大纲要求：{outline_summary}
请严格按照大纲剧情走向写作，不要偏离大纲的主线发展。"""

            prev_ending = self._get_previous_chapter_ending(chapter_num)
            last_action = self._extract_last_action(chapter_num)

            prompt = f"""{self._get_system_prompt()}

=== 第{chapter_num}章创作任务 ===
章节标题：{chapter_title}
{outline_hint}

{volume_context}

=== 前文回顾 ===
{context}

{prev_ending}
{last_action}

=== 章节衔接要求 ===
【重要】新章节必须从前一章结尾自然过渡！保持：
1. 场景连贯：如果上一章结尾在洗衣房，新章节开头不能直接跳到挑粪
2. 动作连贯：主角的下一个动作必须承接上一章结尾的动作
3. 时间连贯：注意时间推进的合理性（不能上章白天，下章突然晚上，除非有明确时间跳跃）
4. 情绪连贯：主角的情绪状态要延续

=== 人物参考 ===
{characters_hint or ""}

{specific_requirements if specific_requirements else ""}

节奏提示：{rhythm}

目标字数：{self.words_per_chapter}字左右

直接输出章节正文，不要标题，不要任何说明文字。"""

        response = self.llm.invoke(prompt)
        content = response.content.strip()

        content = self._deai_polish(content)
        return content

    def _deai_polish(self, content: str) -> str:
        ai_ban_list = {
            "目光如炬": "眼神锐利",
            "心中一震": "心里咯噔一下",
            "不禁": "",
            "缓缓": "慢慢",
            "微微": "",
            "淡淡": "",
            "恍若": "好像",
            "宛如": "像",
            "犹如": "像",
            "霎时": "一下子",
            "须臾": "片刻",
            "蓦然": "突然",
            "陡然": "猛地",
            "赫然": "",
        }
        for ai_word, replacement in ai_ban_list.items():
            if replacement:
                content = content.replace(ai_word, replacement)
            else:
                content = content.replace(ai_word, "")
        return content

    def generate_chapter(self, chapter_num: int = None, chapter_title: str = "", specific_requirements: str = "") -> Dict:
        if chapter_num is None:
            chapter_num = len(self.chapters) + 1

        print(f"正在生成第{chapter_num}章...")

        if not chapter_title:
            chapter_title = self._get_chapter_title_from_outline(chapter_num)
        if not chapter_title:
            chapter_title = f"第{chapter_num}章"

        content = self._generate_chapter_with_context(chapter_num, chapter_title, specific_requirements)

        chapter_info = {
            "number": chapter_num,
            "title": chapter_title,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self._save_chapter(chapter_info)
        self.chapters.append(chapter_info)

        word_count = len(content)
        print(f"第{chapter_num}章「{chapter_title}」生成完成！约{word_count}字")
        return chapter_info

    def continue_writing(self, num_chapters: int = 1, requirements: str = "") -> List[Dict]:
        results = []
        for i in range(num_chapters):
            chapter_num = len(self.chapters) + 1
            chapter = self.generate_chapter(chapter_num=chapter_num, specific_requirements=requirements)
            results.append(chapter)
            print(f"已完成 {i + 1}/{num_chapters} 章")
        return results

    def write_volume(self, volume_num: int, start_from: int = None) -> List[Dict]:
        volume = None
        for v in self.volumes:
            if v["volume_num"] == volume_num:
                volume = v
                break

        if not volume:
            print(f"第{volume_num}卷不存在")
            return []

        outline_file = os.path.join(self.novel_dir, f"卷{volume_num}_outline.txt")
        if not os.path.exists(outline_file):
            print(f"第{volume_num}卷大纲不存在，请先运行 create_volume_outline({volume_num})")
            return []

        start = start_from or volume["start_chapter"]
        end = volume["end_chapter"]

        results = []
        for ch_num in range(start, end + 1):
            existing = [ch for ch in self.chapters if ch["number"] == ch_num]
            if existing:
                print(f"第{ch_num}章已存在，跳过")
                continue

            chapter = self.generate_chapter(chapter_num=ch_num)
            results.append(chapter)

            if ch_num % 10 == 0:
                self.save_metadata()

        return results

    def rewrite_chapter(self, chapter_num: int, rewrite_requirements: str = "") -> Dict:
        old_chapter = None
        for ch in self.chapters:
            if ch["number"] == chapter_num:
                old_chapter = ch
                break

        if not old_chapter:
            print(f"第{chapter_num}章不存在")
            return None

        self.chapters.remove(old_chapter)

        new_chapter = self.generate_chapter(
            chapter_num=chapter_num,
            chapter_title=old_chapter["title"],
            specific_requirements=f"重写：{rewrite_requirements if rewrite_requirements else '保持原章节标题，让内容更自然、更有人的味道，减少AI感'}"
        )
        return new_chapter

    def _save_chapter(self, chapter_info: Dict):
        safe_title = chapter_info["title"]
        for ch in [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            safe_title = safe_title.replace(ch, "_")
        filename = f"第{chapter_info['number']}章_{safe_title}.txt"
        filepath = os.path.join(self.novel_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"第{chapter_info['number']}章 {chapter_info['title']}\n")
            f.write("=" * 50 + "\n")
            f.write(f"创建时间：{chapter_info['created_at']}\n")
            f.write(f"字数：{len(chapter_info['content'])}\n")
            f.write("=" * 50 + "\n\n")
            f.write(chapter_info["content"])

        chapter_info["file_path"] = filepath

    def save_metadata(self):
        metadata_file = os.path.join(self.novel_dir, "metadata.txt")
        total_words = sum(len(ch["content"]) for ch in self.chapters)
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(f"小说标题：{self.novel_title}\n")
            f.write(f"题材：{self.genre}\n")
            f.write(f"主角：{self.protagonist_name}\n")
            f.write(f"目标读者：{self.target_audience}\n")
            f.write(f"每章字数：{self.words_per_chapter}\n")
            f.write(f"总章节数：{self.total_chapters}\n")
            f.write(f"已完成章节：{len(self.chapters)}\n")
            f.write(f"已完成字数：{total_words}\n")
            f.write(f"简介：{self.description}\n")
            f.write(f"最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"元数据已保存到：{metadata_file}")

    def get_novel_status(self) -> str:
        total_words = sum(len(ch["content"]) for ch in self.chapters)
        progress = f"{len(self.chapters)}/{self.total_chapters}" if self.total_chapters else str(len(self.chapters))
        pct = f"{len(self.chapters) / self.total_chapters * 100:.1f}%" if self.total_chapters else "N/A"

        current_volume = "未分卷"
        for vol in self.volumes:
            if vol["start_chapter"] <= len(self.chapters) + 1 <= vol["end_chapter"]:
                current_volume = f"第{vol['volume_num']}卷「{vol['title']}」"
                break

        status = f"""
╔══════════════════════════════════════════════════╗
║        《{self.novel_title}》创作状态                  ║
╠══════════════════════════════════════════════════╣
║ 题材：{self.genre:<40}║
║ 主角：{self.protagonist_name:<40}║
║ 进度：{progress}（{pct}）{' ' * (30 - len(progress) - len(pct))}║
║ 总字数：{total_words:<40}║
║ 总卷数：{len(self.volumes):<40}║
║ 当前卷：{current_volume:<36}║
║ 人物数量：{len(self.characters):<40}║
╚══════════════════════════════════════════════════╝
"""
        if self.chapters:
            latest = self.chapters[-1]
            status += f"\n最新章节：第{latest['number']}章「{latest['title']}」（{len(latest['content'])}字）\n"
        return status

    def list_chapters(self, start: int = None, end: int = None):
        if not self.chapters:
            print("暂无章节，开始创作吧！")
            return

        display_chapters = self.chapters
        if start:
            display_chapters = [ch for ch in display_chapters if ch["number"] >= start]
        if end:
            display_chapters = [ch for ch in display_chapters if ch["number"] <= end]

        print(f"\n《{self.novel_title}》章节列表：")
        print("-" * 55)
        for chapter in display_chapters:
            wc = len(chapter["content"])
            print(f"  第{chapter['number']:3d}章：{chapter['title']}（{wc}字）")
        print("-" * 55)
        total = sum(len(ch["content"]) for ch in self.chapters)
        print(f"共 {len(self.chapters)} 章，约 {total} 字\n")

    def list_volumes(self):
        if not self.volumes:
            print("暂未创建卷架构，请先运行 create_volumes()")
            return

        print(f"\n《{self.novel_title}》卷架构：")
        print("=" * 70)
        for vol in self.volumes:
            ch_count = vol["end_chapter"] - vol["start_chapter"] + 1
            done = len([ch for ch in self.chapters if vol["start_chapter"] <= ch["number"] <= vol["end_chapter"]])
            status = "✅" if done == ch_count else f"📝 {done}/{ch_count}"
            print(f"  第{vol['volume_num']:2d}卷「{vol['title']}」第{vol['start_chapter']}-{vol['end_chapter']}章（{vol['cultivation_stage']}）{status}")
        print("=" * 70)

    def export_novel(self, format: str = "txt") -> str:
        if format == "txt":
            full_path = os.path.join(self.novel_dir, f"{self.novel_title}_完整版.txt")
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(f"《{self.novel_title}》\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"简介：{self.description}\n")
                f.write(f"主角：{self.protagonist_name}\n")
                f.write(f"总章节数：{self.total_chapters}\n\n")
                f.write("=" * 60 + "\n\n")

                for chapter in sorted(self.chapters, key=lambda x: x["number"]):
                    f.write(f"\n\n第{chapter['number']}章 {chapter['title']}\n")
                    f.write("-" * 40 + "\n\n")
                    f.write(chapter["content"])
                    f.write("\n\n")

            print(f"小说已导出到：{full_path}")
            return full_path
        else:
            raise ValueError(f"不支持的导出格式：{format}")


def create_novel_agent(
    title: str,
    description: str,
    genre: str = "古风修仙",
    protagonist_name: str = "陆桢",
    characters: str = "",
    reference_novel: str = "凡人修仙传",
    words_per_chapter: int = 2500,
    total_chapters: int = 500
) -> NovelWritingAgent:
    agent = NovelWritingAgent(
        novel_title=title,
        description=description,
        genre=genre,
        protagonist_name=protagonist_name,
        words_per_chapter=words_per_chapter,
        total_chapters=total_chapters
    )

    agent.set_reference_style(reference_novel)

    if characters:
        agent.define_characters(characters)

    return agent


if __name__ == "__main__":
    print("=" * 60)
    print("  DeepSeek-V4-Pro 修仙小说写作 Agent（500章长篇版）")
    print("=" * 60)

    agent = create_novel_agent(
        title="苍穹仙途",
        description="少年陆桢出身寒微，偶得上古仙缘，踏入修仙之途。从凡尘小镇到九天仙域，一路披荆斩棘，历经生死考验。修仙路上，有挚友相伴，有红颜知己，亦有宿敌环伺。当上古秘辛浮出水面，他才发现自己的命运早已与天地相连……",
        genre="古风修仙",
        protagonist_name="陆桢",
        characters="陆桢：16岁少年，天资聪颖却出身寒门，性格坚韧不屈\n苏晚晴：18岁，仙门天骄，冰灵根天才，外冷内热\n墨渊：千年前陨落的上古大能残魂，寄居在陆桢识海中\n楚无极：魔道天才，行事狠辣，与陆桢宿命纠缠",
        reference_novel="凡人修仙传",
        words_per_chapter=2500,
        total_chapters=500
    )

    print(agent.get_novel_status())

    print("\n正在创建10卷架构...")
    agent.create_volumes(num_volumes=10)

    agent.list_volumes()

    print("\n正在生成第1卷大纲...")
    agent.create_volume_outline(1)

    print("\n正在生成第1章...")
    ch1 = agent.generate_chapter(chapter_num=1, chapter_title="寒门少年")
    print(f"第一章完成，约{len(ch1['content'])}字")

    agent.list_chapters()
    agent.save_metadata()
