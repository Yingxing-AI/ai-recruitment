# Project Copilot 与 Codex

Project Copilot 为 Codex 安装持久项目记忆层。

Codex 负责开发。

Project Copilot 负责记录项目历史、决策和演进过程。

一句话：

Git 记录代码历史。

Project Copilot 记录项目历史。

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
- 历史决策
- 项目状态

### 每天结束

推荐输入：

```text
今天结束工作
```

帮助更新：

- 项目状态
- 工作日志
- 长期记忆

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

`PROJECT_CONTEXT.md`

记录项目使命和目标用户。

`STATUS.md`

记录当前状态。

`ROADMAP.md`

记录项目计划。

`MEMORY.md`

记录长期事实和里程碑。

`DECISIONS.md`

记录重要决策及原因。

`WORKLOG.md`

记录每日工作。

`KNOWLEDGE.md`

记录学习和经验沉淀。

## 最佳实践

建议：

- 每天结束时更新项目状态
- 每周进行一次项目复盘
- 重要决策及时记录
- MVP 变更前先确认影响

## 项目秘书理念

Project Copilot 不负责写代码。

Project Copilot 负责：

- 记录
- 提醒
- 归档
- 复盘
- 守护项目方向

Codex 负责把事情做出来。

Project Copilot 负责记住为什么这样做。
