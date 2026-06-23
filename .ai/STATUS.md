# Status

更新日期：2026-06-23

当前阶段：稳定维护，已完成招聘业务流程式导航收口

当前重点：

- 使用 `PROJECT_CHARTER + ADR + Session Archive` 恢复招聘项目上下文
- 保持招聘 MVP 业务闭环稳定，优先修复本地演示和验证阻塞
- 把前端导航从“功能模块式”收口为“招聘业务流程式”
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
- 前端开发链路：Vite 默认端口已调整为 `3001`，并与 Docker 正式入口 `3000`、后端默认 CORS 同步对齐
- 前端导航：一级菜单已改为 `仪表盘 / 招聘中心 / 面试中心 / 人才库 / 系统设置`，`简历导入` 与 `AI 招聘` 已迁出一级导航
- 页面整合：候选人详情已整合简历上传、解析、候选人总结、岗位匹配与面试问题；职位详情已整合候选人匹配评分与推荐结论
- 兼容入口：旧 `resume-import` / `ai-recruitment` 路由保留为重定向入口，不再作为主导航
- 正式入口验证：已重新拉起 Docker Compose，`http://localhost:3000` 和 `http://localhost:8000/api/v1/health` 均返回正常
- `worker` 命名排查：已确认异常容器属于当前 Compose 项目，且是历史替换残留；尝试单独重建 `worker` 时被 Docker daemon 拒绝停止旧容器
- 验证结果：`npm run build` 通过，`make test` 通过（27 passed）
- 业务代码：本次已修改前端路由、侧边栏结构、候选人/职位详情工作台和产品文档

当前风险：

- `PROJECT_CONTEXT.md`、`DECISIONS.md`、`WORKLOG.md`、`HYPOTHESES.md` 和 `metrics.md` 仍保留为 Compatibility/Legacy，后续需要避免继续作为主写入面
- `WORKLOG.md` 仍承载旧流水账，按 beta.3 Memory Health 口径会持续被判定为记忆漂移，直到后续历史沉淀进一步收敛
- 当前 Docker 环境仍存在遗留 `worker` 容器命名冲突；不影响 `backend` / `frontend` 浏览产品界面，但后续需要清理
- Docker Compose 现已恢复运行，但 `worker` 容器仍以非标准名称 `f384d9dbc1a7_ai-recruitment-worker-1` 启动；后续若继续做环境治理，需确认其来源并清理命名漂移
- 当前 Docker daemon 对停止该 `worker` 容器返回 `permission denied`，导致无法在本会话内完成标准命名恢复

下一步任务：

- 后续开始开发时优先读取 `PROJECT_CHARTER.md`、`STATUS.md`、`ROADMAP.md` 和 `adr/`
- 如需继续清理环境，优先处理 `worker` 容器命名漂移并确认是否存在 orphan / duplicate Compose 状态
- 如需根治 `worker` 命名漂移，需先解决 Docker daemon 对 `stop/remove` 的权限拒绝，再执行 `worker` 单独重建
- 当前“面试反馈”入口仍基于已有面试状态与记录做反馈视角展示，后续如需完整表单化反馈，需要单独确认是否扩展现有面试数据模型
- Docker 正式前端入口已恢复，后续重点转为确认 `worker` 服务命名和启动链路是否可长期稳定复现
- 结束工作时仅把三个月后仍重要的候选事件写入 ADR、Memory、Knowledge 或 Session Archive
