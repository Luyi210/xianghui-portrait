# 目录结构建议

这份文档用于说明当前项目整理后的目录结构，以及哪些内容是核心运行文件，哪些只是开发辅助文件。

## 当前建议结构

```text
人物画像可视化/
├── assets/                     # 前端静态资源
│   ├── brand/                  # 品牌样式
│   ├── css/                    # 页面公共样式
│   └── js/                     # 前端数据与脚本
├── docs/                       # 文档、阶段记录、部署说明
├── .vscode/                    # 本地编辑器配置
├── backend_formal.py           # FastAPI 后端主程序
├── formal_student_data.csv     # 当前线上使用的数据文件
├── formal_data_generate.py     # 数据生成脚本
├── index_formal.html           # 群体页
├── student_formal.html         # 个人画像页
├── benchmark_overview.html     # 对标总览
├── benchmark_compare.html      # 多校比较
├── benchmark_detail.html       # 对标详情
├── resources_fudan.html        # 资源导航
├── policy_overview.html        # 管理者政策页
├── data_methodology.html       # 方法说明页
├── 1.jpeg                      # 公共背景图
├── requirements.txt            # Python 依赖
├── render.yaml                 # Render 部署配置
└── .gitignore                  # Git 忽略规则
```

## 核心运行文件

这些文件会直接影响网站运行，不建议随意移动或删除：

- `backend_formal.py`
- `formal_student_data.csv`
- `requirements.txt`
- `render.yaml`
- `1.jpeg`
- 所有主页面 `.html`
- `assets/` 目录

## 可保留的开发辅助文件

这些文件不会直接影响网站页面运行，但保留它们对维护有帮助：

- `formal_data_generate.py`
- `.vscode/settings.json`
- `docs/` 目录下的所有说明文档

## 以后如果还想继续整理

如果你后面想让项目更像正式仓库，可以再考虑：

### 方案 A：只保持当前结构

优点：
- 简单
- 好找文件
- 改动风险最低

### 方案 B：把 HTML 页面收进 `pages/`

例如：

```text
pages/index_formal.html
pages/student_formal.html
...
```

但这会牵涉到：
- 后端静态路由
- 页面内部跳转路径
- Render 线上访问路径

所以当前阶段不建议动。

## 当前结论

你现在这个项目结构已经够干净了，适合继续开发和展示。
后续重点不在“继续大搬家”，而在于：

- 正常维护代码
- 正常 `git push`
- 正常让 Render 自动部署
