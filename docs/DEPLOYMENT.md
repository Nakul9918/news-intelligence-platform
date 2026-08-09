# 🚀 Production Deployment Manual — News Intelligence Platform

This manual provides complete step-by-step instructions for deploying the **News Intelligence Platform** to Production Cloud Servers (AWS EC2, DigitalOcean, Hetzner, GCP), PaaS platforms (Render, Railway, Streamlit Community Cloud), or Docker infrastructure.

---

## 📋 Recommended Deployment Target Summary

| Platform | Best Used For | Monthly Cost | Difficulty |
| :--- | :--- | :--- | :--- |
| **AWS EC2 / VPS (Ubuntu)** | **Full Production Deployment** (MongoDB + Kafka + ES + FastAPI + Streamlit) | ~$10 - $20/mo | Easy (10 min setup) |
| **Streamlit Cloud + Render** | **Zero-Cost Demo Deployment** (Dashboard on Streamlit Cloud, API on Render) | **FREE** | Very Easy (5 min setup) |
| **Docker Compose VM** | **Enterprise On-Prem / Cloud VM** | ~$15/mo | Easy (1 Command) |

---

## Option 1: Cloud VPS Deployment (AWS EC2 / DigitalOcean / Linode)

Recommended Specification: **Ubuntu 22.04 LTS / 24.04 LTS (2 vCPU, 4GB - 8GB RAM)**

### Step 1: Connect to Server & Install Dependencies
```bash
# Update Ubuntu packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12, Git, and Docker
sudo apt install -y python3-pip python3-venv git curl docker.io docker-compose-v2

# Start & Enable Docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/Nakul9918/news-intelligence-platform.git
cd news-intelligence-platform/project
```

### Step 3: Set Environment Variables
Create a `.env` file in the project directory:
```bash
nano .env
```
Add your keys and configuration:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
MONGO_URI=mongodb://127.0.0.1:27017
DATABASE_NAME=news_db
KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
KAFKA_TOPIC=news-topic-v2
ELASTICSEARCH_HOST=http://127.0.0.1:9200
ELASTICSEARCH_INDEX=news_articles
```

### Step 4: Launch Infrastructure Stack (Kafka + Elasticsearch + MongoDB)
```bash
# Launch Kafka, Zookeeper, and Elasticsearch containers
docker compose -f docker/docker-compose.yml up -d

# Start MongoDB local service (or run MongoDB container)
docker run -d --name news_mongodb -p 27017:27017 -v mongo_data:/data/db mongo:latest
```

### Step 5: Setup Python Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Start All Platform Daemons
```bash
# Verify infrastructure health
python check_infrastructure.py

# Launch background daemons (Ingestion, Consumer, Orchestrator, API, Dashboard)
python start_daemons.py
```

### Step 7: Access Your Live Production Platform
- **Streamlit Dashboard**: `http://<your-server-ip>:8501`
- **FastAPI Documentation**: `http://<your-server-ip>:8000/docs`
- **Platform Health Observability**: `http://<your-server-ip>:8501` → Navigate to `12. PLATFORM HEALTH`

---

## Option 2: FREE Cloud Deployment (Streamlit Cloud + Render)

### A. Deploy Frontend Dashboard on Streamlit Community Cloud (FREE)
1. Go to [https://share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
2. Click **New App**.
3. Select Repository: `Nakul9918/news-intelligence-platform`
4. Select Branch: `main`
5. Main file path: `project/dashboard.py`
6. Under **Advanced Settings**, add Secret:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key"
   ```
7. Click **Deploy!** Your app will be live at `https://news-intelligence-platform.streamlit.app`.

### B. Deploy FastAPI Backend on Render (FREE)
1. Go to [https://render.com](https://render.com) and create a **Web Service**.
2. Connect repository `Nakul9918/news-intelligence-platform`.
3. Build Command: `pip install -r project/requirements.txt`
4. Start Command: `python project/run_api.py`
5. Add Environment Variables: `GEMINI_API_KEY`.

---

## Option 3: Process Supervisor Management (systemd for Linux)

To run the platform daemons permanently as background system services on Linux:

Create `/etc/systemd/system/news-platform.service`:
```ini
[Unit]
Description=News Intelligence Platform Daemons
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/news-intelligence-platform/project
ExecStart=/home/ubuntu/news-intelligence-platform/project/.venv/bin/python start_daemons.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now news-platform
```

---

## 🔒 Security Best Practices for Production

1. **Firewall Setup (ufw)**:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 8501/tcp
   sudo ufw enable
   ```
2. **Reverse Proxy (Nginx + SSL Certbot)**:
   Use Nginx to map domain `news.yourdomain.com` to port `8501` with free Let's Encrypt SSL certificates (`certbot --nginx`).
