# 🔥 Hot Search - 全网热搜神器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)
[![Clawhub](https://img.shields.io/badge/Clawhub-Available-green.svg)](https://clawhub.ai/skills/hot-search)
[![Version](https://img.shields.io/badge/version-v1.0.2-red.svg)](https://github.com/fishsomes/hot-search/releases/tag/v1.0.2)
[![Stars](https://img.shields.io/github/stars/fishsomes/hot-search?style=social)](https://github.com/fishsomes/hot-search)

> 🚀 **一站式金融数据搜索解决方案** - 从股票行情到宏观经济，从原油黄金到北向资金，**7 大数据源**为你服务！

---

## 💥 为什么选择 Hot Search？

| 痛点 | Hot Search 解决方案 |
|------|-------------------|
| ❌ 数据分散，到处找 | ✅ **7 合 1 聚合** - 搜索 + 金融数据 + 爬虫，一个搞定 |
| ❌ API 收费贵 | ✅ **完全免费** - 无需 API 密钥，无限次使用 |
| ❌ 请求卡死，等半天 | ✅ **2 秒超时** - 失败自动跳过，永不阻塞 |
| ❌ 数据不准，来源不明 | ✅ **权威标注** - AkShare + 交易所 + Trading Economics，来源清晰 |
| ❌ 格式混乱，难阅读 | ✅ **结构化输出** - 表格/列表/加粗，一眼看懂 |

---

## 🎯 核心能力

### 🔍 搜索引擎（4 个）
- **必应国内** - 中文内容、国内新闻
- **必应国际** - 英文内容、国际金融数据
- **Yandex** - 俄罗斯/东欧内容
- **Swisscows** - 隐私保护搜索

### 💰 金融数据（3 个）
- **AkShare** - 🇨🇳 90%+ 中国金融数据覆盖（股票/ETF/期货/基金/宏观经济）
- **Trading Economics** - 🌍 全球大宗商品（原油/黄金/比特币/汇率）
- **无浏览器爬虫** - 🕷️ 交易所官网/东方财富/同花顺/新浪财经（国家队持仓/龙虎榜）

---

## 📊 一单搞定全品类金融数据

| 数据品类 | 覆盖范围 | 数据源 |
|---------|---------|--------|
| 📈 **股票行情** | A 股/港股/美股全标的日线/历史行情、开高低收量额、涨跌幅、换手率 | AkShare |
| 💎 **ETF/基金** | 全市场场内 ETF、LOF、公募基金的行情、净值、持仓、规模、分红 | AkShare |
| 📉 **期货期权** | IF/IC/IH/IM 股指期货、商品期货、期权的历史/实时行情、持仓量、成交量 | AkShare |
| 📑 **基本面数据** | 上市公司财报、业绩预告、分红送转、股东人数、机构持仓、分析师评级 | AkShare + 爬虫 |
| 💸 **资金流数据** | 北向/南向资金每日净流入、龙虎榜、大宗交易、两融余额、大单成交 | AkShare + 爬虫 |
| 🌐 **宏观经济** | GDP、CPI、PPI、LPR 利率、汇率、PMI、行业数据、监管政策公告 | AkShare |
| 🔥 **市场情绪** | 涨跌家数、涨停/跌停数、融资余额、融券余额、市场估值分位 | AkShare + 爬虫 |
| 🛢️ **大宗商品** | WTI/布伦特原油、黄金、白银、比特币、天然气、铜 | Trading Economics |

---

## ⚡ 30 秒快速上手

### 1️⃣ 安装

```bash
# 克隆仓库
git clone https://github.com/fishsomes/hot-search.git
cd hot-search

# 安装依赖（2 个核心库）
pip3 install -r requirements.txt
pip3 install akshare pandas  # 金融数据必备
```

### 2️⃣ 开用！

```bash
# 🔥 一键全引擎搜索
python3 search_skill.py "000001 平安银行" all

# 📈 查股票行情（AkShare）
python3 search_skill.py "000001" akshare

# 🛢️ 查原油价格（Trading Economics）
python3 search_skill.py "WTI" trading_economics

# 💰 查北向资金
python3 search_skill.py "北向资金净流入" akshare

# 📊 查 GDP 数据
python3 search_skill.py "中国 GDP 2026" akshare
```

### 3️⃣ Python 集成

```python
from search_skill import SearchEngine
import akshare as ak

search = SearchEngine()

# 搜索
results = search.search_all('原油价格')

# Trading Economics 原油
oil = search.search_trading_economics('WTI')
print(f"WTI 原油：${oil['value']} ({oil['change']})")

# AkShare 股票行情
stock = ak.stock_zh_a_hist(symbol="000001", period="daily")
print(stock.tail())  # 最近 5 天 K 线
```

---

## 🎬 使用场景示例

### 📈 股民日常

```bash
# 早盘：看大盘行情
python3 search_skill.py "上证指数 今日行情" akshare

# 盘中：盯北向资金
python3 search_skill.py "北向资金净流入" akshare

# 收盘：查龙虎榜
python3 search_skill.py "龙虎榜详情" akshare

# 复盘：看个股 K 线
python3 search_skill.py "000001 平安银行 历史行情" akshare
```

### 🛢️ 大宗商品交易员

```bash
# 原油价格（实时）
python3 search_skill.py "WTI" trading_economics

# 布伦特原油
python3 search_skill.py "Brent" trading_economics

# 黄金价格
python3 search_skill.py "Gold" trading_economics

# 比特币
python3 search_skill.py "Bitcoin" trading_economics
```

### 📊 宏观经济研究

```bash
# GDP 数据
python3 search_skill.py "中国 GDP 2026" akshare

# CPI/PPI
python3 search_skill.py "CPI 同比" akshare

# 利率汇率
python3 search_skill.py "LPR 利率" akshare
python3 search_skill.py "美元兑人民币" akshare

# PMI
python3 search_skill.py "制造业 PMI" akshare
```

### 🔍 普通搜索

```bash
# 中文内容
python3 search_skill.py "OpenClaw 教程" bing_cn

# 英文内容
python3 search_skill.py "AI agent framework" bing_global

# 隐私搜索
python3 search_skill.py "敏感话题" swisscows
```

---

## ⚡ 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **成功率** | 95%+ | 7 大数据源备份，单点失败不影响全局 |
| **平均响应** | < 3 秒 | 2 秒超时控制，快速失败快速重试 |
| **数据覆盖** | 90%+ | AkShare 覆盖中国金融数据 90% 以上 |
| **并发能力** | 5 线程 | 批量任务默认 5 线程池，单线程失败不影响全局 |
| **防限流** | ✅ | 第三方 API 默认 sleep(0.5~1s) |


---

## 🔗 相关链接

| 资源 | 链接 |
|------|------|
| 📖 OpenClaw 文档 | https://openclaw.ai |
| 🛒 Clawhub 技能市场 | https://clawhub.ai |
| 💻 GitHub 仓库 | https://github.com/fishsomes/hot-search |
| 📊 AkShare 文档 | https://akshare.akfamily.xyz |
| 🌍 Trading Economics | https://tradingeconomics.com |
| 📰 东方财富 | https://www.eastmoney.com |
| 📈 同花顺 | https://www.10jqka.com.cn |

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

_❤️ 用爱发电 | 👨‍💻 作者：FishSome | 📧 fishsomes@gmail.com | 📅 创建于 2026-03-28 | 🚀 当前版本：v1.0.2_
