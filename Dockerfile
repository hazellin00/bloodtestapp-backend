# 1. 使用輕量的 Python 3.11 映像檔
FROM python:3.11-slim

# 2. 設定工作目錄
WORKDIR /app

# 3. 複製套件清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 複製所有後端程式碼到容器內
COPY . .

# 5. 開放 10000 連接埠 (Render 預設)
EXPOSE 10000

# 6. 啟動指令 (指向 app/main.py 中的 app 物件)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]