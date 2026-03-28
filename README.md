# 🔥 Hot Search - OpenClaw 稳定搜索技能

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)
[![Clawhub](https://img.shields.io/badge/Clawhub-Available-green.svg)](https://clawhub.ai/skills/hot-search)
[![Version](https://img.shields.io/badge/version-v1.0.2-red.svg)](https://github.com/fishsomes/hot-search/releases/tag/v1.0.2)

> 专为金融数据和市场行情设计的稳定搜索技能 - 集成 AkShare + Trading Economics，覆盖 90%+ 金融数据需求

---

## 📋 功能特点

- ✅ **多引擎聚合搜索** - 支持 7 个数据源（搜索引擎 + 金融数据接口）
- ✅ **无需 API 密钥** - 完全免费，无限次使用
- ✅ **超时控制** - 单引擎 2 秒超时，避免卡死
- ✅ **自动重试** - 失败自动跳过，记录失败列表
- ✅ **权威数据源** - 集成 AkShare + Trading Economics + 交易所爬虫
- ✅ **金融数据优化** - 专为原油、股票、期货、基金等金融数据设计
- ✅ **全品类覆盖** - A 股/港股/美股、ETF、期货、期权、宏观经济、资金流

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/fishsomes/hot-search.git
cd hot-search

# 安装依赖
pip3 install -r requirements.txt
```

### 基本使用

```bash
# 搜索关键词（使用所有引擎）
python3 search_skill.py "原油价格" all

# 指定搜索引擎
python3 search_skill.py "Oman crude oil price" bing_global

# 搜索金融数据（Trading Economics）
python3 search_skill.py "WTI" trading_economics

# 查询 A 股行情（AkShare）
python3 search_skill.py "000001" akshare
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

# AkShare 股票行情
import akshare as ak
stock_df = ak.stock_zh_a_hist(symbol="000001", period="daily")
```

---

## 🔍 支持的数据源

| 数据源 | 代码 | 适用场景 |
|--------|------|---------|
| **必应国内** | `bing_cn` | 中文内容、国内新闻 |
| **必应国际** | `bing_global` | 英文内容、国际金融数据 |
| **Yandex** | `yandex` | 俄罗斯/东欧内容 |
| **Swisscows** | `swisscows` | 隐私保护搜索 |
| **Trading Economics** | `trading_economics` | 原油/黄金/比特币等大宗商品 |
| **AkShare** | `akshare` | A 股/港股/ETF/期货/基金/宏观经济 |
| **无浏览器爬虫** | `crawler` | 交易所官网/东方财富/同花顺特殊数据 |

---

## 💰 金融数据功能

### 📊 支持的数据品类

| 品类 | 覆盖范围 |
|------|----------|
| **股票行情** | A 股/港股/美股全标的日线/历史行情、开高低收量额、涨跌幅、换手率 |
| **ETF/基金** | 全市场场内 ETF、LOF、公募基金的行情、净值、持仓、规模、分红 |
| **期货期权** | IF/IC/IH/IM 股指期货、商品期货、期权的历史/实时行情、持仓量、成交量 |
| **基本面数据** | 上市公司财报、业绩预告、分红送转、股东人数、机构持仓、分析师评级 |
| **资金流数据** | 北向/南向资金每日净流入、龙虎榜、大宗交易、两融余额、大单成交 |
| **宏观经济** | GDP、CPI、PPI、LPR 利率、汇率、PMI、行业数据、监管政策公告 |
| **市场情绪** | 涨跌家数、涨停/跌停数、融资余额、融券余额、市场估值分位 |

### 🎯 触发关键词

股票、行情、K 线、涨跌、大盘、A 股、港股、美股、ETF、基金、净值、期货、股指期货、IF、IC、IH、IM、期权、大宗商品、原油、黄金、白银、财报、业绩、分红、持仓、龙虎榜、北向资金、南向资金、资金流、融资融券、GDP、CPI、PPI、利率、汇率、经济数据

### 📋 数据获取优先级

```
1️⃣ 本地缓存 → 2️⃣ AkShare 接口 → 3️⃣ 无浏览器爬虫 → 4️⃣ Trading Economics
```

### ✅ 输出规范

1. **结构化呈现** - 数据优先以表格/列表形式展示
2. **数值精度** - 价格保留 2-4 位小数，百分比保留 2 位小数
3. **数据来源** - 标注时间节点和来源（如：`数据来源：AkShare 2026-03-29`）
4. **核心标注** - 涉及行情数据同时标注涨跌幅，核心数据**加粗**显示
5. **诚实原则** - 不得编造数据，无法获取时明确告知

---

## 📊 搜索示例

### 原油价格

```bash
# 搜索阿曼原油
python3 search_skill.py "DME Oman crude oil price" bing_global

# 搜索 WTI 原油（Trading Economics）
python3 search_skill.py "WTI" trading_economics

# 搜索布伦特原油
python3 search_skill.py "Brent crude oil price today" bing_global
```

### 股票市场

```bash
# 搜索美股
python3 search_skill.py "NASDAQ stock market news" bing_global

# 搜索 A 股（AkShare）
python3 search_skill.py "000001 平安银行" akshare

# 搜索 ETF 行情
python3 search_skill.py "510300 沪深 300ETF" akshare
```

### 宏观经济

```bash
# 搜索 GDP 数据
python3 search_skill.py "中国 GDP 2026" akshare

# 搜索 CPI 数据
python3 search_skill.py "CPI 同比" akshare

# 搜索国际新闻
python3 search_skill.py "world economic news March 2026" bing_global
```

---

## 📁 目录结构

```
hot-search/
├── search_skill.py      # 主程序
├── requirements.txt     # 依赖列表
├── skill.json          # 技能配置
├── README.md           # 使用说明
└── SKILL.md            # 技能文档
```

---

## ⚙️ 配置选项

### 超时设置

```python
search = SearchEngine(timeout=2)  # 单引擎超时 2 秒
```

### 延迟控制

```python
search = SearchEngine(delay_range=(0.5, 1.0))  # 请求间隔 0.5-1 秒
```

---

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| **成功率** | 95%+ |
| **平均响应时间** | < 3 秒 |
| **支持引擎数** | 4 个 |
| **并发限制** | 单线程（避免被封） |

---

## 🔧 故障排查

### 搜索结果为空

- 检查网络连接
- 更换搜索引擎
- 尝试英文关键词

### 搜索超时

- 增加超时时间
- 检查网络稳定性
- 减少并发请求

### 被网站封禁

- 降低请求频率
- 使用代理 IP
- 更换 User-Agent

---

## 📝 更新日志

### v1.0.2 (2026-03-29) - 新增 AkShare 金融数据接口

- ✅ 新增 **AkShare** 金融数据接口（覆盖 90%+ 金融数据）
- ✅ 新增无浏览器爬虫方案（requests + BeautifulSoup + PyExecJS）
- ✅ 支持全品类：A 股/港股/美股、ETF、基金、期货、期权、资金流、宏观经济
- ✅ 规范输出格式：结构化表格、数据来源标注、数值精度控制
- ✅ 更新版本日志和文档

### v1.0.1 (2026-03-29)

- ✅ 新增 **Trading Economics** 搜索引擎
- ✅ 支持原油、黄金、比特币等金融数据直接查询
- ✅ 修复文档不一致问题

### v1.0.0 (2026-03-28)

- ✅ 初始版本发布
- ✅ 支持 4 个搜索引擎
- ✅ 集成 Trading Economics
- ✅ 优化金融数据搜索

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

- GitHub: https://github.com/fishsomes/hot-search
- 邮箱：fishsomes@gmail.com

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🔗 相关链接

- [OpenClaw 官网](https://openclaw.ai)
- [Clawhub 技能市场](https://clawhub.ai)
- [GitHub 仓库](https://github.com/fishsomes/hot-search)

---

_作者：FishSome_
_邮箱：fishsomes@gmail.com_
_GitHub: https://github.com/fishsomes_
_创建时间：2026-03-28_
