# vrag_demo


# 视频查询系统

本项目是一个视频查询系统，用户可以通过上传视频，系统将视频拆分为帧，并将这些帧及其嵌入数据存储在数据库中。用户可以通过文本或语音输入进行搜索，系统会返回最相似的帧并从该帧开始播放对应的视频。

## 功能特性

- **上传视频**：用户可以通过网页界面上传视频。
- **帧提取**：上传的视频在服务器端被处理为帧。
- **嵌入存储**：帧的嵌入数据会被计算并与视频名称、ID及帧信息一起存储在数据库中。
- **搜索功能**：用户可以通过文本或语音输入进行帧的搜索。
- **帧和视频展示**：展示最相似的帧，并从匹配的帧开始播放对应的视频。
- **响应式前端**：用户友好的前端界面支持拖拽上传视频及动态查询结果展示。

## 项目结构


```text
project_root/
├── server/
│   ├── app.py
│   ├── videos/
│   ├── frames/
│   ├── public/
│   └── vrag_service.py
├── database/
│   ├── embeddings.db
│   ├── migrations/
│   └── models.py
├── frontend/
│   ├── index.html
│   ├── styles/
│   ├── scripts/
│   └── assets/
└── README.md
```


### 服务器端

- **`app.py`**：主应用入口，包含路由和服务器配置。
- **`models/`**：包含数据库模型，包括帧和视频模型。
- **`controllers/`**：处理视频上传、帧提取、嵌入计算和搜索查询的逻辑。
- **`middlewares/`**：处理请求、认证和其他跨领域问题的中间件。
- **`routes/`**：定义视频上传、搜索查询和结果检索的API端点。
- **`public/`**：服务器提供的静态文件，包括JavaScript和CSS文件。
- **`utils/`**：实用函数，包括嵌入计算、视频处理和数据库交互。

### 数据库

- **`embeddings.db`**：SQLite数据库，用于存储帧的嵌入数据及相关元数据。
- **`migrations/`**：数据库迁移文件。
- **`models.py`**：定义数据库架构，包括视频、帧和嵌入数据的表。

### 前端

- **`index.html`**：用户与系统交互的主前端界面。
- **`styles/`**：用于样式化前端界面的CSS文件。
- **`scripts/`**：处理用户界面交互的JavaScript文件，包括视频上传和搜索功能。
- **`assets/`**：前端使用的静态资源，如图片和图标。

## 设置

### 前置条件

- Python 3.8或更高版本
- Node.js
- SQLite（或其他首选数据库）
- [安装MoviePy](https://pypi.org/project/moviepy/)
- [安装OpenAI的CLIP模型](https://github.com/openai/CLIP)

### 安装步骤

1. **克隆仓库：**

   ```bash
   git clone https://github.com/Lexieqiqi/vrag_demo.git
   cd vrag_demo

2. **设置虚拟环境：**
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在Windows上使用 `venv\Scripts\activate`

3. **安装依赖项：**
   ```bash
    pip install -r requirements.txt

4. **设置数据库：**
   运行迁移文件以设置数据库架构。
   ```bash
   python manage.py migrate

5. **启动服务器：**
   ```bash
   python vrag_service.py

6. **前端设置：**
   导航到frontend/目录并在浏览器中打开index.html以访问用户界面。


## 使用说明

### 上传视频

- 将视频文件拖放到上传区域，或点击上传框选择视频。

### 搜索帧

- 在文本框中输入查询，或使用语音搜索选项找到与查询相似的帧。
- 系统将展示最相关的帧，并从该帧开始播放对应的视频。

## 未来改进

- **增强搜索**：改进搜索算法以提高帧匹配的准确性。
- **可扩展性**：支持更大的数据库和云存储解决方案。
- **多语言支持**：在搜索功能中添加对多语言的支持。
- **实时处理**：实现实时视频处理和查询功能。

## 贡献指南

欢迎贡献！请按照以下步骤进行贡献：

1. Fork该仓库。
2. 创建一个新的分支（`git checkout -b feature-branch-name`）。
3. 进行修改。
4. 提交更改（`git commit -m 'Add some feature'`）。
5. 推送到分支（`git push origin feature-branch-name`）。
6. 打开一个Pull Request。

## 许可

本项目采用MIT许可 - 请参阅[LICENSE](LICENSE)文件了解详细信息。

## 联系方式

如有任何问题，请联系[lexieqiqi@gmail.com](mailto:lexieqiqi@gmail.com)。
