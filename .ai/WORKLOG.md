# Worklog

## 2026-06-16 11:24

- 已更新项目状态。
- 下一步：补齐项目初始化文件和 .ai 项目记忆。
- 下一步：根据 ROADMAP 选择最高优先级任务继续开发。

## 2026-06-16 15:50

- 完成项目状态分析：后端测试通过，前端构建通过。
- 补充 GitHub Actions CI：后端测试与前端构建分 job 执行。
- 后端 `pyproject.toml` 补充 build-system，便于 CI 和开发环境安装。
- 更新 README 开发验证命令。
- 更新 `.ai` 项目上下文、状态和 roadmap。

## 2026-06-16 16:05

- 前端改为路由级懒加载，页面按 route 生成独立 chunk。
- Vite 增加 react、query、antd vendor chunk 拆分。
- 构建入口业务包显著缩小，Ant Design 保持为共享缓存 chunk。

## 2026-06-16 16:15

- 补齐 Alembic 迁移环境：`env.py`、`script.py.mako`、`versions/`。
- 生成初始 schema 迁移 `5f6650966c99_initial_schema.py`。
- 使用 SQLite 验证 `alembic upgrade head` 与 `alembic downgrade base` 均通过。

## 2026-06-16 16:30

- 新增核心 CRUD API 路由测试：职位、候选人、应聘阶段、面试创建和引用校验。
- 后端测试从 5 个增加到 10 个。
- 当前 `.venv/bin/python -m pytest backend/app/tests` 通过。

## 2026-06-16 收工

- 今日完成 CI、开发验证文档、前端路由级代码拆分、Alembic 初始迁移、核心 CRUD API 测试。
- 最终验证：后端测试 10 passed；前端生产构建通过；Alembic upgrade/downgrade 已用 SQLite 验证。
- 当前未提交改动包括 `.ai/`、`.github/`、Alembic 迁移、后端测试、README、前端分包配置与路由懒加载。
- 下一次建议从“简历导入异常场景补测”开始。

## 2026-06-17 12:04

- 读取 `.ai` 全部项目记忆文件，并评估项目档案质量。
- 补齐 `PROJECT_CONTEXT.md` 中的 AI 招聘系统使命、目标用户、商业目标、MVP 范围和完整技术栈。
- 加固简历上传接口：空文件返回 400；解析异常写入 `parse_status=failed` 和 `parse_error`，避免请求直接 500。
- 新增简历导入异常场景测试：空文件、解析失败、候选人不存在、职位不存在。
- 验证：`.venv/bin/python -m pytest backend/app/tests`，14 passed。

## 2026-06-17 12:35

- 完成 OSS 准备度检查。
- 新增 `CONTRIBUTING.md`，说明开发环境、提交前检查、代码约定和 MVP 范围控制。
- 新增 `SECURITY.md`，说明漏洞报告、密钥处理和部署安全边界。
- 新增 `docs/OSS_READINESS.md`，记录当前开源准备结论、发布前检查、已知缺口和下一步建议。
- 更新 `.dockerignore`，排除 `.env`、缓存、上传目录等本地敏感或生成内容。
- 更新 README 开源协作入口，并将 `deploy/docker/backend.env.example` 的 MinIO 示例密钥改为占位符。
- 验证：`.venv/bin/python -m pytest backend/app/tests`，14 passed；`npm run build` 通过。

## 2026-06-18 10:08

- 完成自然语言工作流 MVP：新增规则驱动的工作流意图解析接口，支持简历解析、候选人总结、岗位匹配和面试题生成。
- AI 招聘页新增自然语言工作流面板，可输入中文指令并基于当前简历、职位和候选人选择执行建议动作。
- 新增后端单元测试覆盖意图识别、缺参提示和未知意图分支。
- 遇到问题：意图匹配初版过于依赖固定短语，已改为“关键短语 + 必要上下文”组合识别。
- 明日计划：继续推进真实 LLM provider 接入方案。

## 2026-06-18 10:28

- 完成发布流程和生产安全基线：新增 `CHANGELOG.md`、`docs/RELEASE.md`、`docs/PRODUCTION_SECURITY.md`，补齐 GitHub issue/PR 模板。
- 后端生产配置增加校验：禁止默认占位 `SECRET_KEY`、SQLite 数据库和未替换的 MinIO 凭据。
- Nginx 入口增加基础安全头与上传体积限制。
- 设置页新增“发布与安全”信息块，方便前端直接查看当前基线。
- 验证：`.venv/bin/python -m pytest backend/app/tests`，19 passed；`npm run build` 通过。
- 明日计划：规划真实 LLM provider 接入方案。

## 2026-06-18 10:27

- 完成招聘主流程打磨：职位详情页和候选人详情页现在可查看岗位/候选人信息、AI 结果、应聘、面试和留痕。
- 完成数据留痕：职位、候选人、应聘、面试和 AI 工作流相关动作会写入 `audit_logs`，并可按目标对象查看。
- 完成数据留存策略：新增留存脚本，可清理过期审计日志并清空老旧 AI 中间响应。
- 完成部署验证：新增烟雾测试和部署验证文档，覆盖核心招聘链路和留存逻辑。
- 完成前端可用性优化：职位和候选人列表可直达详情页，设置页增加数据留存区块。
- 验证：`.venv/bin/python -m pytest backend/app/tests`，22 passed；`npm run build` 通过。
- 明日计划：等待用户选择下一优先级，LLM provider 接入已后置。

## 2026-06-18 10:38

- 补完人才库页的菜单链路：筛选按钮接入本地过滤，推荐到职位按钮可跳转职位管理。
- 复查主菜单和详情页链路，未发现新的断链点；当前仅登录页仍是静态入口，不属于主菜单链路。
- 遇到问题：人才库页原先只有静态按钮，没有任何可执行动作。
- 明日计划：继续按用户优先级推进剩余入口或后续版本需求。
