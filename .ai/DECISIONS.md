# Decisions

说明：旧版决策索引。新决策优先写入 `.ai/adr/`，本文件只保留兼容摘要。

## 兼容索引

- [ADR 0001: MVP 使用规则驱动，不依赖外部 AI API](adr/0001-rule-driven-mvp.md)
- [ADR 0002: Phase 4 聚焦 V1 产品化收口](adr/0002-phase-4-v1-productization.md)
- [ADR 0003: 项目记忆层迁移到 Project Copilot v0.3.0-beta.3 架构](adr/0003-memory-architecture-migration-beta3.md)
- [ADR 0004: Docker Compose 依赖服务走宿主机网关](adr/0004-docker-host-gateway-networking.md)

## Legacy 决策摘录

## ADR-0001: v0.1 使用规则驱动

原因：MVP 不依赖外部 API，优先保证本地可运行。

## ADR-0002: Phase 4 聚焦 V1 产品化

日期：2026-06-18

决策：Phase 4 不再继续新增 AI 功能，优先完成 V1 产品化收口，包括管理仪表盘、演示数据、部署文档、验收测试和 README 产品化。

原因：核心招聘闭环和规则版 AI 已经可用，当前最需要的是稳定性、可演示性和交付文档，而不是继续扩展 AI 能力。

影响：后续开发优先级转向产品化收口；真实 LLM Provider 接入继续后置，除非另行确认。

日期：2026-06-20

决策：项目记忆层迁移到 Project Copilot v0.3.0-beta.3 架构。

原因：现有 `.ai` 仍停留在 beta.1 风格，缺少 `PROJECT_CHARTER`、`ADR`、`Session Archive` 和 `derived metrics` 分层，已影响上下文恢复与验证治理口径。

影响：后续新决策优先写入 `.ai/adr/`；`WORKLOG.md`、`HYPOTHESES.md` 和 `metrics.md` 只保留为 Legacy/Compatibility，不再作为主写入面。

日期：2026-06-22

决策：Docker Compose 下的 `backend` / `worker` 默认通过宿主机网关访问 PostgreSQL、Redis 和 MinIO，并在应用启动阶段增加数据库重试。

原因：当前环境中容器间 DNS 可解析但 TCP 不通，导致后端无法完成启动。

影响：本地产品界面和演示数据链路恢复稳定；后续如容器桥接网络恢复正常，可再评估是否回退为服务名直连。
