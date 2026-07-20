# 第三方优秀法律 Skills 推荐 / Recommended Third-Party Legal Skills

这个页面是推荐索引，不是第三方源码镜像。为了尊重作者授权，本仓库只提供链接、用途说明、许可证提醒和安装协调脚本；安装时应从原作者 GitHub 仓库直接克隆。

This page is a recommendation index, not a mirror of third-party source code. This repository only provides links, use cases, license notes, and an installer that clones from the original GitHub repositories.

## 快速安装 / Quick Install

先查看清单：

```bash
python3 scripts/install_third_party_skills.py --list
```

默认只安装许可证允许自动再分发和改造的项目：

```bash
python3 scripts/install_third_party_skills.py
```

安装受限许可项目前，请先阅读原仓库 `LICENSE`。确认后再显式运行：

```bash
python3 scripts/install_third_party_skills.py --all --accept-restricted-licenses
```

指定安装某几个项目：

```bash
python3 scripts/install_third_party_skills.py --only gutachten-civil-case,gutachten-criminal-case
```

默认安装目录是 `~/.codex/skills`，可以改成你的 AI 运行时目录：

```bash
python3 scripts/install_third_party_skills.py --skills-dir ~/.workbuddy/skills
```

## 给 AI 的一句话 / One-Prompt Install

```text
请打开 https://github.com/NEU-ZHA/legal-ai-skills，阅读 THIRD_PARTY_RECOMMENDED_SKILLS.md 和 third_party_skills.json，然后运行 scripts/install_third_party_skills.py 帮我安装第三方法律 skills。默认先安装 Apache-2.0 项；CC BY-NC-ND 或带附加条款的项目，先解释许可证限制并等我确认后再从原作者仓库克隆，不要改写、不要合并进我的仓库、不要用于训练或向量知识库。
```

## 推荐项目 / Recommended Projects

| 项目 | 作者 | 适合场景 | 许可证与安装策略 |
| --- | --- | --- | --- |
| [gutachten-civil-case](https://github.com/Youchu-lawhub/gutachten-civil-case) | 游初 / Youchu-lawhub | 中国民法请求权基础、德国鉴定式案例分析、法学生民法案例研习 | Apache-2.0；可默认自动安装；保留上游 LICENSE 和署名 |
| [gutachten-criminal-case](https://github.com/Youchu-lawhub/gutachten-criminal-case) | 游初 / Youchu-lawhub | 刑法三阶层、鉴定式刑法案例研习、罪名检视工作流 | Apache-2.0；可默认自动安装；保留上游 LICENSE 和署名 |
| [gutachten-admin-case](https://github.com/Youchu-lawhub/gutachten-admin-case) | 游初 / Youchu-lawhub | 行政法鉴定式案例研习、行政行为合法性审查、比例原则与裁量审查 | CC BY-NC-ND 4.0 + 附加条款；需用户确认；不得公开分发修改版 |
| [cn-litigation-toolkit](https://github.com/Youchu-lawhub/cn-litigation-toolkit) | 游初 / Youchu-lawhub | 中国民商事诉讼工具箱、证据、起诉答辩、质证、庭审、代理意见等实务流程 | CC BY-NC-ND 4.0；需用户确认；建议从上游原样安装 |
| [app-compliance-review](https://github.com/Youchu-lawhub/app-compliance-review) | 游初 / Youchu-lawhub | APP 个人信息保护合规检查、隐私政策与 APK 静态分析、整改清单 | CC BY-NC-ND 4.0 + 附加条款；需用户确认；不得公开分发修改版 |
| [legal-kb-builder](https://github.com/Youchu-lawhub/legal-kb-builder) | 游初 / Youchu-lawhub | 本地法律知识库建设、PDF/DOCX/图片材料处理、业务咨询智能体准备 | CC BY-NC-ND 4.0 + 附加条款；需用户确认；不得公开分发修改版或用于训练/RAG 来源 |

## 许可证原则 / License Principles

- Apache-2.0 项目可以复制、修改和再分发，但必须保留许可证、版权声明和必要署名；修改版应标明已修改。
- CC BY-NC-ND 或带附加条款的项目不要改写后公开发布，也不要合并进本仓库当作自有 skill 分发。
- 本仓库的安装脚本只做本地安装协调：从上游仓库 `git clone`，再把 skill 路径复制或链接到本机 skills 目录。
- 如果用户、机构或课程场景可能涉及商业使用、收费服务、企业/行政机关内部使用、AI 训练、向量知识库或平台上架，请先阅读原仓库 LICENSE，必要时联系作者取得单独授权。

## 给维护者的规则 / Maintainer Rules

- 不把第三方源码、模板、样例报告或方法论全文复制到本仓库。
- 不把受限许可项目改名、改结构后作为本仓库自有内容发布。
- 推荐页可以说明用途和安装方式，但应持续指向原作者仓库。
- 新增第三方项目时，先更新 `third_party_skills.json`，并写明 `license_verified_on` 日期。
