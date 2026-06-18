# Data Retention Strategy

这个项目采用“保留业务事实，定期清理敏感中间产物”的策略。

## 默认策略

- `audit_logs`：保留 180 天，之后删除。
- `AIResumeAnalysis.raw_response`：保留 90 天，之后清空。
- `JobMatchScore.raw_response`：保留 90 天，之后清空。
- 简历原文和解析结果：默认保留，交由项目方按合规要求决定是否缩短保存周期。

## 适用目的

- 保留招聘决策链路，便于复盘和审计。
- 降低敏感内容长期留存的风险。
- 让后续上线前能够按业务要求逐步收紧保留策略。

## 执行方式

使用后端留存脚本：

```bash
cd backend
python -m app.scripts.retention_cleanup --audit-days 180 --ai-days 90
```

可先 dry run：

```bash
cd backend
python -m app.scripts.retention_cleanup --dry-run
```

## 说明

- 目前策略偏保守，只清理审计日志和 AI 中间响应。
- 如需进一步收紧简历原文或对象存储文件的保存周期，应先确认招聘业务的合规要求和回溯需求。
