---
name: pkulaw-legal-search
description: 用户自建的北大法宝（pkulaw.com）网页/Computer Use 检索入口与兜底流程。用于 MCP 结果不足、需要登录网页详情页、需要复制/核验 URL、需要 IP/机构登录状态、或需要像人一样操作北大法宝网页时。当前本机也已配置三个北大法宝 MCP：检索法律法规-关键词、精准查找法条-关键词、检索司法案例-关键词；能用 MCP 时先用 MCP，网页/Computer Use 负责补查和核验。不要把本 skill 视为可被原生 MCP skill 替代的重复项。
---

# 北大法宝网页/Computer Use 检索技能

## 核心原则

本 skill 是用户自建的北大法宝网页检索与兜底流程，不是要替代原生 MCP skill。正确定位是：

- 能用 MCP 快速拿到列表或条文时，先用 MCP。
- MCP 不通、当前会话没加载对应工具、返回 401/403/超时/无结果、结果不足、需要登录详情页、需要网页筛选、需要复制真实 URL、或需要确认页面可见内容时，转入本 skill 的网页/Computer Use 流程。
- 在 Codex 桌面环境中，网页端优先用 Computer Use 操作本机浏览器，因为它更可能保留学校/IP/机构登录状态。

## 当前可用 MCP 范围（2026-05-27 更新配置）

本机目前应优先调用以下三个北大法宝 MCP：

- `mcp__pkulaw_law_keyword__get_law_list`：检索法律法规-关键词。输入 `title` 和/或 `fulltext`，返回法规列表前 10 条。
- `mcp__pkulaw_fatiao__get_law_item_content`：精准查找法条-关键词。适合已知法规名、条号或需要条文原文时使用；参数为 `title` 和 `tiao_num`。
- `mcp__pkulaw_case__get_case_list`：检索司法案例-关键词。输入 `title` 和/或 `fulltext`，返回案例列表前 10 条。

以下旧 MCP 不再作为可用通道写入检索计划，也不要提示用户先用它们：`pkulaw_law_search`、`pkulaw_case_search`、`pkulaw_case_number`、`pkulaw_citation`、`pkulaw_recognition`、`pkulaw_hyperlink`、`pkulaw_nl_sql`。如任务确实需要这些能力，直接说明当前只订阅关键词/精准法条/案例检索，并转网页端北大法宝或请用户追加订阅。

优先级必须按以下顺序执行：

1. **先用三个已配置 MCP**：法规列表用 `get_law_list`，精准法条用 `get_law_item_content`，案例用 `get_case_list`。
2. **再用网页**：MCP 找不到、结果不足、需要登录后详情页或需要确认页面 URL 时，再访问北大法宝网页。
3. **Codex 中优先 Computer Use**：如果在 Codex 桌面环境且页面需要 IP 登录/机构登录/真实浏览器状态，优先用 Computer Use 操作本机浏览器或已登录页面。
4. **camoufox/Agent Browser 仅作后备**：当没有 MCP、没有 Computer Use、或任务明确要求 camoufox/Agent Browser 时，才用 camoufox-cli/Agent Browser。

## 触发场景

当用户提出以下需求时使用：

- 检索法律法规、司法解释、行政法规、地方性法规
- 检索案例、案号、裁判文书、指导性案例、典型案例
- 为作业、法律意见、论文脚注补充北大法宝法规/案例线索
- 初步验证某个法规或案例是否存在

## Step 0：识别可用检索通道

在开始检索前，先判断当前环境有哪些工具。

### A. MCP 优先

如果当前工具列表中存在以下北大法宝 MCP，优先使用：

- `mcp__pkulaw_law_keyword__get_law_list`：按标题/正文关键词检索法规列表。
- `mcp__pkulaw_fatiao__get_law_item_content`：按法规名、条号精准查找法条。
- `mcp__pkulaw_case__get_case_list`：按标题/正文关键词检索案例列表。

MCP 适合快速获得：标题、法条原文、法院、案号、发布日期、案例链接、法规链接。

### B. Browser / Computer Use 后备

如果 MCP 不可用、结果太少、链接打不开，或者需要登录状态下确认详情页：

- **Codex 桌面环境**：优先使用 Computer Use 控制本机浏览器。原因是本机浏览器更可能已有学校/机构 IP 登录状态、cookie、浏览器会话，速度通常也比 camoufox 更快。
- **有 in-app Browser 且页面不需要登录**：可用 Browser 打开公开页面确认链接。
- **非 Codex 或明确要求 camoufox**：再使用 camoufox-cli/Agent Browser。

## Step 1：明确检索对象

先把用户需求归类：

- **法条**：法规名称 + 条号，例如《民法典》第153条。
- **法规文件**：标题、文号、发布时间、修正时间。
- **案例**：案名、法院、案号、案由、关键词。
- **论文/文章**：作者、标题、期刊、年份、关键词。
- **综合研究**：问题描述 + 需要的材料类型。

除非用户要求非常宽泛，否则不要先问用户；根据已有文本先检索，必要时再补问。

## Step 2：MCP 检索策略

### 法条/法规

推荐顺序：

