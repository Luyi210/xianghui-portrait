# 项目文件说明

这份文档用于说明当前工作区内各个主要文件的用途，方便后续维护、交接和定位修改位置。

说明范围：
- 已覆盖当前项目目录下的业务文件、资源文件和少量环境配置文件。
- `.git/` 和 `.venv/` 属于版本管理与虚拟环境目录，内部文件数量很多，这里只说明目录作用，不逐个展开。

## 根目录页面与脚本

### `index_formal.html`
- 群体分析驾驶舱主页面。
- 负责展示学生群体概览、预警列表、群体对比、学生目录等内容。
- 通过 `axios` 请求同域接口 `/api/formal`。
- 是整个项目的主入口页面之一。

### `student_formal.html`
- 单个学生的个人画像页面。
- 根据 URL 参数中的 `id` 加载指定学生画像、维度雷达图、风险标签、成长轨迹、建议路径等内容。
- 也包含“相辉小助手”问答入口。

### `benchmark_overview.html`
- 高校项目对标总览页。
- 展示国内外高校项目卡片、分类筛选、统计图和样本表。
- 数据来源于 `assets/js/benchmark_data.js`。

### `benchmark_compare.html`
- 多校比较页。
- 支持通过 `?ids=...` 参数选择多个高校项目进行并排比较。
- 页面内有表格、条形图、雷达图，用于比较导师制、科研训练、国际交流、资助、选拔机制、学科覆盖等维度。

### `benchmark_detail.html`
- 单个高校项目详情页。
- 根据 URL 参数 `id` 加载某个项目的详细字段信息与雷达图画像。
- 适合从对标总览或多校比较页继续下钻。

### `resources_fudan.html`
- 复旦校内资源与制度导航页。
- 偏“资源入口”与“制度说明”，帮助回答“识别画像之后可以接什么资源”。
- 目前是静态整理页面，后续适合改成 JSON 或后端配置驱动。

### `policy_overview.html`
- 管理者视角的政策概要页。
- 总结顶尖高校常见培养机制，以及这些机制对相辉学堂的启发。
- 更偏管理端、制度端和试点策略视角。

### `data_methodology.html`
- 数据来源与方法说明页。
- 解释对标数据从哪里来、比较边界是什么、当前页面中的分值代表什么、不代表什么。
- 主要用于增强系统可解释性和可信度。

### `backend_formal.py`
- 项目的 Python 后端主程序，使用 FastAPI。
- 负责读取 `formal_student_data.csv`，并向前端提供画像、预警、比较、预测、AI 问答等接口。
- 主要接口包括：
  - `/api/formal/overview`
  - `/api/formal/students`
  - `/api/formal/student/{student_id}`
  - `/api/formal/warnings`
  - `/api/formal/group_compare`
  - `/api/formal/ai_chat`
  - `/api/formal/mentors`
  - `/api/formal/students/{student_id}/growth`
  - `/api/formal/prediction`
  - `/api/formal/compare`
  - `/api/formal/churn_risk`
  - `/api/formal/classes`
- 启动端口配置为 `8002`。
- 代码里还包含 DeepSeek API 调用逻辑，用于“相辉小助手”。

### `formal_data_generate.py`
- 模拟学生画像数据生成脚本。
- 负责生成学生基础信息、八大维度、类型分类、风险标签、建议路径等，并输出到 `formal_student_data.csv`。
- 适合在需要重新造数、调节样本分布或调整画像逻辑时修改。

### `formal_student_data.csv`
- 当前前后端共同使用的核心数据文件。
- 存放模拟学生样本，是 `backend_formal.py` 的直接数据来源。
- 包含学生基础属性、画像维度、风险、建议、百分位等字段。

### `backend_formal.pid`
- 后端进程 PID 文件。
- 一般用于记录当前运行中的后端进程号，方便脚本或手动停止服务。
- 当前文件内容看起来很短，符合 PID 文件特征。

### `backend_formal_stdout.log`
- 后端标准输出日志文件。
- 当前是空文件，说明最近没有写入日志，或者服务启动方式未把输出重定向到这里。

### `1.jpeg`
- 页面背景图片资源。
- 在多个静态页面中被用作大面积背景图，强化整体视觉风格。

## 资源与样式目录

### `assets/js/benchmark_data.js`
- 高校对标数据源。
- 以 JavaScript 对象数组形式维护高校项目样本。
- 被 `benchmark_overview.html`、`benchmark_compare.html`、`benchmark_detail.html` 直接读取。

### `assets/css/benchmark.css`
- 对标模块公共样式文件。
- 主要服务于高校对标相关页面的版式、卡片、表格、图表容器和通用视觉组件。

### `assets/brand/fudan_brand.css`
- 全项目的品牌风格样式文件。
- 负责统一复旦专题风格，例如 banner、品牌导航、色彩、标题体系等。
- 群体画像页、个人画像页、对标页和说明页都会引用它。

### `assets/brand/fudan-academic-bg.svg`
- SVG 背景图资源。
- 从命名看更偏“学术主题”背景，用于品牌视觉或装饰层。

### `assets/brand/fudan-guanghua-bg.svg`
- SVG 背景图资源。
- 从命名看更偏“光华楼/校内建筑主题”背景，用于品牌视觉或装饰层。

## 编辑器与环境配置

### `.vscode/settings.json`
- VS Code 工作区设置文件。
- 当前主要指定：
  - Python 默认解释器使用工作区内的 `.venv/bin/python`
  - 打开终端时自动激活虚拟环境

### `.DS_Store`
- macOS 自动生成的目录元数据文件。
- 与业务无关，可以忽略。

## 目录级说明

### `.git/`
- Git 版本管理目录。
- 存放提交记录、索引、对象、分支引用等内容。
- 属于仓库内部实现，不建议手动修改内部文件。

### `.venv/`
- Python 本地虚拟环境目录。
- 存放解释器、`pip`、依赖包等。
- 用于保证项目运行环境隔离。

## 当前被页面引用、但目录中未找到的文件

以下文件在页面链接里被引用过，但目前不在当前目录中：

### `phase1_plan.md`
- 在 `resources_fudan.html`、`policy_overview.html` 中被链接为阶段文档。
- 当前缺失。

### `phase2_progress.md`
- 在 `student_formal.html`、`data_methodology.html` 中被链接为阶段文档。
- 当前缺失。

### `phase3_progress.md`
- 在 `index_formal.html`、`benchmark_overview.html`、`benchmark_compare.html` 中被链接为阶段文档。
- 当前缺失。

### `docs/benchmark_schema.csv`
- 在 `data_methodology.html` 中被说明为本地结构化对标数据文件。
- 当前缺失。

## 一句话理解这个项目

这是一个以“相辉学堂学生画像”为核心、同时补充“高校培养机制对标”和“制度资源导航”的本地原型项目：前端以静态 HTML 为主，后端用 FastAPI 提供模拟数据接口，整体目标是把学生识别、风险提示、培养建议和项目对标放在一个可展示的系统里。
