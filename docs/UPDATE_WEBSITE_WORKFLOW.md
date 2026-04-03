# 网站更新操作模板

这份文档是给你以后自己更新网站时直接照着操作用的。

当前项目部署关系是：
- 本地电脑：你写代码、改页面、改后端
- GitHub：存放代码
- Render：运行网站

也就是说，你以后更新网站的核心链路永远是：

```text
本地改代码 -> 提交到 GitHub -> Render 自动重新部署 -> 网站变成新版本
```

## 一、最常用的更新模板

以后你每次改完代码，直接在终端里运行：

```bash
cd "/Users/g/Desktop/人物画像可视化/人物画像可视化"
git status
git add -A
git commit -m "写这次修改的内容"
git push
```

## 二、标准更新流程

### 1. 先改本地代码

你平时改的常见文件包括：

- `index_formal.html`
- `student_formal.html`
- `benchmark_compare.html`
- `benchmark_detail.html`
- `benchmark_overview.html`
- `policy_overview.html`
- `resources_fudan.html`
- `data_methodology.html`
- `backend_formal.py`

### 2. 改完后先简单检查

如果你改的是 Python 后端，建议先运行：

```bash
python3 -m py_compile backend_formal.py
```

### 3. 查看当前改动

```bash
git status
```

### 4. 把改动加入提交

如果你想把这次所有改动都一起提交：

```bash
git add -A
```

### 5. 写提交说明

```bash
git commit -m "update benchmark compare page"
```

### 6. 推送到 GitHub

```bash
git push
```

### 7. Render 自动重新部署

你 push 完之后：

- Render 会自动检测到 GitHub 上 `main` 分支更新
- 然后开始重新部署
- 部署完成后，网站就是新版本

## 三、如果只是改了环境变量

如果你改的不是代码，而是 Render 里的环境变量，比如：

- `AI_PROVIDER`
- `AI_API_KEY`
- `AI_BASE_URL`
- `AI_MODEL`

这种情况：

- 不需要 `git push`
- 直接去 Render 的 `Environment`
- 修改后点：

```text
Save, rebuild, and deploy
```

## 四、常见问题

### 1. Render 没自动更新怎么办？

先确认你已经成功：

```bash
git push
```

然后去 Render 看：

- 有没有新的部署记录
- 状态是不是 `Deploying`

### 2. 网站第一次打开慢正常吗？

正常。

因为你现在用的是 Render 免费服务，空闲后会休眠。
第一次访问会出现冷启动，所以会慢一点。

### 3. AI 助手变成“离线说明”怎么办？

优先检查 Render 环境变量：

```text
AI_PROVIDER
AI_API_KEY
AI_BASE_URL
AI_MODEL
```

改完之后记得点：

```text
Save, rebuild, and deploy
```

## 五、一句话记忆版

以后你只要记住这句话就行：

```text
本地改完 -> git add -> git commit -> git push -> 等 Render 变成 Live
```
