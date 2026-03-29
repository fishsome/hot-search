# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.2] - 2026-03-29

### 🎉 Added - 新增功能

- **AkShare 金融数据接口**
  - 覆盖 90%+ 金融数据需求
  - 支持股票/ETF/基金/期货/期权行情
  - 支持基本面财报、资金流、宏观经济数据
  - 官方接口稳定，免费无调用限制

- **无浏览器爬虫抓取方案**
  - 技术栈：requests + BeautifulSoup + PyExecJS
  - 目标数据源：上交所/深交所/港交所官网、东方财富、同花顺、新浪财经
  - 适合：国家队持仓、特殊统计数据、实时异动数据等

- **全品类金融数据支持**
  - 股票行情：A 股/港股/美股全标的日线/历史行情
  - ETF/基金：全市场场内 ETF、LOF、公募基金的行情、净值、持仓
  - 期货期权：IF/IC/IH/IM 股指期货、商品期货、期权
  - 基本面数据：财报、业绩预告、分红送转、机构持仓
  - 资金流数据：北向/南向资金、龙虎榜、大宗交易、两融余额
  - 宏观经济：GDP、CPI、PPI、LPR 利率、汇率、PMI
  - 市场情绪：涨跌家数、涨停/跌停数、融资余额

### 📋 Changed - 改进

- 更新技能描述，强调 AkShare + Trading Economics 集成
- 完善输出规范：结构化表格、数据来源标注、数值精度控制
- 优化金融数据专项注意事项

### 📖 Documentation - 文档更新

- 更新 SKILL.md 至 v1.0.2
- 更新 README.md 介绍和使用示例
- 新增 CHANGELOG.md 更新日志文件

---

## [1.0.1] - 2026-03-29

### 🎉 Added - 新增功能

- **Trading Economics 搜索引擎**
  - 支持原油（WTI/Brent）价格查询
  - 支持黄金、白银等贵金属价格
  - 支持比特币等加密货币价格
  - 支持天然气、铜等大宗商品

### 🐛 Fixed - 修复

- 修复文档不一致问题
- 优化版本日志格式

---

## [1.0.0] - 2026-03-28

### 🎉 Added - 新增功能

- **多引擎聚合搜索**
  - 必应国内（bing_cn）
  - 必应国际（bing_global）
  - Yandex（yandex）
  - Swisscows（swisscows）

- **核心特性**
  - 无需 API 密钥，完全免费
  - 超时控制，避免卡死
  - 自动重试，失败跳过
  - 金融数据搜索优化

- **图片搜索**
  - 支持 Bing 图片搜索
  - 支持图片下载功能

---

## [2.2.0] - 2026-03-30

### 🎉 Added - OpenClaw 适配版

- **统一调用入口**
  - 新增 `hot-search.py` 统一入口文件
  - 命令行规范：`hot-search [command] [args]`
  - 所有命令返回标准 JSON 格式

- **新增命令**
  - `monitor` - 热点监控（关键词 + 热度阈值）
  - `history` - 历史热搜查询（支持日期参数）
  - `parse` - 自然语言指令解析
  - `version` - 版本信息查询

- **自然语言指令解析**
  - 支持中文自然语言指令
  - 自动解析为标准命令
  - 示例："今日全网热点" → "hot all"

- **OpenClaw Skill 标准化**
  - 更新 `skill.json` 至 V2.2.0 格式
  - AI Agent 异步适配
  - JSON 输出格式标准化
  - 错误处理兼容 OpenClaw

### 📋 Changed - 改进

- 统一 JSON 输出格式：
  ```json
  {
    "success": true/false,
    "error": null/"错误信息",
    "timestamp": "时间戳",
    "data": [...]
  }
  ```
- 错误处理标准化，失败时返回 `success=false + error`
- 性能优化：单引擎 2s 超时，总超时 10s

### 📖 Documentation - 文档更新

- 新增 `TEST_REPORT.md` OpenClaw 兼容性测试报告
- 更新 `CHANGELOG.md` 版本日志
- 更新 `skill.json` 版本信息

---

## [Unreleased]

- 异步任务完整轮询机制
- 历史数据定时保存任务
