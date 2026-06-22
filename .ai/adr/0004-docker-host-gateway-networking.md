# ADR 0004: Docker Compose 依赖服务走宿主机网关

日期：2026-06-22

状态：Accepted

背景：

在当前运行环境中，`backend` 和 `worker` 容器可以解析 `postgres`、`redis` 和 `minio` 的 Compose 服务名，但容器间 TCP 访问会超时，导致后端启动阶段无法连接数据库，规则版招聘 MVP 无法打开完整产品界面。

决策：

保留 PostgreSQL、Redis 和 MinIO 的对外端口映射，并让 `backend` / `worker` 在 Docker Compose 中通过 `host.docker.internal:host-gateway` 访问这些依赖服务；同时让 `frontend` 的 Nginx 代理也通过宿主机网关访问 `backend:8000` 的宿主端口，并在应用启动阶段增加数据库重试，降低冷启动时序失败概率。

原因：

该方案能绕过当前环境的容器间桥接网络限制，又不改变招聘 MVP 的业务边界、端口约定和前后端访问入口。

取舍：

Compose 配置比纯服务名访问更显式，也更依赖宿主机端口映射；但换来当前环境下稳定可用的本地演示与验证链路。

影响：

后续在 Docker Compose 环境中，`backend`、`worker` 和 `frontend` 代理链路默认通过宿主机网关访问依赖服务；如运行环境恢复正常容器互联，可再评估是否回退为服务名直连。
