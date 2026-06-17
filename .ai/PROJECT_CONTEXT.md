# Project Context

项目名称：ai-recruitment

项目使命：为企业内部招聘团队提供 AI 辅助招聘管理 MVP，打通职位、候选人、简历导入、规则版 AI 分析、匹配评分、面试流程和人才库沉淀。

目标用户：
- 企业 HR、招聘专员和招聘经理
- 参与招聘协作的业务面试官
- 需要私有化部署招聘流程工具的中小团队

商业目标：
- 降低简历初筛和候选人管理的人工成本
- 用规则版 AI 能力先验证招聘工作流价值
- 保持 Docker Compose 本地/私有化可运行，为后续真实 LLM Provider 接入留接口

MVP 范围：
- 职位 CRUD
- 候选人 CRUD
- 简历上传、文本提取、结构化解析和异常状态记录
- 规则版候选人摘要、优势/不足、面试建议
- 人岗匹配评分和推荐结论
- 应聘流程、阶段日志、面试安排与反馈
- Docker Compose 部署骨架和基础 CI 验证

技术栈：
- 前端：React + TypeScript + Vite + Ant Design
- 后端：FastAPI + SQLAlchemy + Alembic + Pydantic
- 数据库：PostgreSQL，测试/本地可用 SQLite
- 缓存/任务队列：Redis
- 文件存储：本地存储，预留 MinIO/OSS/COS
- 部署：Docker Compose + Nginx
- AI：统一 LLM Provider 抽象，当前默认 mock/规则驱动

说明：这里记录长期稳定背景，极少修改；不要写临时状态。

现有线索：
- docker-compose.yml
- backend/
- frontend/
- docs/
- README.md
- LICENSE
- AGENTS.md
