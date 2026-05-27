#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法学引注分析工具
基于《法学引注手册（第二版）》

功能：
1. 识别引注类型
2. 提取已有要素
3. 检查缺失要素
4. 检测格式错误
5. 生成修正建议
"""

import re
import json
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class CitationType(Enum):
    """引注类型枚举"""
    UNKNOWN = "未知类型"
    CHINESE_BOOK = "中文专著"
    CHINESE_TRANSLATION = "中文译著"
    JOURNAL_ARTICLE = "期刊论文"
    COLLECTION_ARTICLE = "文集论文"
    NEWSPAPER_ARTICLE = "报纸文章"
    ANCIENT_BOOK = "古籍文献"
    ONLINE_SOURCE = "网络文献"
    THESIS = "学位论文"
    CONFERENCE_PAPER = "会议论文"
    LEGAL_STATUTE = "法律条文"
    REGULATION = "规范性文件"
    JUDICIAL_CASE = "司法案例"
    ENGLISH_BOOK = "英文图书"
    ENGLISH_ARTICLE = "英文期刊"
    ENGLISH_CASE = "英文案例"
    OTHER_FOREIGN = "其他外文文献"


@dataclass
class CitationElement:
    """引注要素"""
    name: str
    value: str = ""
    required: bool = True
    present: bool = False


@dataclass
class CitationAnalysis:
    """引注分析结果"""
    original_text: str
    citation_type: CitationType
    elements: List[CitationElement] = field(default_factory=list)
    format_errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    corrected_text: str = ""


class CitationAnalyzer:
    """引注分析器"""
    
    def __init__(self):
        self.type_patterns = self._init_type_patterns()
    
    def _init_type_patterns(self) -> Dict[CitationType, List[str]]:
        """初始化类型识别模式"""
        return {
            CitationType.CHINESE_TRANSLATION: [
                r'\[[美英德日法俄]\]',  # 国别标识
                r'[译譯]\s*[，,]',  # 译者标识
            ],
            CitationType.JOURNAL_ARTICLE: [
                r'载[《\']',  # "载"字 + 期刊名
                r'第\s*\d+\s*期',  # 期数
            ],
            CitationType.COLLECTION_ARTICLE: [
                r'载.*主编',  # 载 + 主编
                r'载.*编[《\']',  # 载 + 编 + 书名
            ],
            CitationType.NEWSPAPER_ARTICLE: [
                r'载[《\'].*报[》\']',  # 报纸名
                r'第\s*\d+\s*版',  # 版次
            ],
            CitationType.LEGAL_STATUTE: [
                r'[《\'][^《》\']*[法典律条例规定][》\'].*第\s*\d+\s*条',  # 法律名 + 条号
            ],
            CitationType.JUDICIAL_CASE: [
                r'诉',  # "诉"字
                r'判决书',  # 判决书
                r'法院.*号',  # 法院 + 案号
            ],
            CitationType.ONLINE_SOURCE: [
                r'http[s]?://',  # URL
                r'访问',  # 访问日期
                r'微信公众号',  # 微信公众号
            ],
            CitationType.THESIS: [
                r'学位论文',  # 学位论文标识
                r'博士|硕士',  # 学位类型
            ],
            CitationType.CONFERENCE_PAPER: [
                r'会议论文',  # 会议论文标识
                r'研讨会|学术会议',  # 会议类型
            ],
            CitationType.ANCIENT_BOOK: [
                r'[（(][宋明清汉唐][）)]',  # 朝代
                r'点校|校注|整理',  # 整理方式
            ],
            CitationType.ENGLISH_CASE: [
                r'\d+\s+[A-Z][a-zA-Z\.]*\s+\d+',  # 卷号 报告 页码
                r'v\.\s*[A-Z]',  # v. + 当事人
            ],
            CitationType.ENGLISH_ARTICLE: [
                r'\d+\s+[A-Z][a-zA-Z\s]+\d+\s*\(\d{4}\)',  # 卷号 期刊 页码 (年份)
            ],
            CitationType.ENGLISH_BOOK: [
                r'[A-Z][a-z]+,\s*\*[A-Z]',  # 作者, *书名（斜体）
            ],
        }
    
    def identify_type(self, text: str) -> CitationType:
        """识别引注类型"""
        scores = {t: 0 for t in CitationType}
        
        for citation_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    scores[citation_type] += 1
        
        # 特殊判断：如果有国别标识且有"译"，优先判断为译著
        if scores[CitationType.CHINESE_TRANSLATION] >= 2:
            return CitationType.CHINESE_TRANSLATION
        
        # 特殊判断：如果有"第X条"且像法律名称
        if re.search(r'[《\'][^《》\']*[法典律条例规定][》\']', text) and \
           re.search(r'第\s*\d+\s*条', text):
            return CitationType.LEGAL_STATUTE
        
        # 选择得分最高的类型
        max_score = max(scores.values())
        if max_score > 0:
            for t, s in scores.items():
                if s == max_score:
                    return t
        
        # 默认判断为中文专著
        if '《' in text and '出版社' in text:
            return CitationType.CHINESE_BOOK
        
        return CitationType.UNKNOWN
    
    def extract_elements(self, text: str, citation_type: CitationType) -> List[CitationElement]:
        """提取引注要素"""
        elements = []
        
        if citation_type == CitationType.CHINESE_BOOK:
            elements = self._extract_chinese_book_elements(text)
        elif citation_type == CitationType.CHINESE_TRANSLATION:
            elements = self._extract_translation_elements(text)
        elif citation_type == CitationType.JOURNAL_ARTICLE:
            elements = self._extract_journal_elements(text)
        elif citation_type == CitationType.LEGAL_STATUTE:
            elements = self._extract_legal_statute_elements(text)
        elif citation_type == CitationType.JUDICIAL_CASE:
            elements = self._extract_case_elements(text)
        elif citation_type == CitationType.ONLINE_SOURCE:
            elements = self._extract_online_elements(text)
        elif citation_type == CitationType.THESIS:
            elements = self._extract_thesis_elements(text)
        elif citation_type == CitationType.ENGLISH_BOOK:
            elements = self._extract_english_book_elements(text)
        elif citation_type == CitationType.ENGLISH_ARTICLE:
            elements = self._extract_english_article_elements(text)
        else:
            elements = self._extract_generic_elements(text)
        
        return elements
    
    def _extract_chinese_book_elements(self, text: str) -> List[CitationElement]:
        """提取中文专著要素"""
        elements = [
            CitationElement("作者", required=True),
            CitationElement("著作方式", required=False),
            CitationElement("书名", required=True),
            CitationElement("版次", required=False),
            CitationElement("出版社", required=True),
            CitationElement("年份", required=True),
            CitationElement("页码", required=False),
        ]
        
        # 提取作者（在书名号之前，以冒号或《分隔）
        author_match = re.search(r'^([^：《]+)[：《]', text)
        if author_match:
            elements[0].value = author_match.group(1).strip()
            elements[0].present = True
        
        # 提取著作方式
        method_match = re.search(r'(主编|编著|编|著)', text)
        if method_match:
            elements[1].value = method_match.group(1)
            elements[1].present = True
        
        # 提取书名
        title_match = re.search(r'《([^》]+)》', text)
        if title_match:
            elements[2].value = title_match.group(1)
            elements[2].present = True
        
        # 提取版次
        edition_match = re.search(r'[（(]第(\d+)版[）)]', text)
        if edition_match:
            elements[3].value = f"第{edition_match.group(1)}版"
            elements[3].present = True
        
        # 提取出版社
        publisher_match = re.search(r'》\s*[，,]?\s*([^，,\d]+出版社)', text)
        if publisher_match:
            elements[4].value = publisher_match.group(1).strip()
            elements[4].present = True
        
        # 提取年份
        year_match = re.search(r'(\d{4})年', text)
        if year_match:
            elements[5].value = year_match.group(1) + "年"
            elements[5].present = True
        
        # 提取页码
        page_match = re.search(r'第(\d+)[-—－]*(\d*)页', text)
        if page_match:
            if page_match.group(2):
                elements[6].value = f"第{page_match.group(1)}-{page_match.group(2)}页"
            else:
                elements[6].value = f"第{page_match.group(1)}页"
            elements[6].present = True
        
        return elements
    
    def _extract_translation_elements(self, text: str) -> List[CitationElement]:
        """提取译著要素"""
        elements = self._extract_chinese_book_elements(text)
        
        # 插入国别和原作者要素
        elements.insert(0, CitationElement("国别", required=True))
        elements.insert(1, CitationElement("原作者", required=True))
        elements.insert(3, CitationElement("译者", required=True))
        
        # 提取国别
        country_match = re.search(r'\[([美英德日法俄][国國]?)\]', text)
        if country_match:
            elements[0].value = country_match.group(1)
            elements[0].present = True
        
        # 提取原作者（在国别之后、书名号之前）
        original_author_match = re.search(r'\[[^\]]+\]([^：《]+)[：《]', text)
        if original_author_match:
            elements[1].value = original_author_match.group(1).strip()
            elements[1].present = True
        
        # 提取译者
        translator_match = re.search(r'》\s*[，,]?\s*([^，,]+)[译譯]', text)
        if translator_match:
            elements[3].value = translator_match.group(1).strip() + "译"
            elements[3].present = True
        
        return elements
    
    def _extract_journal_elements(self, text: str) -> List[CitationElement]:
        """提取期刊论文要素"""
        elements = [
            CitationElement("作者", required=True),
            CitationElement("论文名", required=True),
            CitationElement("期刊名", required=True),
            CitationElement("年份", required=True),
            CitationElement("期数", required=True),
            CitationElement("页码", required=False),
        ]
        
        # 提取作者
        author_match = re.search(r'^([^：《]+)[：《]', text)
        if author_match:
            elements[0].value = author_match.group(1).strip()
            elements[0].present = True
        
        # 提取论文名
        title_match = re.search(r'《([^》]+)》', text)
        if title_match:
            elements[1].value = title_match.group(1)
            elements[1].present = True
        
        # 提取期刊名
        journal_match = re.search(r'载[《\']([^》\']+)[》\']', text)
        if journal_match:
            elements[2].value = journal_match.group(1)
            elements[2].present = True
        
        # 提取年份和期数
        year_issue_match = re.search(r'(\d{4})年\s*第\s*(\d+)\s*期', text)
        if year_issue_match:
            elements[3].value = year_issue_match.group(1) + "年"
            elements[3].present = True
            elements[4].value = f"第{year_issue_match.group(2)}期"
            elements[4].present = True
        
        # 提取页码
        page_match = re.search(r'第(\d+)页', text)
        if page_match:
            elements[5].value = f"第{page_match.group(1)}页"
            elements[5].present = True
        
        return elements
    
    def _extract_legal_statute_elements(self, text: str) -> List[CitationElement]:
        """提取法律条文要素"""
        elements = [
            CitationElement("法律名称", required=True),
            CitationElement("修改年份", required=False),
            CitationElement("条号", required=True),
            CitationElement("款", required=False),
            CitationElement("项", required=False),
            CitationElement("废止标注", required=False),
        ]
        
        # 提取法律名称（包括可能的修改年份）
        law_match = re.search(r'[《\']([^》\']+[法典律条例规定])[》\']\s*(?:[（(](\d{4})年[修修][正订][）)])?', text)
        if law_match:
            elements[0].value = law_match.group(1)
            elements[0].present = True
            if law_match.group(2):
                elements[1].value = law_match.group(2) + "年"
                elements[1].present = True
        
        # 提取条号、款、项
        article_match = re.search(r'第\s*(\d+)\s*条(?:\s*第\s*(\d+)\s*款)?(?:\s*第\s*(\d+)\s*项)?', text)
        if article_match:
            elements[2].value = f"第{article_match.group(1)}条"
            elements[2].present = True
            if article_match.group(2):
                elements[3].value = f"第{article_match.group(2)}款"
                elements[3].present = True
            if article_match.group(3):
                elements[4].value = f"第{article_match.group(3)}项"
                elements[4].present = True
        
        # 检查废止标注
        if '已废止' in text or '已失效' in text:
            elements[5].value = "已废止"
            elements[5].present = True
        
        return elements
    
    def _extract_case_elements(self, text: str) -> List[CitationElement]:
        """提取司法案例要素"""
        elements = [
            CitationElement("当事人", required=True),
            CitationElement("法院", required=True),
            CitationElement("案号", required=True),
            CitationElement("判决书类型", required=False),
            CitationElement("来源", required=False),
        ]
        
        # 提取当事人（在"诉"字前后）
        parties_match = re.search(r'^(.+?)(?:等)?诉(.+?)(?:等)?案', text)
        if parties_match:
            elements[0].value = f"{parties_match.group(1)}诉{parties_match.group(2)}"
            elements[0].present = True
        
        # 提取法院和案号
        court_match = re.search(r'([^，,]+法院)[（(](\d{4}|20XX)[）)]([^号]+)号', text)
        if court_match:
            elements[1].value = court_match.group(1)
            elements[1].present = True
            elements[2].value = f"({court_match.group(2)}){court_match.group(3)}号"
            elements[2].present = True
        
        # 提取判决书类型
        type_match = re.search(r'(民事|刑事|行政)判决书', text)
        if type_match:
            elements[3].value = type_match.group(1) + "判决书"
            elements[3].present = True
        
        # 提取来源（如《最高人民法院公报》）
        source_match = re.search(r'载[《\']([^》\']+)[》\']', text)
        if source_match:
            elements[4].value = source_match.group(1)
            elements[4].present = True
        
        return elements
    
    def _extract_online_elements(self, text: str) -> List[CitationElement]:
        """提取网络文献要素"""
        elements = [
            CitationElement("作者", required=False),
            CitationElement("文章名", required=True),
            CitationElement("网站/平台", required=True),
            CitationElement("发布日期", required=False),
            CitationElement("网址", required=True),
            CitationElement("访问日期", required=True),
        ]
        
        # 提取作者和文章名
        author_title_match = re.search(r'^([^：《]+)[：《]《([^》]+)》', text)
        if author_title_match:
            elements[0].value = author_title_match.group(1).strip()
            elements[0].present = True
            elements[1].value = author_title_match.group(2)
            elements[1].present = True
        else:
            title_match = re.search(r'《([^》]+)》', text)
            if title_match:
                elements[1].value = title_match.group(1)
                elements[1].present = True
        
        # 提取网站/平台
        if '微信公众号' in text:
            wechat_match = re.search(r'微信公众号["""\']([^"""\']+)["""\']', text)
            if wechat_match:
                elements[2].value = f"微信公众号\"{wechat_match.group(1)}\""
                elements[2].present = True
        else:
            site_match = re.search(r'载([^，,]+)[，,]', text)
            if site_match:
                elements[2].value = site_match.group(1).strip()
                elements[2].present = True
        
        # 提取日期
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if date_match:
            date_str = f"{date_match.group(1)}年{date_match.group(2)}月{date_match.group(3)}日"
            if '访问' in text:
                elements[5].value = date_str
                elements[5].present = True
            else:
                elements[3].value = date_str
                elements[3].present = True
        
        # 提取网址
        url_match = re.search(r'(http[s]?://[^\s，,]+)', text)
        if url_match:
            elements[4].value = url_match.group(1)
            elements[4].present = True
        
        return elements
    
    def _extract_thesis_elements(self, text: str) -> List[CitationElement]:
        """提取学位论文要素"""
        elements = [
            CitationElement("作者", required=True),
            CitationElement("论文名", required=True),
            CitationElement("学校", required=True),
            CitationElement("年份", required=True),
            CitationElement("学位类型", required=False),
            CitationElement("页码", required=False),
        ]
        
        # 提取作者
        author_match = re.search(r'^([^：《]+)[：《]', text)
        if author_match:
            elements[0].value = author_match.group(1).strip()
            elements[0].present = True
        
        # 提取论文名
        title_match = re.search(r'《([^》]+)》', text)
        if title_match:
            elements[1].value = title_match.group(1)
            elements[1].present = True
        
        # 提取学校、年份、学位类型
        school_match = re.search(r'([^，,\d]+大学|研究院)(\d{4})年(博士|硕士)?学位论文', text)
        if school_match:
            elements[2].value = school_match.group(1)
            elements[2].present = True
            elements[3].value = school_match.group(2) + "年"
            elements[3].present = True
            if school_match.group(3):
                elements[4].value = school_match.group(3) + "学位论文"
                elements[4].present = True
        
        # 提取页码
        page_match = re.search(r'第(\d+)页', text)
        if page_match:
            elements[5].value = f"第{page_match.group(1)}页"
            elements[5].present = True
        
        return elements
    
    def _extract_english_book_elements(self, text: str) -> List[CitationElement]:
        """提取英文图书要素"""
        elements = [
            CitationElement("Author", required=True),
            CitationElement("Title", required=True),
            CitationElement("Edition", required=False),
            CitationElement("Publisher", required=True),
            CitationElement("Year", required=True),
            CitationElement("Page", required=False),
        ]
        
        # 提取作者
        author_match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z]\.?\s*[A-Z][a-z]+)?)', text)
        if author_match:
            elements[0].value = author_match.group(1)
            elements[0].present = True
        
        # 提取书名（斜体或首字母大写）
        title_match = re.search(r'\*([^*]+)\*|([A-Z][a-zA-Z\s:]+(?:[A-Z][a-z]+))', text)
        if title_match:
            elements[1].value = title_match.group(1) or title_match.group(2)
            elements[1].present = True
        
        # 提取出版信息
        pub_match = re.search(r'(?:\d+\s*ed\.?\s*,\s*)?([^,\d]+(?:Press|Publisher)),?\s*(\d{4})', text)
        if pub_match:
            elements[3].value = pub_match.group(1).strip()
            elements[3].present = True
            elements[4].value = pub_match.group(2)
            elements[4].present = True
        
        # 提取页码
        page_match = re.search(r'[，,]\s*p\.?\s*(\d+[-–—]?\d*)', text)
        if page_match:
            elements[5].value = f"p. {page_match.group(1)}"
            elements[5].present = True
        
        return elements
    
    def _extract_english_article_elements(self, text: str) -> List[CitationElement]:
        """提取英文期刊要素"""
        elements = [
            CitationElement("Author", required=True),
            CitationElement("Title", required=True),
            CitationElement("Volume", required=True),
            CitationElement("Journal", required=True),
            CitationElement("Page", required=True),
            CitationElement("Year", required=True),
        ]
        
        # 提取作者
        author_match = re.search(r'^([A-Z][a-z]+(?:,\s*[A-Z]\.?)?)', text)
        if author_match:
            elements[0].value = author_match.group(1)
            elements[0].present = True
        
        # 提取期刊信息
        journal_match = re.search(r'(\d+)\s+([A-Z][a-zA-Z\s]+)\s+(\d+)(?:,\s*(\d+[-–—]?\d*))?\s*\((\d{4})\)', text)
        if journal_match:
            elements[2].value = journal_match.group(1)  # Volume
            elements[2].present = True
            elements[3].value = journal_match.group(2).strip()  # Journal
            elements[3].present = True
            elements[4].value = journal_match.group(4) or journal_match.group(3)  # Page
            elements[4].present = True
            elements[5].value = journal_match.group(5)  # Year
            elements[5].present = True
        
        return elements
    
    def _extract_generic_elements(self, text: str) -> List[CitationElement]:
        """通用要素提取"""
        elements = []
        
        # 尝试提取作者
        author_match = re.search(r'^([^：《]+)[：《]', text)
        if author_match:
            elements.append(CitationElement("作者", author_match.group(1).strip(), True, True))
        
        # 尝试提取书名/文章名
        title_match = re.search(r'《([^》]+)》', text)
        if title_match:
            elements.append(CitationElement("书名/文章名", title_match.group(1), True, True))
        
        # 尝试提取年份
        year_match = re.search(r'(\d{4})年', text)
        if year_match:
            elements.append(CitationElement("年份", year_match.group(1) + "年", True, True))
        
        return elements
    
    def check_format_errors(self, text: str, citation_type: CitationType, elements: List[CitationElement]) -> List[str]:
        """检查格式错误"""
        errors = []
        
        # 检查中文文献的数字用法
        if citation_type in [CitationType.CHINESE_BOOK, CitationType.CHINESE_TRANSLATION, 
                             CitationType.JOURNAL_ARTICLE, CitationType.LEGAL_STATUTE]:
            # 检查是否使用了中文数字表示条号
            if re.search(r'第[一二三四五六七八九十百千]+条', text):
                errors.append("条号应使用阿拉伯数字（第657条，而非第六百五十七条）")
            
            # 检查作者与书名之间的标点
            if '《' in text and not re.search(r'[：《]', text.split('《')[0]):
                errors.append("作者与书名之间应使用冒号（作者：《书名》）")
            
            # 检查出版信息格式
            if '出版社' in text and not re.search(r'出版社\d{4}年', text):
                errors.append("出版社与年份之间不应有标点（出版社1995年版）")
        
        # 检查法律条文的格式
        if citation_type == CitationType.LEGAL_STATUTE:
            # 检查是否使用了括号数字
            if re.search(r'第[（(]\d+[）)]', text):
                errors.append("条款序数应直接使用阿拉伯数字（第1款，而非第(1)款）")
        
        # 检查期刊论文
        if citation_type == CitationType.JOURNAL_ARTICLE:
            if '载' not in text:
                errors.append("期刊论文应使用'载'字连接")
        
        # 检查文集论文
        if citation_type == CitationType.COLLECTION_ARTICLE:
            if '载' not in text:
                errors.append("文集论文应使用'载'字连接")
            if not re.search(r'主编|编[《\']', text):
                errors.append("文集论文应注明编者（主编/编）")
        
        # 检查译著
        if citation_type == CitationType.CHINESE_TRANSLATION:
            if not re.search(r'\[[美英德日法俄]', text):
                errors.append("译著应标注原作者国别（[美]/[德]等）")
            if '译' not in text:
                errors.append("译著应注明译者")
        
        # 检查网络文献
        if citation_type == CitationType.ONLINE_SOURCE:
            if 'http' not in text and '微信公众号' not in text:
                errors.append("网络文献应提供网址或平台信息")
            if '访问' not in text:
                errors.append("网络文献应注明访问日期")
        
        return errors
    
    def generate_suggestions(self, citation_type: CitationType, elements: List[CitationElement], format_errors: List[str]) -> List[str]:
        """生成修正建议"""
        suggestions = []
        
        # 检查缺失的必需要素
        missing_required = [e for e in elements if e.required and not e.present]
        if missing_required:
            missing_names = "、".join([e.name for e in missing_required])
            suggestions.append(f"缺少必需要素：{missing_names}")
        
        # 针对不同类型的建议
        if citation_type == CitationType.CHINESE_BOOK:
            # 检查版次
            edition_elem = next((e for e in elements if e.name == "版次"), None)
            if edition_elem and not edition_elem.present:
                suggestions.append("如该书非初版，请补充版次信息（第X版）")
            
            # 检查页码
            page_elem = next((e for e in elements if e.name == "页码"), None)
            if page_elem and not page_elem.present:
                suggestions.append("如引用具体内容，请补充页码")
        
        elif citation_type == CitationType.LEGAL_STATUTE:
            # 检查修改年份
            year_elem = next((e for e in elements if e.name == "修改年份"), None)
            if year_elem and not year_elem.present:
                suggestions.append("如该法律经过修改，请标注修改年份")
        
        elif citation_type == CitationType.JUDICIAL_CASE:
            # 检查来源
            source_elem = next((e for e in elements if e.name == "来源"), None)
            if source_elem and not source_elem.present:
                suggestions.append("如案例来源于《公报》或指导案例，请注明")
        
        # 添加格式修正建议
        for error in format_errors:
            if "阿拉伯数字" in error:
                suggestions.append("将中文数字改为阿拉伯数字")
            elif "冒号" in error:
                suggestions.append("在作者后添加冒号")
            elif "载" in error:
                suggestions.append("添加'载'字")
        
        return suggestions
    
    def generate_corrected_text(self, text: str, citation_type: CitationType, elements: List[CitationElement]) -> str:
        """生成修正后的引注文本"""
        # 这里简化处理，实际应根据提取的要素重新组装
        corrected = text
        
        # 修正数字用法
        chinese_nums = {
            '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
            '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
            '十一': '11', '十二': '12', '二十': '20', '三十': '30',
            '百': '100', '千': '1000'
        }
        
        # 修正条号（但保留"之一"等特殊用法）
        for cn, num in chinese_nums.items():
            pattern = f'第{cn}条'
            replacement = f'第{num}条'
            corrected = re.sub(pattern, replacement, corrected)
        
        # 修正标点（简单示例）
        if citation_type in [CitationType.CHINESE_BOOK, CitationType.CHINESE_TRANSLATION]:
            # 确保作者后有冒号
            if '《' in corrected:
                parts = corrected.split('《', 1)
                if parts[0] and not parts[0].endswith('：') and not parts[0].endswith(':'):
                    # 检查是否已有冒号
                    if '：' not in parts[0] and ':' not in parts[0]:
                        corrected = parts[0] + '：《' + parts[1]
        
        return corrected
    
    def analyze(self, text: str) -> CitationAnalysis:
        """分析引注"""
        # 识别类型
        citation_type = self.identify_type(text)
        
        # 提取要素
        elements = self.extract_elements(text, citation_type)
        
        # 检查格式错误
        format_errors = self.check_format_errors(text, citation_type, elements)
        
        # 生成建议
        suggestions = self.generate_suggestions(citation_type, elements, format_errors)
        
        # 生成修正文本
        corrected_text = self.generate_corrected_text(text, citation_type, elements)
        
        return CitationAnalysis(
            original_text=text,
            citation_type=citation_type,
            elements=elements,
            format_errors=format_errors,
            suggestions=suggestions,
            corrected_text=corrected_text
        )
    
    def format_analysis(self, analysis: CitationAnalysis) -> str:
        """格式化分析结果"""
        lines = []
        
        lines.append("=" * 60)
        lines.append("引注分析报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 原始文本
        lines.append("【原始引注】")
        lines.append(analysis.original_text)
        lines.append("")
        
        # 引注类型
        lines.append(f"【引注类型】{analysis.citation_type.value}")
        lines.append("")
        
        # 已有要素
        lines.append("【已有要素】")
        present_elements = [e for e in analysis.elements if e.present]
        if present_elements:
            for elem in present_elements:
                lines.append(f"  ✓ {elem.name}：{elem.value}")
        else:
            lines.append("  （未能识别要素）")
        lines.append("")
        
        # 缺失要素
        lines.append("【缺失要素】")
        missing_required = [e for e in analysis.elements if e.required and not e.present]
        missing_optional = [e for e in analysis.elements if not e.required and not e.present]
        
        if missing_required:
            lines.append("  必需（必须补充）：")
            for elem in missing_required:
                lines.append(f"  ✗ {elem.name}")
        
        if missing_optional:
            lines.append("  可选（建议补充）：")
            for elem in missing_optional:
                lines.append(f"  △ {elem.name}")
        
        if not missing_required and not missing_optional:
            lines.append("  （要素完整）")
        lines.append("")
        
        # 格式问题
        if analysis.format_errors:
            lines.append("【格式问题】")
            for error in analysis.format_errors:
                lines.append(f"  ⚠ {error}")
            lines.append("")
        
        # 修正建议
        if analysis.suggestions:
            lines.append("【修正建议】")
            for suggestion in analysis.suggestions:
                lines.append(f"  → {suggestion}")
            lines.append("")
        
        # 修正后的文本
        if analysis.corrected_text != analysis.original_text:
            lines.append("【修正后的引注】")
            lines.append(analysis.corrected_text)
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='法学引注分析工具')
    parser.add_argument('citation', nargs='?', help='要分析的引注文本')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    # 如果没有提供参数，从标准输入读取
    if args.citation:
        text = args.citation
    else:
        print("请输入引注文本（按Ctrl+D结束）：")
        text = sys.stdin.read().strip()
    
    if not text:
        print("错误：未提供引注文本")
        sys.exit(1)
    
    # 创建分析器并分析
    analyzer = CitationAnalyzer()
    analysis = analyzer.analyze(text)
    
    # 输出结果
    if args.json:
        result = {
            "original_text": analysis.original_text,
            "citation_type": analysis.citation_type.value,
            "elements": [
                {
                    "name": e.name,
                    "value": e.value,
                    "required": e.required,
                    "present": e.present
                }
                for e in analysis.elements
            ],
            "format_errors": analysis.format_errors,
            "suggestions": analysis.suggestions,
            "corrected_text": analysis.corrected_text
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(analyzer.format_analysis(analysis))


if __name__ == '__main__':
    main()
