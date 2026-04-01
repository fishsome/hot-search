#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推荐系统 - 权重排序 + 推荐
根据用户关注点（金融、战争、科技等）推荐新闻
"""

import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class NewsRecommender:
    """新闻推荐器"""

    def __init__(
        self,
        user_focus: Dict[str, int] = None,
        recommend_count: int = 5,
        weights_path: str = "./cache/weights.json",
    ):
        # 默认用户关注点权重
        if not user_focus:
            user_focus = {
                "finance": 3,       # 金融
                "war": 2,           # 战争
                "tech": 2,          # 科技
                "entertainment": 1, # 娱乐
                "sports": 1,        # 体育
                "politics": 1,      # 政治
                "health": 1,        # 健康
            }
        
        self.user_focus = user_focus
        self.recommend_count = recommend_count
        self.weights_path = Path(weights_path)
        
        # 关键词映射（新闻关键词 -> 关注点类别）
        self.keyword_map = {
            "finance": [
                "股票", "股市", "基金", "期货", "原油", "黄金", "比特币",
                "金融", "银行", "利率", "汇率", "经济", "GDP", "财报",
                "stock", "market", "oil", "gold", "bitcoin", "finance",
                "Iran", "sanctions", "trade",
            ],
            "war": [
                "战争", "冲突", "军事", "袭击", "导弹", "核", "武器",
                "俄罗斯", "乌克兰", "伊朗", "以色列", "加沙",
                "war", "conflict", "military", "attack", "missile",
                "Russia", "Ukraine", "Gaza",
            ],
            "tech": [
                "科技", "人工智能", "AI", "芯片", "半导体", "5G", "互联网",
                "科技", "创新", "研发", "专利",
                "technology", "AI", "chip", "semiconductor", "innovation",
                "Artemis", "NASA", "moon", "space",
            ],
            "entertainment": [
                "娱乐", "电影", "音乐", "明星", "演员", "导演", "综艺",
                "entertainment", "movie", "music", "star", "actor",
            ],
            "sports": [
                "体育", "足球", "篮球", "网球", "奥运", "比赛", "冠军",
                "sports", "football", "basketball", "tennis", "olympic",
                "Final Four", "UConn", "NCAA",
            ],
            "politics": [
                "政治", "总统", "政府", "选举", "国会", "法案", "政策",
                "politics", "president", "government", "election",
                "Trump", "Congress", "shutdown", "DHS",
            ],
            "health": [
                "健康", "医疗", "疫苗", "新冠", "病毒", "疾病",
                "health", "medical", "vaccine", "COVID",
            ],
        }
        
        # 加载权重配置
        self._load_weights()

    def recommend(
        self,
        news: List[Dict],
        count: int = None,
    ) -> List[Dict]:
        """
        推荐新闻
        
        Args:
            news: 新闻列表
            count: 推荐条数
        
        Returns:
            推荐新闻列表（按权重排序）
        """
        if not count:
            count = self.recommend_count
        
        # 计算每条新闻的权重分数
        scored_news = []
        for item in news:
            score = self._calculate_score(item)
            scored_news.append({
                "news": item,
                "score": score,
            })
        
        # 按分数降序排序
        scored_news.sort(key=lambda x: x["score"], reverse=True)
        
        # 返回推荐新闻
        recommended = [item["news"] for item in scored_news[:count]]
        
        logger.info(f"推荐 {len(recommended)} 条新闻（最高分数: {scored_news[0]['score'] if scored_news else 0}）")
        return recommended

    def _calculate_score(self, news: Dict) -> int:
        """
        计算新闻权重分数
        
        Args:
            news: 新闻数据
        
        Returns:
            权重分数
        """
        title = news.get("title", "")
        snippet = news.get("snippet", "")
        text = title + " " + snippet
        
        score = 0
        
        # 匹配关键词并计算分数
        for category, keywords in self.keyword_map.items():
            weight = self.user_focus.get(category, 1)
            
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    score += weight
                    # 匹配多个关键词时，分数累加
                    # 但限制单类别最大分数（避免过度偏向）
                    if score > weight * 3:
                        score = weight * 3
                    break
        
        return score

    def _load_weights(self) -> None:
        """
        加载权重配置
        """
        if self.weights_path.exists():
            try:
                with open(self.weights_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.user_focus = config.get("user_focus", self.user_focus)
                    logger.info(f"加载权重配置: {self.user_focus}")
            except Exception as e:
                logger.warning(f"加载权重配置失败: {e}")

    def save_weights(self) -> bool:
        """
        保存权重配置
        
        Returns:
            是否保存成功
        """
        try:
            self.weights_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                "user_focus": self.user_focus,
            }
            
            with open(self.weights_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存权重配置: {self.user_focus}")
            return True
        except Exception as e:
            logger.error(f"保存权重配置失败: {e}")
            return False

    def update_focus(
        self,
        category: str,
        weight: int,
    ) -> bool:
        """
        更新用户关注点权重
        
        Args:
            category: 类别名称
            weight: 权重值
        
        Returns:
            是否更新成功
        """
        if category in self.user_focus:
            self.user_focus[category] = weight
            self.save_weights()
            logger.info(f"更新权重: {category} -> {weight}")
            return True
        else:
            logger.warning(f"类别 {category} 不存在")
            return False


if __name__ == "__main__":
    # 测试
    recommender = NewsRecommender()
    
    test_news = [
        {"title": "伊朗警告美国进行地面入侵", "snippet": "战争冲突升级", "source": "美联社"},
        {"title": "股市大跌，原油价格上涨", "snippet": "金融市场波动", "source": "联合早报"},
        {"title": "NASA Artemis II登月任务进展", "snippet": "科技航天", "source": "美联社"},
        {"title": "UConn击败杜克进入四强", "snippet": "NCAA篮球", "source": "美联社"},
    ]
    
    recommended = recommender.recommend(test_news, count=3)
    
    print(f"推荐新闻 ({len(recommended)}条):")
    for i, item in enumerate(recommended, 1):
        print(f"{i}. {item['title']}")