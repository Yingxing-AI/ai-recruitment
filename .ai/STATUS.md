# Status

更新日期：2026-06-20

当前阶段：记忆层迁移完成，进入稳定维护

当前重点：

- 使用 `PROJECT_CHARTER + ADR + Session Archive` 恢复招聘项目上下文
- 保持招聘 MVP 业务闭环稳定，不在本次迁移中修改业务代码
- 让“继续开发 / 开始今天工作”保持只读恢复，“今天结束工作”才写入 Session Archive
- 统一根目录验证入口，避免误用系统 `pytest`

当前状态：

- 记忆架构：`Project Copilot v0.3.0-beta.3` 风格，保留 beta.1 兼容层
- 长期边界：`.ai/PROJECT_CHARTER.md`
- 决策主层：`.ai/adr/`
- 会话层：`.ai/sessions/current.md` 和 `.ai/sessions/archive/`
- 指标主层：`.ai/derived/metrics.json`
- Validation：已按 beta.3 快照口径刷新
- 根目录验证入口：`make test` / `make lint-backend`
- 业务代码：本次未修改
- Git / Release / README：本次未自动写入

当前风险：

- `PROJECT_CONTEXT.md`、`DECISIONS.md`、`WORKLOG.md`、`HYPOTHESES.md` 和 `metrics.md` 仍保留为 Compatibility/Legacy，后续需要避免继续作为主写入面
- `WORKLOG.md` 仍承载旧流水账，按 beta.3 Memory Health 口径会持续被判定为记忆漂移，直到后续历史沉淀进一步收敛

下一步任务：

- 后续开始开发时优先读取 `PROJECT_CHARTER.md`、`STATUS.md`、`ROADMAP.md` 和 `adr/`
- 结束工作时仅把三个月后仍重要的候选事件写入 ADR、Memory、Knowledge 或 Session Archive
