# Project Context

项目名称：ai-recruitment

项目是什么：企业内部使用的 AI 招聘管理系统 MVP。

项目目标：提供职位管理、简历导入、候选人管理、规则版 AI 简历分析、岗位匹配评分、面试流程管理和人才库沉淀能力。

目标用户：企业招聘团队、HRBP、招聘负责人和参与面试的业务负责人。

技术栈：
- 前端：React + TypeScript + Vite + Ant Design
- 后端：FastAPI + SQLAlchemy + Pydantic + Alembic
- 数据库：PostgreSQL，测试可用 SQLite
- 缓存/任务队列：Redis
- 文件存储：本地存储或 MinIO
- 部署：Docker Compose + Nginx
- AI：规则版 mock provider，保留 LLM provider 抽象

现有线索：
- docker-compose.yml
- backend/
- frontend/
- README.md
- LICENSE

验证命令：
- 后端：`.venv/bin/python -m pytest backend/app/tests`
- 前端：`cd frontend && npm run build`
