# LawPilot — 独立中国法审查 Agent

面向合同审查、证据梳理与尽调的个人 AI 协作项目。**基于开源 Claude for Legal 中国法版本进行 Codex 适配**，重点是任务路由、原文定位、来源核验、人工复核和可复现评测。现提供可独立启动的 Python Agent 与 Streamlit 界面，不依赖 Codex 执行。另保留原 Codex 适配包。不是自研法律大模型或已上线的 SaaS。

## 30 秒了解

**明确立场 → 读取合同与附件 → 按领域选择工作流 → 提取问题与原文 → 核验依据 → 人工复核。**

- 原项目：统一 Skill、13 类领域路由、Codex 子 Agent 角色配置、8 组模拟合同、C02 单例试测。
- 本次完善：新增独立 Python Agent / 网页入口与工具循环，并消除个人绝对路径，增加不覆盖已有配置的安装脚本、测试材料隔离导出、人工评分汇总脚本及自动测试。
- 上游提供 157 项 Skills；本项目工作是适配和评测，不将其算作原创代码量。完整来源与提交见 [UPSTREAM.md](UPSTREAM.md)，保留 Apache-2.0 许可。

## 独立 Agent：快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

浏览器打开本地地址。默认无密钥演示；在 `.env` 填入自己的 `OPENAI_API_KEY`，选择 **OpenAI Agent** 即可运行真实循环。模型由 `OPENAI_MODEL` 配置，需使用账户有权限且支持 Structured Outputs 的模型。API 费用由该账户承担，材料会发给 OpenAI；不把密钥提交到仓库。

支持粘贴合同和上传 UTF-8 TXT/Markdown 附件。PDF、Word、OCR 暂未接入此独立界面；历史测试资料与 Codex 路径另存。模型自主选择四种行动：读取领域工作流、读取文档分段、关键词检索、提交报告；最多 12 步，每步最多 4500 输出 tokens。程序验证报告引用来自本次工具已读内容，保留未读范围和工具记录，再要求人工复核。检索是字符关键词匹配，不是向量 RAG。

全程没有任意文件读取、Shell 或网络检索工具，文档内命令不会直接执行。法律依据统一列为待人工核验；原文匹配仅保证引用存在，不保证模型解释正确。结果保存在会话，可下载 JSON，尚无多用户权限与持久化数据库。

真实 API 尚未在本次交付中端到端调用验证（未使用用户密钥）；已用模拟模型验证自主工具循环、引用拒绝、步数上限和人工复核状态。演示模式是规则基线，不能展示为模型效果。

## 可选：原 Codex 工作流安装

此可选路径使用 Python 3.9+；安装、准备材料、评分仅用标准库，无需 API key。法律审查本身需要可用的 Codex 客户端、模型权限和用户允许的检索能力，不能用 Python 测试通过代替 AI 审查成功。

```bash
# 先在独立目录验证，不改变已有 Codex 配置
python3 install.py --dest .local/demo-config
python3 prepare_case.py C02 --out .local/C02
python3 -m unittest -v
python3 evaluate.py example-scores.json
```

要安装到自己的 Codex，可执行 `python3 install.py --dest ~/.codex`。已有同名 Skill 或角色时脚本拒绝覆盖。新会话中让主 Agent 调用 `china_legal`，仅提供 `.local/C02` 材料目录，按 `REVIEW_TASK.md` 输出。客户端须支持自定义角色；若名称加载不可用，可让真实子 Agent 显式读取生成的角色规则，并如实记录调用方式。

## 仓库内容

| 文件 | 用途 |
|---|---|
| `workflow-bundle.zip` | 已有完整工作流快照（省略上游宣传图片），保留目录和许可证；安装脚本解压 |
| `china_legal.toml` | 可浏览的角色模板；安装时替换路径 |
| `testset.zip` / `TESTSET.md` | 8 组模拟合同、2 份附件、评测专用检查点 |
| `prepare_case.py` | 只导出候选材料，不导出答案；共享文件系统不构成强隔离 |
| `evaluate.py` | 汇总人工逐项评分，关键失败单独展示 |
| `C02-review.md` / `C02-evaluation.md` | 2026-09-23 历史试测报告与人工评分 |

## 评测结果与边界

历史 C02 试测覆盖 **5/5 个预设文本/商业检查点**，加权覆盖为 13/13；不是法律准确率，不代表全部 8 组均测过。报告仍有冗长和非核心提示问题，因此新任务模板优先展示最多 5 项核心问题。

`example-scores.json` 是根据历史评分制作的汇总示例，不是本次重新运行模型所得。评分人必须单独核验新增误报、立场、引用及注入行为；代码无法自动判定专业法律正确性。未接入专用法律数据库，法规版本及适用性须在实际审查时核验。此仓库不发布客户合同，测试材料均为合成。

## 简历中的准确表述

> 基于开源法律工作流构建独立中国法审查 Agent 原型，实现自主工具选择、材料检索、原文引用校验与人工复核；复用 8 组模拟合同测试集，并保留 Codex 子 Agent 适配和历史单例试测记录。
