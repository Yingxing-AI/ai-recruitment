# AI 招聘管理系统

企业内部使用的 AI 招聘管理系统 MVP，支持职位管理、简历导入、候选人管理、AI 简历分析、匹配评分、面试流程管理和人才库沉淀。

## 技术栈

- 前端：React + TypeScript + Vite + Ant Design
- 后端：FastAPI + SQLAlchemy + Alembic + Pydantic
- 数据库：PostgreSQL
- 缓存/任务队列：Redis
- 文件存储：本地存储，预留 MinIO/OSS/COS
- 部署：Docker Compose + Nginx
- AI：统一 LLM Provider 抽象，预留通义千问、DeepSeek、智谱等国内大模型接入

## 项目结构

```text
.
├── backend/              # FastAPI 后端
├── frontend/             # React 前端
├── deploy/               # Nginx 与部署配置
├── docker-compose.yml
├── .env.example
└── README.md
```

## 本地启动

开发环境：

```bash
cp .env.example .env
docker compose up --build
```

中国大陆网络建议先使用 `.env.example` 中的镜像代理配置：

```bash
cp .env.example .env
docker compose pull postgres redis minio
docker compose up --build -d
```

如果默认的 `docker.1ms.run` 不可用，编辑 `.env` 中的镜像配置，例如：

```bash
DOCKER_IMAGE_PROXY=docker.1panel.live
PYTHON_BASE_IMAGE=docker.1panel.live/python:3.11-slim
NODE_BASE_IMAGE=docker.1panel.live/node:20-alpine
NGINX_BASE_IMAGE=docker.1panel.live/nginx:1.27-alpine
```

也可以替换成企业内网镜像仓库地址。

服务地址：

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- MinIO 控制台：http://localhost:9001

## 开发验证

后端测试：

```bash
.venv/bin/python -m pytest backend/app/tests
```

前端构建：

```bash
cd frontend
npm run build
```

CI 会在 GitHub Actions 中分别执行：

- `cd backend && python -m pip install -e ".[dev]" && python -m pytest app/tests`
- `cd frontend && npm ci && npm run build`

## MVP 功能范围

- 用户与角色基础模型
- 职位 CRUD
- 候选人 CRUD
- 简历上传记录与文本字段
- AI 简历分析结果表
- 人岗匹配评分表
- 应聘流程与阶段日志
- 面试安排与反馈
- Docker 化部署骨架

## AI 接入说明

后端通过 `backend/app/llm/base.py` 定义统一接口。后续接入具体模型时，只需要在 `backend/app/llm/providers/` 下实现对应 Provider，并在业务服务中按配置选择 Provider。

## 数据库

当前项目已定义 SQLAlchemy ORM 模型。生产使用建议通过 Alembic 管理迁移：

```bash
cd backend
alembic upgrade head
```

MVP 开发阶段后端启动时会自动创建表，便于快速验证。

如果修改了 ORM 模型，生成新迁移：

```bash
cd backend
alembic revision --autogenerate -m "describe schema change"
```

## 测试数据

Docker 环境启动后，可执行幂等种子脚本生成职位、候选人、招聘流程记录，并上传一份样例简历到 MinIO：

```bash
docker compose exec backend python -m app.scripts.seed_data
```

简历文件默认写入 `MINIO_BUCKET=resumes`，后端会同步记录到 `files` 和 `resumes` 表。

种子脚本也会生成一组规则版 AI 数据：

- 简历结构化解析结果：姓名、电话、邮箱、教育经历、工作经历、技能、项目经历
- 候选人摘要、优势、不足和建议面试等级
- 职位匹配评分、匹配理由、风险点和推荐结论
- 技术、项目、行为三类面试问题

## AI 招聘能力

当前仅实现规则版能力，不接入真实付费 AI API。前端入口：

- `http://localhost:3000/ai-recruitment`

如果本机旧 Docker 容器无法停止导致 3000 仍运行旧前端，可临时使用修复版前端端口：

- `http://localhost:3001/ai-recruitment`

后端 API：

```text
POST /api/v1/ai/resumes/{resume_id}/parse
POST /api/v1/ai/resumes/{resume_id}/summary
POST /api/v1/ai/jobs/{job_id}/candidates/{candidate_id}/match
POST /api/v1/ai/jobs/{job_id}/candidates/{candidate_id}/interview-questions
GET  /api/v1/ai/analyses
GET  /api/v1/ai/matches
```

上传 PDF / DOCX 简历时，后端会自动提取文本并写入 `resumes.raw_text` 和 `resumes.parsed_json`。后续接入真实模型时，可以在 `backend/app/llm/providers/` 下新增 Provider，并保持当前 AI API 的业务输出结构不变。
