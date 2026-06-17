# Contributing

感谢关注 AI 招聘管理系统。这个项目当前处于 MVP 阶段，优先保持本地可运行、测试可验证、范围不发散。

## 开发环境

```bash
cp .env.example .env
docker compose up --build
```

后端本地测试：

```bash
.venv/bin/python -m pytest backend/app/tests
```

前端构建：

```bash
cd frontend
npm run build
```

## 提交前检查

- 后端测试通过。
- 前端构建通过。
- 没有提交 `.env`、上传文件、数据库文件、缓存目录或真实密钥。
- 数据库模型变更需要同步 Alembic 迁移。
- 面向用户的行为变更需要更新 README 或相关文档。

## 代码约定

- 后端使用 FastAPI、SQLAlchemy、Pydantic 和 Alembic。
- 前端使用 React、TypeScript、Vite 和 Ant Design。
- AI 能力通过 `backend/app/llm/base.py` 的 Provider 抽象接入。
- 当前 MVP 默认使用 mock/规则驱动能力，不要求真实付费 LLM API。

## 范围控制

当前 MVP 聚焦招聘闭环：职位、候选人、简历导入、规则版 AI 分析、匹配评分、应聘流程、面试安排和 Docker 部署骨架。超出该范围的功能建议先开 issue 说明动机、用户场景和取舍。
