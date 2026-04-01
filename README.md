# Hot Search 🔥 V4.0

_版本：4.0.0 | 作者：FishSome | 邮箱：fishsomes@gmail.com_

---

[![GitHub stars](https://img.shields.io/github/stars/fishsome/hot-search)](https://github.com/fishsome/hot-search/stargazers)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/Powered-By-OpenClaw-blue)](https://openclaw.ai)
[![SkillHub](https://img.shields.io/badge/Available-SkillHub-orange)](https://clawhub.ai/skills/hot-search)

---

## 🎯 核心功能（V4.0 聚焦主线）

### 1️⃣ 搜索聚合
- **主引擎**：Bing（国内版 + 国际版）
- **备用引擎**：Sougou、百度
- **特点**：主引擎失败自动切换备用引擎

### 2️⃣ 国际新闻抓取
- **联合早报**（中文，东南亚视角）
- **RT News**（俄罗斯视角）
- **联合国新闻**（权威官方立场）
- **美联社 AP News**（美国主流视角）

### 3️⃣ 定时抓取
- **早中晚定时**：07:00、12:00、21:00
- **后台抓取**：50-100条新闻自动缓存
- **智能权重**：金融/战争/科技优先推荐

---

## 🚀 快速开始

### 安装依赖

```bash
pip3 install requests beautifulsoup4 pyyaml schedule pyexecjs
```

### 基本使用

```bash
# 搜索聚合
python3 hot-search.py search "关键词" cn      # Bing国内版
python3 hot-search.py search "关键词" all    # 所有引擎

# 新闻抓取
python3 hot-search.py news zaobao 10          # 联合早报
python3 hot-search.py news all 20              # 所有新闻源

# 立即抓取
python3 hot-search.py fetch 50                # 抓取50条并缓存

# 推荐新闻
python3 hot-search.py recommend 5              # 权重推荐5条

# 查看缓存
python3 hot-search.py cache 100                # 获取缓存新闻

# 定时调度
python3 hot-search.py scheduler start          # 启动定时
python3 hot-search.py scheduler stop           # 停止定时

# 配置管理
python3 hot-search.py config show              # 显示配置
python3 hot-search.py config update finance 5 # 更新权重
```

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
│   └── apnews.py        # 美联社
├── anti_crawler/
│   ├── headers_pool.py  # Headers池轮换
│   ├── retry.py         # 智能重试
│   └── js_executor.py   # JS执行器
├── config/
│   └── config.yaml      # 配置文件
├── hot-search.py        # 主CLI入口
└── SKILL.md             # Skill元数据
```

---

## ⚙️ 配置说明

编辑 `config/config.yaml`:

```yaml
search:
  primary: bing          # 主搜索引擎
  fallback:
    - sougou
    - baidu
  timeout: 3

news:
  sources:
    - zaobao
    - rt
    - un_news
    - apnews

scheduler:
  schedule:
    morning: "07:00"
    noon: "12:00"
    evening: "21:00"
  batch_size: 50

recommend:
  user_focus:
    finance: 3           # 金融（权重最高）
    war: 2               # 战争
    tech: 2              # 科技
    entertainment: 1     # 娱乐
    sports: 1            # 体育

anti_crawler:
  headers_pool: true
  js_executor: true
  delay_range:
    min: 0.5
    max: 2.0
```

---

## 🔧 反爬技术栈

| 技术 | 说明 |
|------|------|
| **requests** | HTTP请求库 |
| **BeautifulSoup** | HTML解析 |
| **PyExecJS** | JS加密执行 |
| **Headers池轮换** | UA/Headers随机切换 |
| **智能重试** | 指数退避 + 错误分类 |
| **请求延迟** | 0.5-2秒随机延迟 |

---

## 📝 更新日志

### V4.0.0 (2026-04-01)
- ✅ **聚焦主线，简化功能**
- ✅ **搜索聚合**：Bing主 + Sougou/百度备
- ✅ **国际新闻**：联合早报/RT/UN/AP
- ✅ **定时抓取**：早中晚自动抓取50-100条
- ✅ **权重推荐**：金融/战争/科技优先
- ✅ **反爬技术**：Headers池+智能重试+JS执行
- ✅ **缓存管理**：JSON Lines格式缓存

### V1.0.2 (2026-03-29)
- ✅ 新增 AkShare 金融数据接口（90%+ 金融数据覆盖）
- ✅ 新增无浏览器爬虫抓取方案
- ✅ 新增 Trading Economics 搜索引擎

---

## 🤖 OpenClaw Agent 调用规范

### ⚠️ exec 执行必须用异步阻塞

```bash
# ✅ 正确：异步阻塞执行（推荐）
exec command="python3 hot-search.py search '关键词' all" yieldMs=5000

# ✅ 正确：长时间任务用 background
exec command="python3 hot-search.py fetch 100" background=true

# ❌ 错误：同步阻塞执行（会卡死！）
exec command="python3 hot-search.py search '关键词' all"
```

---

## 📬 联系方式

- 📧 邮箱：fishsomes@gmail.com
- 🐙 GitHub：https://github.com/fishsome/hot-search
- 🌐 OpenClaw：https://openclaw.ai
- 🛒 SkillHub：https://clawhub.ai/skills/hot-search

---

_最后更新：2026-04-01_