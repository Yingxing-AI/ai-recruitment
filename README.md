# AI 招聘管理系统

面向企业内部招聘团队的 AI 招聘管理 MVP，当前进入 Phase 4：V1 产品化。

当前产品定位是企业 HR 的招聘工作台，而不是孤立功能集合。默认用户路径为：

职位
-> 候选人
-> 上传简历
-> AI 解析与总结
-> 岗位匹配
-> 面试安排
-> 面试反馈
-> Offer
-> 录用
-> 人才库沉淀

项目已经覆盖：

- 职位管理
- 候选人管理
- 简历上传与解析
- 规则版 AI 简历总结
- 岗位匹配评分
- 面试题生成
- 招聘流程流转
- 管理仪表盘与演示数据

## 导航结构

- 仪表盘
- 招聘中心
  - 职位
  - 候选人
  - 招聘流程
- 面试中心
  - 面试安排
  - 面试反馈
- 人才库
- 系统设置

说明：
- `简历导入` 和 `AI 招聘` 不再作为一级菜单。
- 简历上传、解析、候选人总结和面试问题已整合进候选人详情页。
- 候选人匹配评分、推荐结论、匹配/缺失/风险点已整合进职位详情页。

## 功能清单

- 职位 CRUD
- 候选人 CRUD
- 简历上传、文本提取、结构化解析
- 规则版候选人摘要、优势/不足、面试建议
- 人岗匹配评分和推荐结论
- 应聘流程、阶段日志、面试安排与反馈
- 招聘管理仪表盘
- Docker Compose 私有化部署

## 技术栈

- 前端：React + TypeScript + Vite + Ant Design
- 后端：FastAPI + SQLAlchemy + Alembic + Pydantic
- 数据库：PostgreSQL，本地和测试可用 SQLite
- 缓存/队列：Redis
- 文件存储：本地存储，预留 MinIO/OSS/COS
- 部署：Docker Compose + Nginx
- AI：统一 LLM Provider 抽象，当前默认规则版

## 快速启动

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec backend python -m app.scripts.seed_data
```

访问地址：

- Docker 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- MinIO 控制台：http://localhost:9001

## 开发验证

前端构建：

```bash
cd frontend
npm run build
```

前端本地开发：

```bash
cd frontend
npm run dev
```

本地 Vite 开发服务器默认使用 `http://localhost:3001`，避免与 Docker 前端 `3000` 端口冲突。

后端代码检查：

```bash
make lint-backend
```

后端测试：

```bash
make test
```

实例验证链路：

```bash
cd backend
./.venv/bin/python -m pytest -q app/tests/test_instance_verification_chain.py
```

## API 文档

核心业务接口：

- `GET /api/v1/jobs`
- `GET /api/v1/candidates`
- `GET /api/v1/resumes`
- `GET /api/v1/applications`
- `GET /api/v1/interviews`
- `GET /api/v1/dashboard/summary`

规则版 AI 接口：

- `POST /api/v1/ai/resumes/{resume_id}/parse`
- `POST /api/v1/ai/resumes/{resume_id}/summary`
- `POST /api/v1/ai/jobs/{job_id}/candidates/{candidate_id}/match`
- `POST /api/v1/ai/jobs/{job_id}/candidates/{candidate_id}/interview-questions`
- `GET /api/v1/ai/analyses`
- `GET /api/v1/ai/matches`

## 当前 AI 说明

当前 AI 能力全部由规则驱动实现，不接入付费外部 API。

简历上传后，后端会提取文本并写入：

- `resumes.raw_text`
- `resumes.parsed_json`

规则版 AI 输出包括：

- 候选人摘要
- 优势与不足
- 岗位匹配评分
- 面试问题生成

## 演示数据

种子脚本会生成：

- 示例职位
- 示例候选人
- 示例简历
- 示例 AI 分析结果
- 示例岗位匹配结果
- 示例面试记录
- 10 条额外的虚拟实例

重新生成演示数据：

```bash
docker compose exec backend python -m app.scripts.seed_data
```

## 部署说明

详细部署步骤见 [docs/deployment.md](docs/deployment.md)。

## 验收用例

详细验收测试见 [docs/test-cases.md](docs/test-cases.md)。

## 后续计划

当前只预留真实 LLM Provider 接口，后续可在不改业务流程的前提下接入真实模型。

相关说明见 [TODO.md](TODO.md) 和 [CHANGELOG.md](CHANGELOG.md)。
