# Security Policy

## Supported Versions

当前项目处于 `0.1.x` MVP 阶段，只维护 `main` 分支上的最新代码。

## Reporting a Vulnerability

如果发现安全问题，请不要公开提交可利用细节。请通过私有渠道联系项目维护者，并提供：

- 受影响的版本或提交
- 复现步骤
- 影响范围
- 建议修复方式

维护者确认后会优先处理，并在修复可用后再公开说明。

## Secret Handling

- 不要提交 `.env`、真实数据库密码、对象存储密钥或 LLM API Key。
- `.env.example` 和 `deploy/docker/*.env.example` 只允许放示例值。
- Docker Compose 中的默认密码仅用于本地开发，生产部署必须通过环境变量替换。
- 生产环境必须替换 `SECRET_KEY`、数据库密码、MinIO 账号密码，并收紧 CORS 来源。

## Deployment Notes

- 默认配置面向本地开发，不应直接暴露到公网。
- 上传的简历可能包含个人敏感信息，生产环境需要配置访问控制、存储加密、备份策略和日志脱敏。
- 接入真实 LLM Provider 时，不要把简历原文、API Key 或模型响应写入公开日志。
