# Project Copilot 与 Codex

Project Copilot 为 Codex 安装轻量项目记忆。

Codex 负责开发。

Project Copilot 负责让 Codex 记住项目为什么这样演进。

一句话：

Git 记录代码历史。

Project Copilot 记录为什么。

## 为什么需要 Project Copilot

随着项目持续开发，人们经常忘记：

- 为什么开始这个项目
- 为什么这样设计
- 为什么放弃某些需求
- 项目如何演化到今天

Git 能告诉你：

改了什么。

Project Copilot 能告诉你：

为什么改。

目标是让项目在一年后仍然能够回答：

- 为什么存在
- 为什么这样设计
- 为什么放弃某些功能
- 如何一步步发展到今天

## 第一次使用

接管已有项目：

```bash
project-copilot adopt
```

或者初始化新项目：

```bash
project-copilot init
```

系统将生成：

- `.ai/`
- `AGENTS.md`
- 项目记忆规则

## 推荐工作流

### 每天开始

在项目目录打开：

```bash
codex
```

推荐输入：

```text
继续开发这个项目
```

### 开发过程中

正常与 Codex 对话即可。

Project Copilot 会通过项目记忆帮助 Codex 理解：

- 项目目标
- MVP 范围
- 历史 ADR
- 项目状态

### 每天结束

推荐输入：

```text
今天结束工作
```

帮助确认：

- 哪些 ADR 候选值得保留
- 哪些里程碑三个月后仍重要
- 哪些风险或知识需要进入长期记忆

普通代码修改、测试增加和小型 Bug 修复交给 Git，不写入 `.ai`。

### 每周复盘

推荐输入：

```text
复盘项目
```

查看：

- 本周完成
- 关键决策
- 风险变化
- 路线图推进情况

### 项目变复杂时

推荐输入：

```text
项目偏航检查
```

确认：

- 是否偏离目标用户
- 是否超出 MVP
- 是否与历史决策冲突

## 项目记忆结构

`PROJECT_CHARTER.md`

记录项目使命、目标用户、MVP 范围、非目标和长期边界。

`PROJECT_CONTEXT.md`

兼容旧版项目定义。新项目优先使用 `PROJECT_CHARTER.md`。

`STATUS.md`

记录当前状态。

`ROADMAP.md`

记录项目计划。

`MEMORY.md`

记录稳定事实、重要事件、关键里程碑和不应遗忘的信息。

`HYPOTHESES.md`

兼容旧版假设层。新会话优先使用 `sessions/current.md` 暂存候选事件。

`DECISIONS.md`

兼容旧版决策索引。新决策优先写入 `adr/`。

`adr/`

记录架构、产品范围和长期取舍，重点回答为什么这样做。

`WORKLOG.md`

兼容旧版工作日志。Session Memory 模式下不再记录普通每日流水。

`sessions/current.md`

记录当前会话候选事件，结束工作时统一确认。

`sessions/archive/`

记录确认后的重大会话摘要。

`KNOWLEDGE.md`

记录学习和经验沉淀。

## 最佳实践

建议：

- 开始工作时读取项目记忆
- 开发过程中只维护候选事件
- 结束工作时统一确认并写入
- 每周进行一次项目复盘
- 重要决策进入 ADR
- MVP 变更前先确认影响
- 长期记忆写入后自动刷新验证报告，候选事件阶段不刷新

## 项目秘书理念

Project Copilot 不负责写代码。

Project Copilot 负责：

- 记住项目背景
- 记住关键决策原因
- 记住 MVP 边界
- 帮助 Codex 避免忘记上下文

Codex 负责把事情做出来。

Project Copilot 负责记住为什么这样做。
