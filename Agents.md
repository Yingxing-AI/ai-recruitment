# Agents

## 当前阶段

项目当前进入 Phase 4：V1 产品化。

## 开发边界

- 不新增付费 AI API 接入。
- 不扩展超出当前 MVP 的大功能。
- 优先稳定性、文档、演示、测试和部署收口。
- 当前 AI 能力保持规则版，后续仅预留真实 LLM Provider 接口。

## 标准运行约定

- 前端默认端口：`3000`
- 后端默认端口：`8000`
- 一键启动：`docker compose up --build -d`

## 开发前后要求

- 开发前先读 `.ai/PROJECT_CONTEXT.md`、`.ai/STATUS.md`、`.ai/ROADMAP.md`、`.ai/DECISIONS.md`
- 开发后更新 `.ai/STATUS.md`、`.ai/WORKLOG.md`
- 发生重要事实、里程碑或决策变化时，同步 `.ai` 相关文件

## 验收优先级

1. 可启动
2. 可演示
3. 可验证
4. 可维护
