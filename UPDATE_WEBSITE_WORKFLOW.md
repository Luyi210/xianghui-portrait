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

---

## 一、最常用的更新模板

以后你每次改完代码，直接在终端里运行：

```bash
cd "/Users/g/Desktop/人物画像可视化/人物画像可视化"
git status
git add -A
git commit -m "写这次修改的内容"
git push
```

这 4 步的意思：

- `git status`
  - 看看哪些文件改了
- `git add -A`
  - 把这次所有改动加入提交
- `git commit -m "..."`  
  - 给这次修改写一个说明
- `git push`
  - 把最新代码上传到 GitHub

然后 Render 会自动发现 GitHub 更新，并重新部署。

---

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

---

### 2. 改完后先简单检查

如果你改的是 Python 后端，建议先运行：

```bash
python3 -m py_compile backend_formal.py
```

如果没有报错，说明至少语法没问题。

如果你改的是 HTML 页面，建议本地先打开看一眼。

---

### 3. 查看当前改动

```bash
git status
```

如果你看到一堆文件名，说明这些文件已经改了但还没提交。

---

### 4. 把改动加入提交

如果你想把这次所有改动都一起提交：

```bash
git add -A
```

如果你只想提交某几个文件，也可以写具体文件名：

```bash
git add benchmark_compare.html backend_formal.py
```

---

### 5. 写提交说明

```bash
git commit -m "update benchmark compare page"
```

你以后可以参考这些写法：

```bash
git commit -m "update homepage layout"
git commit -m "fix ai assistant config"
git commit -m "refine student portrait page"
git commit -m "add new benchmark data"
git commit -m "fix deployment settings"
```

---

### 6. 推送到 GitHub

```bash
git push
```

如果 push 成功，说明 GitHub 已经收到最新代码。

---

### 7. Render 自动重新部署

你 push 完之后：

- Render 会自动检测到 GitHub 上 `main` 分支更新
- 然后开始重新部署
- 部署完成后，网站就是新版本

你可以去 Render 看状态：

- `Deploying`：正在部署
- `Live`：部署完成，网站在线
- `Failed`：部署失败，需要看日志

---

## 三、最短版本

如果你已经很熟练了，以后最常用的其实就这几句：

```bash
cd "/Users/g/Desktop/人物画像可视化/人物画像可视化"
git add -A
git commit -m "update something"
git push
```

---

## 四、如果只是改了环境变量

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

这样 Render 会重新部署。

---

## 五、怎么看网站是不是已经更新成功

### 方法 1：看 Render 状态

Render 服务页面如果显示：

```text
Live
```

一般说明新版本已经部署完成。

---

### 方法 2：直接打开网站

你的网站地址现在是：

```text
https://xianghui-portrait.onrender.com
```

常用页面：

- 首页：  
  `https://xianghui-portrait.onrender.com/`

- 群体页：  
  `https://xianghui-portrait.onrender.com/index_formal.html`

- 个人画像：  
  `https://xianghui-portrait.onrender.com/student_formal.html?id=20240001`

- 多校比较：  
  `https://xianghui-portrait.onrender.com/benchmark_compare.html`

---

## 六、常见问题

### 1. `git push` 失败怎么办？

先看是不是在正确目录：

```bash
pwd
```

应该是：

```bash
/Users/g/Desktop/人物画像可视化/人物画像可视化
```

再看 Git 状态：

```bash
git status
```

---

### 2. Render 没自动更新怎么办？

先确认你已经成功：

```bash
git push
```

然后去 Render 看：

- 有没有新的部署记录
- 状态是不是 `Deploying`

如果没有自动触发，也可以在 Render 手动点：

```text
Manual Deploy
```

---

### 3. 网站第一次打开慢正常吗？

正常。

因为你现在用的是 Render 免费服务，空闲后会休眠。
第一次访问会出现冷启动，所以会慢一点。

---

### 4. AI 助手变成“离线说明”怎么办？

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

---

## 七、你以后可以直接复制的模板

### 模板 A：普通更新

```bash
cd "/Users/g/Desktop/人物画像可视化/人物画像可视化"
git status
git add -A
git commit -m "update website content"
git push
```

### 模板 B：只检查有没有改动

```bash
cd "/Users/g/Desktop/人物画像可视化/人物画像可视化"
git status
```

### 模板 C：检查 Python 后端语法

```bash
cd "/Users/g/Desktop/人物画像可视化/人物画像可视化"
python3 -m py_compile backend_formal.py
```

---

## 八、一句话记忆版

以后你只要记住这句话就行：

```text
本地改完 -> git add -> git commit -> git push -> 等 Render 变成 Live
```
