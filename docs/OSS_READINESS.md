# OSS Readiness

本文件记录项目开源准备度检查结果，作为发布前清单维护。

## 当前结论

状态：基本具备开源协作基础，但还不建议直接面向生产用户发布稳定版。

已具备：

- `LICENSE` 已存在。
- `README.md` 包含项目定位、技术栈、本地启动、验证命令和核心 API。
- `.env.example` 已提供本地开发配置模板。
- `.gitignore` 已排除 `.env`、虚拟环境、缓存、构建产物、上传文件和本地数据库。
- GitHub Actions 已包含后端测试和前端构建。
- `CONTRIBUTING.md` 已说明开发、提交前检查和范围控制。
- `SECURITY.md` 已说明漏洞报告、密钥处理和部署安全边界。

## 发布前必须检查

- 后端测试通过：`.venv/bin/python -m pytest backend/app/tests`
- 前端构建通过：`cd frontend && npm run build`
- Docker Compose 可从干净环境启动：`cp .env.example .env && docker compose up --build`
- `git status --short` 无未预期变更。
- `git ls-files .env` 无输出。
- 敏感信息扫描无真实密钥、真实密码、生产域名凭证或个人数据样本。
- README 中的启动命令、服务端口和 API 列表与代码一致。
- 数据库模型与 Alembic 迁移一致。

## 已知缺口

- 缺少正式 release 流程和版本变更日志。
- 缺少 issue/PR 模板。
- 缺少容器镜像发布流程。
- 缺少生产部署安全基线文档。
- 真实 LLM Provider 接入方案尚未确定。
- 上传简历涉及个人信息，生产使用前需要补充隐私和数据保留策略。

## 安全注意事项

- `.env.example` 和 Compose 默认值仅供本地开发。
- 生产环境必须替换 `SECRET_KEY`、数据库密码、MinIO 账号密码和 LLM API Key。
- 生产环境必须收紧 `BACKEND_CORS_ORIGINS`。
- 不要提交真实简历、候选人个人信息或内部职位数据。

## 下一步建议

1. 增加 issue/PR 模板。
2. 增加 `CHANGELOG.md` 和 release checklist。
3. 补充真实 LLM Provider 接入设计。
4. 补充生产部署安全基线。
