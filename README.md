# **Kura: Simple File Storage System**
Kura is a lightweight storage system that lets you upload, download, and delete files easily. Manage your files efficiently while keeping control of your data.

# Getting Started
To get started with Kura, follow these simple steps:

## Prerequisites
- [Docker](https://www.docker.com/)

## Installation
1. **Clone the repository:**
```bash
git clone https://github.com/janpeix04/sc-kura.git
cd sc-kura
```

2. **Configure email (for account verification)**

    Follow [Google's guide](https://support.google.com/accounts/answer/185833?hl=en) to set up your email for sending verification messages in Kura.

3. **Create a `.env` file in the `backend` folder**
```bash
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7

MAIL_USERNAME=<youremail@gmail.com>   # Must match the Google App Password account
MAIL_PASSWORD=<google_app_password>   # Use a Google App Password, not your regular Gmail password
MAIL_FROM=<youremail@gmail.com>       # Must match MAIL_USERNAME

EMAIL_TEMPLATE_PATH=email_templates/build
```

4. **Install docker image**
```bash
docker build --platform=linux/amd64 -t sc-kura:latest .
docker compose --env-file backend/.env up # add -d to run in the background
```

## Usage
Once Kura is running, open your web browser and go to: [http://localhost:3000](http://localhost:3000)

# Features
- **Web-Based Interface:** Access Kura from any modern browser.
- **JWT Authentication & Verification:** Secure login with JWT tokens and account activation via email verification code.
- **Asynchronous Email Handling:** Emails are sent via Celery tasks for fast and responsive signup.
- **File Management:** Upload, download, and delete files directly through the web interface.

# Contributing
We welcome contributions to Kura! If you'd like to help improve this project:

1. Fork the repository
2. Create a new branch (`git checkout -b feat/AmazingFeature`).
3. Make your changes and commit them (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feat/AmazingFeature`).
5. Open a Pull Request.

Please ensure your code adheres to our [coding guidelines](./DEVELOPMENT.md) and feel free to open an issue if you encounter any bugs or have feature suggestions.

# License
Distributed under the MIT License. See [LICENSE](./LICENSE) for more information.