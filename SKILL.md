---
name: hot-search
description: Hot Search 🔥 全网热搜神器 - 多引擎聚合搜索 + AkShare 金融数据。支持股票行情、期货期权、基金 ETF、宏观经济、资金流等全品类金融数据。免费无限，稳定可靠。
---

# Hot Search 🔥 全网热搜神器

_版本：1.0.2 | 作者：FishSome | 邮箱：fishsomes@gmail.com_

---

## 🔥 版本日志

### v1.0.2 (2026-03-29)
- ✅ 新增 **AkShare** 金融数据接口（90%+ 金融数据覆盖）
- ✅ 新增无浏览器爬虫抓取方案（requests + BeautifulSoup + PyExecJS）
- ✅ 扩展支持：A 股/港股/美股、ETF、基金、期货、期权、资金流、宏观经济等
- ✅ 新增金融数据输出规范（结构化表格、数据来源标注）

### v1.0.1 (2026-03-29)
- ✅ 新增 **Trading Economics** 搜索引擎
- ✅ 支持原油、黄金、比特币等金融数据直接查询
- ✅ 修复文档不一致问题

### v1.0.0 (2026-03-28)
- ✅ 初始版本发布
- ✅ 支持 Bing 国内/国际、Yandex、Swisscows
- ✅ 支持图片搜索和下载

---

## 🔍 技能概述

Hot Search 是专为 OpenClaw 框架设计的稳定搜索技能，特别优化了金融数据和市场行情的搜索能力。

### 核心优势

- **稳定可靠** - 多引擎备份，单引擎失败不影响全局
- **免费使用** - 无需 API 密钥，无使用次数限制
- **快速响应** - 超时控制，避免长时间阻塞
- **金融优化** - 集成 AkShare + Trading Economics，针对原油、股票等金融数据优化

---

## 💰 金融功能模块

### 🎯 触发条件

当用户查询包含以下关键词时，优先使用金融数据能力：

**股票行情**：股票、行情、K 线、涨跌、大盘、A 股、港股、美股、ETF、基金、净值

**期货期权**：期货、股指期货、IF、IC、IH、IM、期权、大宗商品、原油、黄金、白银

**资金流向**：财报、业绩、分红、持仓、龙虎榜、北向资金、南向资金、资金流、融资融券、两融、大宗交易

**机构数据**：股东、机构持仓、国家队、汇金、证金

**宏观经济**：GDP、CPI、PPI、利率、汇率、经济数据、行业数据、IPO、解禁、减持

**市场情绪**：涨停、跌停、涨跌家数

### 📋 数据获取优先级

```
1️⃣ 本地缓存 → 2️⃣ AkShare 接口 → 3️⃣ 无浏览器爬虫
```

| 优先级 | 数据源 | 说明 |
|--------|--------|------|
| 1 | 本地缓存 | 优先查询本地数据库，减少重复请求 |
| 2 | AkShare | 覆盖 90%+ 金融数据，官方接口稳定，免费无限制 |
| 3 | 无浏览器爬虫 | 上交所/深交所/港交所、东方财富、同花顺、新浪财经 |

### 📊 支持的数据品类

| 品类 | 覆盖说明 |
|------|----------|
| **股票行情** | A 股/港股/美股全标的日线/历史行情、开高低收量额、涨跌幅、换手率、振幅 |
| **ETF/基金** | 全市场场内 ETF、LOF、公募基金的行情、净值、持仓、规模、跟踪误差、分红 |
| **期货期权** | IF/IC/IH/IM 股指期货、商品期货、期权的历史/实时行情、持仓量、成交量、结算价 |
| **基本面数据** | 上市公司财报、业绩预告、分红送转、股东人数、机构持仓、分析师评级 |
| **资金流数据** | 北向/南向资金每日净流入、龙虎榜、大宗交易、两融余额、大单成交、行业资金流 |
| **宏观经济** | GDP、CPI、PPI、LPR 利率、汇率、PMI、行业数据、监管政策公告 |
| **市场情绪** | 涨跌家数、涨停/跌停数、融资余额、融券余额、市场估值分位 |

### ✅ 结果输出规范

