# LawPilot — 中国法审查 Agent

LawPilot 帮助整理合同中的关键问题、对应原文和待确认事项。输入合同、附件及我方立场后，Agent 会选择适用工作流，读取和检索材料，生成供人工复核的审查草稿。

项目使用 Python 和 Streamlit，可独立启动。支持无密钥演示和 OpenAI Agent 两种运行方式。

## 工作流程

```text
合同与附件 + 我方立场
        ↓
选择审查工作流
        ↓
读取材料、搜索相关原文
        ↓
整理核心问题与修改建议
        ↓
校验证据引用、列出信息缺口
        ↓
人工复核与记录导出
```

- **按任务选择工作流**：支持合同、NDA、尽调问题提取和证据时间线。
- **保留原文依据**：发现项关联材料 ID 和原文，程序检查引用是否出现在本次已读取的内容中。
- **显示审查范围**：保留工具执行记录，明确标出未读范围、缺失资料和待核验依据。
- **人工复核**：审查结果为草稿，可记录处理意见并导出 JSON。

## 快速开始

Python 3.9+，建议使用独立虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

打开终端显示的本地地址，填写我方立场，粘贴合同或上传 UTF-8 TXT / Markdown 附件，再点击“开始审查”。内置合同为合成示例。

### 运行方式

| 模式 | 用途 | 配置 |
|---|---|---|
| 无密钥演示 | 体验输入、结果展示和人工复核流程，采用关键词规则 | 无需 API key |
| OpenAI Agent | 由模型自主选择工具并生成结构化审查草稿 | 配置 `OPENAI_API_KEY` |

使用 OpenAI 模式时，在 `.env` 中填写密钥。`OPENAI_MODEL` 默认为 `gpt-4o-mini`，可替换为账户可用且支持 Structured Outputs 的模型。材料会发送给 OpenAI，调用费用由对应账户承担。请勿将 `.env` 提交到仓库。

## Agent 如何运行

Agent 可以读取领域工作流、读取文档分段、按关键词搜索材料或提交审查报告。每次任务最多执行 12 步，每步最多输出 4500 tokens。

文档以材料数据处理，其中的操作指令不会直接执行。可用工具不包含任意路径读取、Shell 或网络访问。检索采用字符关键词匹配，可能遗漏同义表达或未命中的上下文。

报告最多列出 5 项核心发现。引用不匹配时，程序要求模型修正；达到步数上限仍未完成的任务会返回未完成状态。原文匹配只能确认引文存在，法律解释和建议仍需专业人员复核。

## 测试与评估

```bash
python3 -m unittest -v
python3 prepare_case.py C02 --out .local/C02
python3 evaluate.py example-scores.json
```

测试集包含 8 组模拟合同和 2 份附件，覆盖金额矛盾、附件冲突、我方立场变化及提示注入等情况。`prepare_case.py` 只导出待审材料，不导出评分答案；如需隔离评测，应在独立环境中运行审查任务。

自动测试覆盖工具调用、原文引用校验、步数上限、未读范围、安装保护和评分计算。评分脚本汇总人工逐项评分，并单独展示关键失败。`example-scores.json` 用于演示评分格式与计算，不代表独立 Agent 的效果评估。

OpenAI 接口目前通过模拟响应测试，真实 API 的端到端运行尚待验证。合成样例和程序测试不构成法律准确性证明。

## Codex 集成

项目也提供 Codex Skill 和子 Agent 配置。可先安装到独立目录检查：

```bash
python3 install.py --dest .local/demo-config
```

安装到 Codex 配置目录：

```bash
python3 install.py --dest ~/.codex
```

安装脚本校验压缩包并填充本机路径，遇到已有同名 Skill 或角色时停止，不覆盖现有配置。客户端需要支持自定义角色；安装后可在新会话中调用 `china_legal`，并指定材料目录、我方立场和交付范围。

## 项目结构

| 文件 | 用途 |
|---|---|
| `app.py` | 网页界面、人工复核与导出 |
| `agent.py` | Agent 循环、工具与证据校验 |
| `workflow-bundle.zip` | 法律工作流及依赖资料 |
| `china_legal.toml` / `install.py` | Codex 角色配置与安装 |
| `testset.zip` / `TESTSET.md` | 合成材料与评测说明 |
| `prepare_case.py` | 导出单组待审材料 |
| `evaluate.py` | 汇总人工评分 |
| `test_agent.py` / `test_workflow.py` | 自动测试 |

## 使用范围

当前支持 TXT 和 Markdown，不解析 PDF、Word 或扫描件。材料和结果保留在当前会话中，可下载留档；尚未提供多用户权限或持久化数据库。

项目未连接权威法律数据库，法规版本、适用性及法律结论均需另行核验。输出用于辅助整理和专业审阅，不替代正式法律意见。

## 开源来源

法律工作流采用 [Claude for Legal 中国法版本](https://github.com/CSlawyer1985/claude-for-legal-ZH)，遵循 Apache-2.0 许可。来源版本和文件范围见 [UPSTREAM.md](UPSTREAM.md)，许可全文见 [LICENSE](LICENSE)。
