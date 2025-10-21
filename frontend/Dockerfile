# ============================================================
# 1️⃣ Build Stage — React + Vite アプリのビルド
# ============================================================
FROM node:20-alpine AS build

# 作業ディレクトリ
WORKDIR /app

# 依存ファイルをコピー
COPY package.json package-lock.json* vite.config.js /app/

# npm install
RUN npm install

# ソースコードとindex.htmlをコピー
COPY index.html /app/
COPY src /app/src

# 本番ビルド
RUN npm run build

# ============================================================
# 2️⃣ Runtime Stage — Nginxで静的ファイルを配信
# ============================================================
FROM nginx:1.27-alpine

# Nginx 設定を上書き（CORS対応 & APIプロキシ）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ビルド済みファイルをコピー
COPY --from=build /app/dist /usr/share/nginx/html

# ポート公開
EXPOSE 80

# ============================================================
# 1️⃣ Build Stage — React + Vite アプリのビルド
# ============================================================
FROM node:20-alpine AS build

# 作業ディレクトリ
WORKDIR /app

# 依存ファイルをコピー
COPY package.json package-lock.json* vite.config.js /app/

# npm install
RUN npm install

# ソースコードとindex.htmlをコピー
COPY index.html /app/
COPY src /app/src

# 本番ビルド
RUN npm run build

# ============================================================
# 2️⃣ Runtime Stage — Nginxで静的ファイルを配信
# ============================================================
FROM nginx:1.27-alpine

# Nginx 設定を上書き（CORS対応 & APIプロキシ）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ビルド済みファイルをコピー
COPY --from=build /app/dist /usr/share/nginx/html

# ポート公開
EXPOSE 80

# コンテナ起動時に nginx をフォアグラウンドで実行
CMD ["nginx", "-g", "daemon off;"]
# コンテナ起動時に nginx をフォアグラウンドで実行
CMD ["nginx", "-g", "daemon off;"]

