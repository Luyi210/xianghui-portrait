# 新增内容接入指南

这份文档是给你以后继续扩这个项目时用的。

目标不是讲抽象架构，而是告诉你：

- 如果想加一个新页面，怎么接
- 如果想加一个新接口，怎么接
- 如果想加一份新数据，怎么接
- 如果想加一段新的 AI 功能，怎么接

---

## 一、先记住这个项目的接入原则

你现在这个项目的结构很清楚：

- 页面：根目录里的 `.html`
- 后端：`backend_formal.py`
- 静态资源：`assets/`
- 说明文档：`docs/`
- 数据：目前主要是 `formal_student_data.csv`

所以以后你要新增东西，先判断它属于哪一类：

1. 新页面
2. 新接口
3. 新数据
4. 新 AI 功能

只要分类清楚，接入就不会乱。

---

## 二、新增一个页面怎么接

### 适用场景

比如你以后想加：

- 导师画像页
- 年级专题页
- 某类学生分析页
- 某个展示专题页

### 操作步骤

#### 1. 新建一个 HTML 文件

例如：

```text
mentor_overview.html
```

#### 2. 页面里引用已有资源

通常至少引用：

```html
<link rel="stylesheet" href="assets/brand/fudan_brand.css" />
```

如果是对标类页面，还可以加：

```html
<link rel="stylesheet" href="assets/css/benchmark.css" />
```

如果要画图：

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
```

如果要调后端接口：

```html
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
```

#### 3. 如果这个页面要上线访问

记得在 `backend_formal.py` 里的 `HTML_PAGES` 集合里加上：

```python
'mentor_overview.html',
```

否则后端不会把它作为公开页面提供出来。

#### 4. 给页面加入口

在已有页面里加链接，比如：

```html
<a class="brand-link" href="mentor_overview.html">导师画像</a>
```

---

## 三、新增一个后端接口怎么接

### 适用场景

比如你想加：

- 某类学生的聚合统计
- 某个年级单独分析
- 新的风险预测
- 新的 AI 报告接口

### 操作步骤

#### 1. 在 `backend_formal.py` 里新增路由

例子：

```python
@app.get('/api/formal/mentor_overview')
def mentor_overview():
    df = load_df()
    if df.empty:
        return {'status': 'error', 'message': '无数据'}
    return {'status': 'success', 'total': int(len(df))}
```

#### 2. 前端页面请求它

例如：

```javascript
const res = await axios.get('/api/formal/mentor_overview');
```

#### 3. 前端拿到数据后渲染

你可以：

- 渲染表格
- 渲染卡片
- 渲染图表

---

## 四、新增一份数据怎么接

### 适用场景

比如你以后想加：

- 新的学生样本数据
- 新的学校对标数据
- 新的制度资源清单

### 方案 A：前端直接使用

适合小规模静态数据，比如：

- 一个 JS 数组
- 一个说明型 CSV

放置建议：

- `assets/js/`
- `docs/`

### 方案 B：后端读取后再给前端

适合：

- 数据量更大
- 需要筛选 / 计算 / 聚合

做法：

1. 把数据文件放在项目里
2. 在 `backend_formal.py` 里读取
3. 新增一个接口返回处理结果

---

## 五、新增 AI 功能怎么接

### 适用场景

比如你想加：

- 自动生成学生报告
- 自动生成群体总结
- 导师问答助手
- 管理者分析助手

### 当前建议做法

优先在 `backend_formal.py` 里扩展。

原因：

- 现在你项目不大
- AI 配置已经集中在后端
- 页面只需要请求 `/api/formal/...`

### 一个常见方式

#### 1. 新增一个 AI 接口

例如：

```python
@app.post('/api/formal/mentor_ai_chat')
async def mentor_ai_chat(request: Request):
    body = await request.json()
    question = body.get('question', '').strip()
    return {'status': 'success', 'answer': f'收到问题：{question}'}
```

#### 2. 前端页面调用

```javascript
const res = await axios.post('/api/formal/mentor_ai_chat', {
  question: q
});
```

---

## 六、推荐的扩展顺序

如果你以后继续做这个项目，我建议优先级按这个顺序：

### 第一步：加新页面

原因：

- 风险最低
- 最容易出成果
- 最适合展示型项目

### 第二步：加新接口

原因：

- 能增强页面内容
- 能让页面变成“动态分析”而不只是静态展示

### 第三步：加新 AI 功能

原因：

- 能提升交互感
- 但也更容易引入外部接口不稳定的问题

### 第四步：再考虑重构目录

例如把页面挪进 `pages/`、把后端拆模块等。

当前阶段不建议过早重构。

---

## 七、你以后新增功能时最实用的问题

每次你想加新内容，先问自己：

### 1. 这是“页面”还是“数据”？

- 页面：新建 `.html`
- 数据：新建接口或数据文件

### 2. 这个内容是静态展示还是需要计算？

- 静态展示：前端写死或读小文件
- 需要计算：放后端接口

### 3. 这个功能是不是以后还会继续扩展？

- 如果只是展示一次，就简单做
- 如果以后会反复扩展，就早点设计成接口

---

## 八、最短记忆版

以后你要加新东西，可以按这个判断：

```text
新页面 -> 新建 html -> 加进 backend_formal.py 的 HTML_PAGES
新数据 -> 看是前端直接读还是后端接口返回
新功能 -> 优先在 backend_formal.py 里加接口
新 AI -> 在 backend_formal.py 里扩展 AI 路由
```
