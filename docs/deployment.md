# Deployment

## 目标

本项目面向本地开发和私有化部署，推荐使用 Docker Compose 一键启动。

## 标准端口

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

## 环境准备

1. 安装 Docker 和 Docker Compose。
2. 复制环境变量文件：

```bash
cp .env.example .env
```

3. 如需调整镜像代理、数据库密码或对象存储账号，修改 `.env`。

## 一键启动

```bash
docker compose up --build -d
```

启动后，首次访问前建议导入演示数据：

```bash
docker compose exec backend python -m app.scripts.seed_data
```

## 常用检查

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

## 数据与文件

- PostgreSQL 保存业务数据。
- Redis 提供队列与缓存。
- MinIO 用于简历文件存储。
- 上传文件默认写入容器内 `/app/uploads`，并同步到对象存储。

## 常见问题

- 如果前端无法打开，先确认 `3000` 端口未被其他服务占用。
- 如果后端连不上数据库，检查 `.env` 中的数据库连接串和容器健康状态。
- 如果需要重建演示数据，可重复执行 seed 命令，脚本保持幂等。
