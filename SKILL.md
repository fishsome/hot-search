---
name: hot-search
version: "4.0.0"
description: Hot Search 🔥 V4.0 - 聚焦主线，简化功能。搜索聚合（Bing主+Sougou/百度备）+ 国际新闻（联合早报/RT/UN/AP）+ 定时抓取 + 权重推荐。
---

# Hot Search 🔥 V4.0

_版本：4.0.0 | 作者：FishSome | 邮箱：fishsomes@gmail.com_

---

## 🎯 核心功能（聚焦主线）

### 1️⃣ **搜索聚合**
- **主引擎**：Bing（国内版 + 国际版）
- **备用引擎**：Sougou、百度
- **特点**：主引擎失败自动切换备用引擎

### 2️⃣ **国际新闻抓取**
- **联合早报**（中文，东南亚视角）
- **RT News**（俄罗斯视角）
- **联合国新闻**（权威官方立场）
- **美联社 AP News**（美国主流视角）

### 3️⃣ **定时抓取**
- **早中晚定时**：07:00、12:00、21:00
- **后台抓取**：50-100条新闻自动缓存
- **智能权重**：金融/战争/科技优先推荐

---

## 📦 安装依赖

```bash
pip3 install requests beautifulsoup4 pyyaml schedule pyexecjs
```

---

## 🚀 使用方法

### CLI 命令

```bash
# 搜索聚合
python3 hot-search.py search [keyword] [engine]
python3 hot-search.py search "Python教程" all      # Bing主+备用引擎
python3 hot-search.py search "Python教程" cn       # Bing国内版

# 新闻抓取
python3 hot-search.py news [source] [limit]
python3 hot-search.py news all 20                  # 所有新闻源
python3 hot-search.py news zaobao 10               # 仅联合早报

# 立即抓取
python3 hot-search.py fetch [batch_size]
python3 hot-search.py fetch 50                     # 抓取50条新闻并缓存

# 推荐新闻
python3 hot-search.py recommend [count]
python3 hot-search.py recommend 5                  # 推荐5条新闻（权重排序）

# 缓存新闻
python3 hot-search.py cache [limit]
python3 hot-search.py cache 100                    # 获取缓存中的100条新闻

# 定时调度
python3 hot-search.py scheduler start              # 启动定时调度
python3 hot-search.py scheduler stop               # 停止定时调度

# 配置管理
python3 hot-search.py config show                  # 显示配置
python3 hot-search.py config update finance 3      # 更新权重：金融=3
```

---

## 📊 返回格式（标准化JSON）

所有命令返回统一JSON格式：

```json
{
  "success": true,
  "keyword": "Python教程",
  "engine": "all",
  "count": 10,
  "results": [
    {
      "title": "Python教程...",
      "link": "https://...",
      "snippet": "...",
      "source": "Bing国际"
    }
  ]
}
```

---

## ⚙️ 配置文件

配置文件路径：`./config/config.yaml`

```yaml
# 搜索引擎配置
search:
  primary: bing          # 主搜索引擎
  fallback:              # 备用搜索引擎
    - sougou
    - baidu
  timeout: 3             # 超时时间（秒）

# 新闻源配置
news:
  sources:               # 新闻源列表
    - zaobao
    - rt
    - un_news
    - apnews

# 定时调度配置
scheduler:
  schedule:              # 抓取时间
    morning: "07:00"
    noon: "12:00"
    evening: "21:00"
  batch_size: 50         # 每次抓取条数

# 推荐系统配置
recommend:
  user_focus:            # 用户关注点权重
    finance: 3           # 金融（权重最高）
    war: 2               # 战争
    tech: 2              # 科技
    entertainment: 1     # 娱乐
    sports: 1            # 体育
```

---

## 🔧 Python 调用

```python
from core.searcher import SearchAggregator
from core.news_fetcher import NewsAggregator
from core.recommender import NewsRecommender
from core.scheduler import NewsScheduler

# 搜索聚合
searcher = SearchAggregator()
results = searcher.search_global("Python教程", limit=10)

# 新闻抓取
news_fetcher = NewsAggregator()
news = news_fetcher.fetch_all_news(limit_per_source=10, total_limit=30)

# 推荐新闻
recommender = NewsRecommender()
recommended = recommender.recommend(news, count=5)

# 定时调度
scheduler = NewsScheduler()
scheduler.start()  # 后台定时抓取
result = scheduler.fetch_now(batch_size=50)  # 手动抓取
```

---

## 🛠️ 反爬技术栈

| 技术 | 说明 |
|------|------|
| **requests** | HTTP请求库 |
| **BeautifulSoup** | HTML解析 |
| **PyExecJS** | JS加密执行 |
| **Headers池轮换** | UA/Headers随机切换 |
| **智能重试** | 指数退避 + 错误分类 |
| **请求延迟** | 0.5-2秒随机延迟 |

---

## 📁 项目结构

```
hot-search-v4/
├── core/
│   ├── searcher.py      # 搜索聚合器
│   ├── news_fetcher.py  # 新闻抓取聚合器
│   ├── cache.py         # 缓存管理
│   ├── recommender.py   # 推荐系统
│   └── scheduler.py     # 定时调度
├── engines/
│   ├── bing.py          # Bing搜索引擎
│   ├── sougou.py        # Sougou搜索引擎
│   ├── baidu.py         # 百度搜索引擎
│   ├── zaobao.py        # 联合早报
│   ├── rt.py            # RT News
│   ├── un_news.py       # 联合国新闻
│   ├── apnews.py        # 美联社
├── anti_crawler/
│   ├── headers_pool.py  # Headers池轮换
│   ├── retry.py         # 智能重试
│   ├── js_executor.py   # JS执行器
├── config/
│   ├── config.yaml      # 配置文件
├── cache/
│   ├── news_cache.log   # 新闻缓存（JSON Lines）
│   ├── weights.json     # 权重配置
├── skill.json           # Skill元数据
├── SKILL.md             # 本文件
└── hot-search.py        # 主CLI入口
```

---

## 🎯 与旧版本对比

| 功能 | V1.0-3.0 | V4.0 |
|------|---------|------|
| 搜索引擎 | 多引擎聚合 | **Bing主+Sougou/百度备** |
| 新闻源 | 不稳定 | **4大权威源** |
| 定时抓取 | 无 | **早中晚自动** |
| 缓存管理 | 无 | **JSON Lines缓存** |
| 推荐系统 | 无 | **权重排序** |
| 反爬技术 | 基础 | **Headers池+智能重试+JS执行** |
| 代码复杂度 | 高 | **聚焦主线，简化** |

---

## ⚠️ 注意事项

1. **网络请求**：所有请求使用异步阻塞（yieldMs=5000）
2. **超时控制**：单次请求超时3秒，避免长时间阻塞
3. **错误处理**：主引擎失败自动切换备用引擎
4. **缓存清理**：过期缓存自动清理（24小时）
5. **权重更新**：可通过config命令更新关注点权重

---

## 📝 更新日志

### V4.0.0 (2026-03-30)
- ✅ **聚焦主线，简化功能**
- ✅ **搜索聚合**：Bing主 + Sougou/百度备
- ✅ **国际新闻**：联合早报/RT/UN/AP
- ✅ **定时抓取**：早中晚自动抓取50-100条
- ✅ **权重推荐**：金融/战争/科技优先
- ✅ **反爬技术**：Headers池+智能重试+JS执行
- ✅ **缓存管理**：JSON Lines格式缓存

---

_最后更新：2026-03-30_
_作者：FishSome_
_邮箱：fishsomes@gmail.com_