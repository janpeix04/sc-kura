# Kura: Simple Self-Hosted File Storage System

Kura is a lightweight, self-hosted file storage system designed to run
on your local server. It allows you to securely upload, download,
organize, and manage your files with ease.

Unlike traditional cloud storage, Kura gives you full control over your
data while providing a clean web interface and essential file management
features such as search, trash handling, and folder organization.

> [!NOTE]  
> Kura is actively evolving. A new security feature called **Personal Vault (End-to-End Encryption - E2EE)** is currently under development to provide fully encrypted private storage

------------------------------------------------------------------------

## ✨ Features

### 📁 File Management

-   Upload files (up to **1.5GB per file**)
-   Download files instantly
-   Delete files safely
-   Move files and folders to trash
-   Restore files and folders from trash
-   Search files and folders quickly

### 🔐 Security & Authentication

-   JWT-based authentication using FastAPI
-   Secure account system with email verification
-   Asynchronous email handling via Celery

### 🌍 Multilingual Support

-   English 🇬🇧
-   Spanish 🇪🇸
-   Catalan 🇨🇦

### ⚡ Performance & Architecture

-   FastAPI backend for high performance
-   Dockerized deployment
-   Background task processing with Celery

------------------------------------------------------------------------

## 🚀 Getting Started

### 📦 Prerequisites

-   Docker
-   Git

------------------------------------------------------------------------

## 🛠️ Installation

### 1. Clone the repository

``` bash
git clone https://github.com/janpeix04/sc-kura.git
cd sc-kura
```

### 2. Configure Email (required for verification)

Kura uses email verification for account activation.

Follow Google's guide: https://support.google.com/accounts/answer/185833

### 3. Create `.env` file (inside `backend/`)

```bash
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7

MAIL_USERNAME=<youremail@gmail.com>   # Must match the Google App Password account
MAIL_PASSWORD=<google_app_password>   # Use a Google App Password, not your regular Gmail password
MAIL_FROM=<youremail@gmail.com>       # Must match MAIL_USERNAME

EMAIL_TEMPLATE_PATH=email_templates/build
```

### 4. Build and run with Docker

```bash
docker build --platform=linux/amd64 -t sc-kura:latest .
docker compose --env-file backend/.env up
```

------------------------------------------------------------------------

## 🌐 Usage

Once Kura is running, open your web browser and go to: http://localhost:3000

------------------------------------------------------------------------

## 🤝 Contributing

We welcome contributions to Kura! If you'd like to help improve this project:

1. Fork the repository
2. Create a new branch (`git checkout -b feat/AmazingFeature`).
3. Make your changes and commit them (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feat/AmazingFeature`).
5. Open a Pull Request.

Please ensure your code adheres to our [coding guidelines](./DEVELOPMENT.md) and feel free to open an issue if you encounter any bugs or have feature suggestions.


------------------------------------------------------------------------

## 📄 License

Distributed under the MIT License. See [LICENSE](./LICENSE) for more information.s

------------------------------------------------------------------------

## 🔐 Roadmap

Personal Vault (E2EE) coming soon: - End-to-end encryption - Client-side
encryption - Zero-knowledge storage
# sc-mirai
