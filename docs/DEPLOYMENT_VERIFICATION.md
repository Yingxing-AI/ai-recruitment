# Deployment Verification

这个清单用于发布前和部署后做最小验证。

## 发布前

1. 后端测试通过。
2. 前端构建通过。
3. `README.md`、`CHANGELOG.md`、`docs/RELEASE.md` 已同步。
4. 生产配置已替换默认密钥和数据库配置。

## 部署后

1. 打开健康检查接口，确认服务可用。
2. 打开职位、候选人和 AI 招聘页面，确认核心路由可访问。
3. 新建一个职位和候选人，确认能进入详情页。
4. 通过自然语言工作流解析一条指令，确认前端页面能展示结果。
5. 检查留痕日志是否写入。
6. 运行实例验证链路，确认简历上传、解析、总结、匹配、面试题和阶段流转可以串起来。

## Smoke Tests

可直接运行后端烟雾测试：

```bash
cd backend
python -m pytest app/tests/test_deployment_smoke.py
```

建议与常规测试一起执行：

```bash
cd backend
python -m pytest app/tests
```

实例验证链路：

```bash
cd backend
python -m pytest app/tests/test_instance_verification_chain.py
```
