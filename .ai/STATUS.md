# Status

更新日期：2026-06-22

当前阶段：稳定维护，已修复本地后端启动阻塞

当前重点：

- 使用 `PROJECT_CHARTER + ADR + Session Archive` 恢复招聘项目上下文
- 保持招聘 MVP 业务闭环稳定，优先修复本地演示和验证阻塞
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
- 后端启动：已增加数据库重试，Docker Compose 下默认通过宿主机网关访问依赖服务
- 前端代理：已改为通过宿主机网关访问后端；当前 Docker 旧 `frontend` 容器因守护进程权限未完成替换，临时可用入口为本地 Vite `3001`
- 业务代码：本次已修改后端启动与部署配置
- Git / Release / README：本次未自动写入

当前风险：

- `PROJECT_CONTEXT.md`、`DECISIONS.md`、`WORKLOG.md`、`HYPOTHESES.md` 和 `metrics.md` 仍保留为 Compatibility/Legacy，后续需要避免继续作为主写入面
- `WORKLOG.md` 仍承载旧流水账，按 beta.3 Memory Health 口径会持续被判定为记忆漂移，直到后续历史沉淀进一步收敛
- 当前 Docker 环境仍存在遗留 `worker` 容器命名冲突；不影响 `backend` / `frontend` 浏览产品界面，但后续需要清理
- 当前 Docker 守护进程不允许停止旧 `frontend` 容器，导致新 Nginx 代理配置尚未接管 `3000`

下一步任务：

- 后续开始开发时优先读取 `PROJECT_CHARTER.md`、`STATUS.md`、`ROADMAP.md` 和 `adr/`
- 如需继续清理环境，优先处理遗留 `worker` 容器命名冲突
- 如需恢复 Docker 正式前端入口，需清理或重启当前 `frontend` 容器
- 结束工作时仅把三个月后仍重要的候选事件写入 ADR、Memory、Knowledge 或 Session Archive