1. 已知法律名和条号：先用法律名称或核心标题词跑 `get_law_list`，确认目标法规存在。
2. 需要精确法条支撑：关键词 MCP 不能直接取指定条文全文；取得法规线索后转网页端详情页确认条号和原文。
3. 不确定法规名称：从用户问题中提炼 1-3 个关键词，用 `get_law_list` 多轮检索。
4. 需要条文全文、效力状态或详情页链接：关键词 MCP 只能作为入口；必要时转网页端北大法宝详情页确认。

输出时应保留：

- 法规全称
- 条号/款项
- 条文原文或摘要
- 北大法宝链接（如 MCP 返回）
- 是否为现行有效、已修正、已废止（如可得）

### 案例

推荐顺序：

1. 已知案号：把案号作为 `title` 或 `fulltext` 关键词，用 `get_case_list` 检索。
2. 已知案名/关键词：用 `get_case_list`。
3. 需要裁判分歧或类案：先用争点词、案由词、核心事实词多轮 `get_case_list`；结果不足时转网页端筛选。

输出时应保留：

- 案名
- 法院
- 案号
- 审结日期
- 裁判要旨/相关段落摘要
- 北大法宝链接（如 MCP 返回）

### 学术文章/综合检索

当前 MCP 订阅不包含文章库或综合语义检索。需要论文、律所文章、微信公众号文章、跨库综合研究时，直接走网页端北大法宝或其他可靠来源，不要调用旧的 `ai_pkulaw_search`。

输出时应保留：

- 作者
- 文题
- 来源
- 年份/期数
- 链接
- 与用户问题的相关性说明

## Step 3：网页检索策略

仅在 MCP 不足时进入网页检索。

### Codex 桌面环境优先：Computer Use

适用情形：

- 北大法宝需要学校 IP 登录或机构登录。
- 本机浏览器已登录。
- 需要像人一样点击筛选、展开详情页、复制链接。
- MCP 返回结果但链接需要网页确认。

基本流程：

1. 用 Computer Use 打开/读取浏览器状态。
2. 访问 `https://www.pkulaw.com` 或对应模块。
3. 确认是否已通过 IP/机构登录。
4. 在搜索框输入关键词。
5. 根据模块筛选法规、案例、期刊、律所文章等。
6. 打开目标详情页，复制地址栏 URL、标题和关键信息。

### camoufox / Agent Browser 后备

仅在以下情形使用：

- 没有 Codex Computer Use。
- 用户明确要求 camoufox/Agent Browser。
- 需要无头浏览器批量抓取公开结果。

常用 URL：

- 北大法宝首页：`https://www.pkulaw.com`
- 法律法规：`https://www.pkulaw.com/chl/`
- 司法案例：`https://www.pkulaw.com/case`
- 法学期刊：`https://www.pkulaw.com/journal`
- 指导性案例：`https://www.pkulaw.com/gac/`

常见链接格式：

- 法律法规：`https://www.pkulaw.com/chl/XXXXXbdfb.html`
- 司法案例：`https://www.pkulaw.com/pfnl/XXXXXbdfb.html`
- 指导性案例：`https://www.pkulaw.com/gac/XXXXXbdfb.html`
- 学术文章：`https://www.pkulaw.com/qikauthor_qikan/XXXXXbdfb.html`

## Step 4：核验与交付

无论用 MCP 还是网页，都要做最小核验：

- 标题是否与用户要找的对象一致。
- 法条是否是正确法律、正确条号、正确款项。
- 案例是否是正确案号、法院、日期。
- 链接是否来自 `pkulaw.com`。
- 如果引用到正文或脚注，格式是否符合 `legal-citation-comprehensive`。

交付格式建议：

```markdown
检索结果：

1. 《中华人民共和国民法典》第153条
   来源：北大法宝
   链接：...
   核验：条文内容与当前分析所引规则一致。

2. 案例名称，法院，案号
   链接：...
   相关性：...
```

## 常见问题处理

### MCP 找不到结果

- 换关键词：法律简称/全称、案由、法院、案号、核心事实。
- 换关键词：法律简称/全称、案由、法院、案号、核心事实。
- 转网页端搜索，尤其是需要登录后数据库、详情页、条文全文或高级筛选时。

### 网页需要登录

- Codex 中优先 Computer Use 使用本机浏览器/IP 登录状态。
- 不要反复无头刷新登录页。
- 如果页面提示机构登录/IP 登录失败，说明当前网络或账号状态不足，应如实告知。

### MCP 和网页结果不一致

- 以详情页标题、案号、法条原文为准。
- 对法条，优先使用权威原文 MCP/详情页；必要时说明版本或修正日期。
- 对案例，优先案号一致，其次法院和审结日期一致。

### 链接不可公开访问

- 仍可提供北大法宝详情页链接，并说明可能需要学校/IP/VIP 权限。
- 不要伪造公开链接。

## 与其他技能配合

- `legal-fact-checker`：法律产出事实核查，防止编造法规/案例。
- `legal-citation-comprehensive`：把检索结果转成规范脚注。
- `legal-homework-formatter`：把引注和链接写入最终 Word 作业。
- `quote-normalizer`：处理中文弯引号。

## 注意事项

1. 不要默认 camoufox 是第一选择；它只是网页检索后备。
2. 不要在 MCP 可直接查到法条/案例时浪费时间模拟浏览器。
3. 不要编造北大法宝链接；没有链接就说没有取得。
4. 如果使用网页，应尽量记录详情页 URL，而不是搜索结果页 URL。
5. 需要登录/IP 权限的内容，应说明访问限制。