1. **结构化呈现** - 数据优先以表格/列表形式展示，清晰易读
2. **数值精度** - 价格/数值保留 2-4 位小数，百分比保留 2 位小数
3. **数据来源** - 标注时间节点和来源（如：`数据来源：AkShare 2026-03-29`）
4. **核心标注** - 涉及行情数据同时标注涨跌幅，核心数据**加粗**显示
5. **诚实原则** - 不得编造数据，无法获取时明确告知用户并说明原因

---

## 📦 安装方法

### 方法 1：从 Clawhub 安装

```bash
openclaw skill install hot-search
```

### 方法 2：从 GitHub 安装

```bash
git clone https://github.com/fishsomes/hot-search.git
cd hot-search
pip3 install -r requirements.txt
```

---

## 🚀 使用指南

### 命令行使用

```bash
# 基本搜索
python3 search_skill.py "关键词"

# 指定引擎
python3 search_skill.py "关键词" bing_global

# 多引擎搜索
python3 search_skill.py "关键词" all

# Trading Economics 金融数据
python3 search_skill.py "原油" trading_economics
python3 search_skill.py "WTI" trading_economics
```

### Python 调用

```python
from search_skill import SearchEngine

search = SearchEngine()

# 单引擎搜索
results = search.search('原油价格', 'bing_global')

# 多引擎搜索
results = search.search_all('Oman crude oil price')

# Trading Economics 金融数据
data = search.search_trading_economics('WTI')
print(data)  # {'value': '101.18', 'change': '+1.5%', 'url': '...'}
```

---

## 📈 AkShare 金融数据接口

### 安装依赖

```bash
pip3 install akshare pandas
```

### 常用接口示例

```python
import akshare as ak

# 股票实时行情
stock_df = ak.stock_zh_a_spot_em()  # A 股实时行情
stock_hist = ak.stock_zh_a_hist(symbol="000001", period="daily")  # 历史 K 线

# ETF 行情
etf_df = ak.fund_etf_spot_em()  # ETF 实时行情

# 期货行情
futures_df = ak.futures_zh_spot()  # 期货实时行情
index_futures = ak.futures_index_spot()  # 股指期货（IF/IC/IH/IM）

# 北向资金
north_flow = ak.stock_hsgt_north_net_flow_in_em()  # 北向资金净流入

# 龙虎榜
dragon_list = ak.stock_lhb_detail_em()  # 龙虎榜详情

# 宏观经济
macro_gdp = ak.macro_gdp_year()  # GDP 数据
macro_cpi = ak.macro_cpi_year()  # CPI 数据
```

---

## 🌐 Trading Economics 金融数据

### 支持的数据类型

| 关键词 | 说明 |
|--------|------|
| `WTI` / `原油` | WTI 原油价格 |
| `Brent` / `布伦特` | 布伦特原油价格 |
| `Gold` / `黄金` | 黄金价格 |
| `Bitcoin` / `比特币` | 比特币价格 |
| `Natural Gas` / `天然气` | 天然气价格 |
| `Copper` / `铜` | 铜价格 |

### 使用示例

```python
search = SearchEngine()

# 查询 WTI 原油
result = search.search_trading_economics('WTI')
# 返回：{'title': 'WTI', 'value': '101.18', 'change': '+1.5%', 'url': '...'}

# 查询黄金
result = search.search_trading_economics('gold')
```

---

## 📊 数据源列表

| 数据源 | 名称 | 适用场景 |
|--------|------|----------|
| `bing_cn` | 必应国内 | 中文内容、国内新闻 |
| `bing_global` | 必应国际 | 英文内容、国际金融数据 |
| `yandex` | Yandex | 俄罗斯/东欧内容 |
| `swisscows` | Swisscows | 隐私保护搜索 |
| `trading_economics` | Trading Economics | 原油/黄金/比特币等大宗商品 |
| `akshare` | AkShare | A 股/港股/ETF/期货/基金/宏观经济 |
| `crawler` | 无浏览器爬虫 | 交易所官网/东方财富/同花顺特殊数据 |

---

## 📸 图片搜索

```python
# 搜索图片
image_urls = search.search_bing_images('Emiri Momota', limit=5)

# 下载图片
search.download_image(image_url, '/path/to/image.jpg')

# 搜索并下载
downloaded = search.search_and_download('原油图表', limit=3)
```

---

## ⚠️ 注意事项

