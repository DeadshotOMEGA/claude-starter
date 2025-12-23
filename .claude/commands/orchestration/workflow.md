---
description: Execute complete feature development lifecycle with agent delegation
argument-hint: [feature description or ID]
allowed-tools: Read, Write, Edit, Bash, Task, AskUserQuestion
model: opus
---

$ARGUMENTS

## Feature Development Lifecycle

Execute the complete feature development lifecycle using strategic agent delegation:

**Requirements & Investigation → Planning → Implementation → Validation**

### Phase Guidelines

**Requirements & Investigation**
- Main agent performs lightweight initial investigation to understand the feature scope
- Main agent asks clarifying questions to understand user intent and constraints
- As requirements emerge, spawn investigation agents using the Task tool:
  - Task(subagent_type="Explore", prompt="investigate authentication patterns for feature X")
  - Task(subagent_type="Explore", prompt="document existing API integration patterns")
  - Launch multiple Task calls in a single message for parallel execution
  - Each focusing on: existing patterns, related code, dependencies, technical constraints
- All investigation documents MUST use the template from `pdocs template investigation-topic`
- Output:
  - Requirements document incorporating user clarifications and high-level findings
  - Collection of investigation documents covering different aspects of the feature
- User signs off on requirements and investigation before proceeding to planning

**Planning**
- Spawn planning agent: Task(subagent_type="implementation-planner", prompt="create implementation plan for feature X")
- Agent has access to ALL requirements and investigation documents
- Agent creates detailed implementation plan citing specific investigation findings
- Plan breaks down work into discrete, delegatable tasks

**Implementation**
- Spawn implementation agents in parallel for independent tasks (multiple Task calls in single message):
  - Task(subagent_type="programmer", prompt="<relevant docs> Implement phase 3")
  - Task(subagent_type="junior-engineer", prompt="<relevant docs> Implement phase 4")
- Each agent receives relevant investigation documents and plan sections
- Implement shared dependencies first, then launch parallel agents

**Validation**
- Run tests, linting, type checks after implementation
- Task(subagent_type="architecture-advisor", prompt="Review implementation for <feature>")
- Address any issues found
