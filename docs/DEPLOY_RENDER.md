# Render 部署说明

这份项目已经调整成“单服务部署”模式：
- `backend_formal.py` 同时提供 API 和前端页面
- 浏览器访问根路径 `/` 就会打开 `index_formal.html`
- 前端请求 API 时使用相对路径 `/api/formal`

## 1. 部署前准备

把代码上传到 GitHub 仓库，确认以下文件已经包含：
- `backend_formal.py`
- `requirements.txt`
- `render.yaml`
- 所有 `html` 文件
- `assets/`
- `1.jpeg`
- `formal_student_data.csv`

## 2. 在 Render 创建服务

1. 登录 Render
2. 选择 `New +`
3. 选择 `Blueprint` 或 `Web Service`
4. 连接你的 GitHub 仓库

如果你使用 `Blueprint`：
- Render 会自动读取仓库里的 `render.yaml`

如果你使用 `Web Service` 手动填写：
- Environment: `Python`
- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
uvicorn backend_formal:app --host 0.0.0.0 --port $PORT
```

## 3. 环境变量

如果你要启用 AI 问答，在 Render 后台添加一组环境变量即可。

### 方案 A：DeepSeek / OpenAI 兼容接口

- `AI_PROVIDER=openai`
- `AI_API_KEY=你的密钥`
- `AI_BASE_URL=https://api.deepseek.com`
- `AI_MODEL=deepseek-chat`

也兼容旧变量：
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_MODEL`

### 方案 B：Anthropic Messages 兼容接口

适用于类似 `https://v2.aicodee.com` 这类 `anthropic-messages` 通道：

- `AI_PROVIDER=anthropic`
- `AI_API_KEY=你的密钥`
- `AI_BASE_URL=https://v2.aicodee.com`
- `AI_MODEL=MiniMax-M2.7-highspeed`

如果没有配置成功，页面仍可正常使用，只是 AI 助手会返回离线说明版回答。

## 4. 部署完成后访问

部署成功后，Render 会给你一个类似下面的网址：

```text
https://your-service-name.onrender.com/
```

常用页面：
- 首页：`/`
- 群体页：`/index_formal.html`
- 学生页：`/student_formal.html?id=20240001`
- 对标总览：`/benchmark_overview.html`
- 多校比较：`/benchmark_compare.html`

## 5. 注意事项

- Render 免费实例在一段时间无访问后可能休眠，首次打开会慢一点。
- `formal_student_data.csv` 目前是随代码一起部署的静态数据文件。
- 如果后续你想让数据在线编辑、持久更新，下一步就要再加数据库。
