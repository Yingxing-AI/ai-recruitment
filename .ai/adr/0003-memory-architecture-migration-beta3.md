# ADR 0003: 项目记忆层迁移到 Project Copilot v0.3.0-beta.3 架构

日期：2026-06-20

状态：Accepted

背景：

当前项目的 `.ai/` 仍停留在 beta.1 风格，核心写入面以 `PROJECT_CONTEXT.md`、`DECISIONS.md`、`WORKLOG.md` 和 `metrics.md` 为主，缺少 Charter、ADR 目录、Session Archive 和 derived metrics。继续沿用旧结构会导致上下文恢复、长期记忆治理和验证口径与 `Project Copilot v0.3.0-beta.3` 脱节。

决策：

把当前项目记忆层迁移到 `Project Copilot v0.3.0-beta.3` 风格：新增 `PROJECT_CHARTER.md`、`adr/`、`sessions/current.md`、`sessions/archive/` 和 `derived/metrics.json`，保留旧文件作为 Compatibility 或 Legacy，不删除历史。

原因：

新架构把长期边界、决策、候选事件和归档摘要分层，能够保证“开始今天工作”只读恢复上下文，“今天结束工作”才写入 Session Archive，并让 Validation 与 Memory Health 重新对齐官方口径。

取舍：

需要同时维护一段时间的 Compatibility/Legacy 文件，短期内结构更复杂；但这比直接删除旧文件更安全，也能避免历史丢失。

影响：

后续新决策优先写入 `adr/`，开发过程中只维护 `sessions/current.md` 候选区；`PROJECT_CONTEXT.md`、`DECISIONS.md`、`WORKLOG.md`、`HYPOTHESES.md` 和 `metrics.md` 不再作为主活跃层。