### 通用规范
1. **合法合规** - 仅用于合法数据抓取
2. **频率控制** - 避免高频请求被封禁
3. **超时设置** - 建议 2-5 秒超时
4. **错误处理** - 捕获异常，记录失败

### 金融数据专项
1. **数据时效** - 行情数据标注采集时间，避免误导用户
2. **来源标注** - 所有金融数据必须标注来源（AkShare/交易所/爬虫）
3. **精度控制** - 价格保留 2-4 位小数，百分比保留 2 位小数
4. **失败处理** - 单只股票/单个接口失败直接跳过，记录到失败列表
5. **并发限制** - 批量任务默认 5 线程池，单线程失败不影响全局
6. **防限流** - 第三方 API 调用默认加 `time.sleep(0.5~1s)`

---

## 🤖 Agent 调用规范（❗ 必须遵守）

### ⚠️ exec 执行必须用异步阻塞

**所有 Python 脚本执行必须使用异步阻塞方式（yieldMs/background）！**

```bash
# ✅ 正确：异步阻塞执行（推荐）
# 设置 yieldMs=5000，5 秒后后台继续执行，不阻塞主进程
exec command="python3 search_skill.py '关键词' all" yieldMs=5000

# ✅ 正确：长时间任务用 background
# 立即后台执行，用 process 工具轮询结果
exec command="python3 search_skill.py '全量股票数据' akshare" background=true

# ❌ 错误：同步阻塞执行（会卡死！）
# 不要这样！网络请求可能阻塞 10+ 秒
exec command="python3 search_skill.py '关键词' all"
```

**原因：**
- 搜索操作涉及多个网络请求，单引擎 2 秒超时，多引擎可能 10+ 秒
- 同步阻塞会卡死 Agent 主进程，无法响应其他请求
- 异步阻塞让出执行权，后台继续运行，完成后通知

### 🎯 子 Agent 触发条件

**当预测需要搜索的不同网站内容超过 50 条时，必须询问用户是否开启子 Agent！**

**判断逻辑：**
```python
# 条件：
# 1. 需要搜索的不同网站/数据源 >= 3 个
# 2. 预计总结果数 >= 50 条
# 3. 任务复杂度较高（如：跨多个数据源采集）

if len(search_queries) >= 3 and estimated_results >= 50:
    # 询问用户
    print("⚠️ 检测到需要搜索多个数据源，预计返回 50+ 条结果")
    print("是否开启子 Agent 进行异步并行搜索？（推荐）")
    print("  - 优势：多任务并行，互不阻塞，失败隔离")
    print("  - 耗时：预计 5-10 秒（单线程需 30+ 秒）")
```

### 📋 子 Agent 使用场景

| 场景 | 建议 |
|------|------|
| 单数据源搜索（<10 条结果） | ❌ 不需要子 Agent |
| 单数据源批量搜索（>50 条结果） | ⚠️ 建议子 Agent |
| 多数据源聚合搜索（3+ 数据源） | ✅ 强烈推荐子 Agent |
| 全量数据采集（全市场股票/基金） | ✅ 必须子 Agent |
| 策略回测 + 数据采集 | ✅ 必须子 Agent |

### 📊 子 Agent 优势

- ✅ **并行执行** - 多个数据源同时搜索，速度提升 3-5 倍
- ✅ **失败隔离** - 单任务失败不影响其他任务
- ✅ **进度可见** - 实时上报进度，每 10 分钟主动汇报
- ✅ **超时控制** - 独立超时设置，不阻塞主 Agent
- ✅ **自动重试** - 失败任务自动重试 3 次

---

## 🔗 相关资源

- [OpenClaw 文档](https://docs.openclaw.ai)
- [Clawhub 技能市场](https://clawhub.ai/skills/hot-search)
- [GitHub 仓库](https://github.com/fishsomes/hot-search)
- [AkShare 文档](https://akshare.akfamily.xyz) - 90%+ 金融数据覆盖
- [Trading Economics](https://tradingeconomics.com) - 全球经济指标
- [东方财富](https://www.eastmoney.com) - A 股行情/资金流
- [同花顺](https://www.10jqka.com.cn) - 股票/基金/期货数据

---

_最后更新：2026-03-29_
_作者：FishSome_
_邮箱：fishsomes@gmail.com_