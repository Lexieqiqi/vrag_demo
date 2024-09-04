import torch
from PIL import Image
import cn_clip.clip as clip
from cn_clip.clip import load_from_name
from moviepy.editor import VideoFileClip
import sqlite3
import numpy as np
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# 配置目录和参数
VIDEOS_DIR = 'videos'
FRAMES_DIR = 'frames'
DB_PATH = 'embeddings.db'
FPS = 1  # 帧提取速率（每秒帧数）

def init_db(db_path=DB_PATH):
    """初始化数据库，创建必要的表格。"""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # 创建 Videos 表
        c.execute('''
            CREATE TABLE IF NOT EXISTS Videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                path TEXT
            )
        ''')

        # 创建 ImageEmbeddings 表
        c.execute('''
            CREATE TABLE IF NOT EXISTS ImageEmbeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                frame_path TEXT UNIQUE,
                embedding BLOB,
                FOREIGN KEY (video_id) REFERENCES Videos(id)
            )
        ''')
        conn.commit()

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = load_from_name("ViT-B-16", device=device, download_root='./')
model.eval()

def video_to_images(video_path, output_folder, video_id, fps=FPS):
    """从视频中提取帧，并按视频 ID 命名保存。"""
    video_clip = VideoFileClip(video_path)
    # 帧文件名格式：video_{video_id}_frame%04d.png
    frame_filename_template = os.path.join(output_folder, f"video_{video_id}_frame%04d.png")
    video_clip.write_images_sequence(frame_filename_template, fps=fps)


def store_embeddings_in_db(image_paths, video_id, db_path=DB_PATH):
    """生成并存储帧的嵌入向量到数据库中。"""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        for frame_path in image_paths:
            absolute_frame_path = os.path.abspath(frame_path)
            image = preprocess(Image.open(absolute_frame_path)).unsqueeze(0).to(device)
            with torch.no_grad():
                image_features = model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True)  # 归一化
            embedding_blob = image_features.cpu().numpy().astype(np.float32).tobytes()

            # 插入或替换嵌入向量
            c.execute("""
                INSERT OR REPLACE INTO ImageEmbeddings (video_id, frame_path, embedding)
                VALUES (?, ?, ?)
            """, (video_id, absolute_frame_path, embedding_blob))
        conn.commit()

def cosine_similarity(a, b):
    """计算两个向量的余弦相似度。"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def query_db_with_text(query, db_path=DB_PATH, top_n=4):
    """根据文本查询数据库，返回最相似的前 N 帧。"""
    text = clip.tokenize([query]).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    text_features = text_features.cpu().numpy()

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT ImageEmbeddings.frame_path, ImageEmbeddings.embedding, Videos.path, Videos.id, Videos.name
            FROM ImageEmbeddings
            JOIN Videos ON ImageEmbeddings.video_id = Videos.id
        """)

        similarities = []
        for row in c.fetchall():
            frame_path, embedding_blob, video_path, video_id, video_name = row
            image_features = np.frombuffer(embedding_blob, dtype=np.float32)
            similarity = cosine_similarity(text_features, image_features)
            similarities.append((frame_path, similarity, video_path, video_id, video_name))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]


@app.route('/upload', methods=['POST'])
def upload_video():
    """处理视频上传，提取帧并存储嵌入向量。"""
    video = request.files.get('video')
    if not video:
        return jsonify({"error": "No video uploaded"}), 400

    video_name = video.filename
    # 插入到 Videos 表，获取 video_id
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO Videos (name, path) VALUES (?, ?)", (video_name, ""))
        video_id = c.lastrowid

    # 定义保存路径，包含 video_id
    video_save_filename = f"video_{video_id}_{video_name}"
    video_save_path = os.path.join(VIDEOS_DIR, video_save_filename)
    # 更新 Videos 表中的 path 字段
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE Videos SET path = ? WHERE id = ?", (video_save_path, video_id))
        conn.commit()

    # 保存视频文件
    video.save(video_save_path)

    # 提取帧
    video_to_images(video_save_path, FRAMES_DIR, video_id, fps=FPS)

    # 收集帧文件路径
    frame_files = sorted([
        os.path.join(FRAMES_DIR, img)
        for img in os.listdir(FRAMES_DIR)
        if img.endswith('.png') and f"video_{video_id}_" in img
    ])

    # 存储嵌入向量到数据库
    store_embeddings_in_db(frame_files, video_id)

    return jsonify({"message": "Video uploaded and processed successfully."}), 200

@app.route('/query', methods=['POST'])
def query_frames():
    """根据文本查询最相似的帧，并返回相关视频信息。"""
    query_data = request.get_json()
    query_text = query_data.get('query')

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # 查询数据库
    closest_frames = query_db_with_text(query_text)

    result = []
    for frame_path, similarity, video_path, video_id, video_name in closest_frames:
        # 计算帧时间
        # 假设帧命名为 video_{video_id}_frame%04d.png
        base_filename = os.path.basename(frame_path)
        try:
            frame_number_str = base_filename.split('_frame')[1].split('.png')[0]
            frame_number = int(frame_number_str)
            frame_time = frame_number / FPS  # frame_number / 0.1 = frame_number * 10.0 秒
        except (IndexError, ValueError):
            frame_time = 0

        # 构建视频 URL
        video_url = request.host_url.rstrip('/') + '/videos/' + os.path.basename(video_path)

        result.append({
            "frame_path": frame_path,
            "video_url": video_url,
            "frame_time": frame_time,
            "similarity": float(similarity),  # 转换为浮点数以便 JSON 序列化
            "video_id": video_id,
            "video_name": video_name
        })

    return jsonify(result), 200

@app.route('/videos/<path:filename>')
def serve_video(filename):
    """提供视频文件的访问。"""
    return send_from_directory(VIDEOS_DIR, filename)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
