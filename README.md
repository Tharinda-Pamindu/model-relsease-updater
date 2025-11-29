# Hugging Face Daily Updates

This repository contains a GitHub Actions workflow that fetches the latest models and datasets from Hugging Face (created in the last 24 hours) and emails a summary to a specified recipient.

## How it Works

1.  **`fetch_updates.py`**: A Python script that queries the Hugging Face API for new models and datasets.
2.  **GitHub Actions**: A workflow (`.github/workflows/daily_updates.yml`) runs this script daily at 8:00 AM UTC.

## Setup

### 1. Fork or Clone this Repository
Ensure you have this code in your GitHub repository.

### 2. Configure GitHub Secrets
To send emails securely, you need to configure the following secrets in your repository settings:

1.  Go to **Settings** > **Secrets and variables** > **Actions**.
2.  Click **New repository secret**.
3.  Add the following secrets:

    *   `EMAIL_SENDER`: The email address sending the updates (e.g., `your-email@gmail.com`).
    *   `EMAIL_PASSWORD`: The app password for the sender email.
        *   **Note for Gmail**: You cannot use your regular password. You must enable 2-Step Verification and generate an **App Password**. [Guide here](https://support.google.com/accounts/answer/185833).
    *   `EMAIL_RECEIVER`: The email address(es) to receive the updates. You can specify multiple emails separated by a comma (e.g., `user1@example.com,user2@example.com`).

### 3. Run Manually
You can test the workflow by going to the **Actions** tab, selecting **Hugging Face Daily Updates**, and clicking **Run workflow**.

## Customization

*   **Schedule**: Edit `.github/workflows/daily_updates.yml` to change the cron schedule.
*   **Threshold**: Edit `fetch_updates.py` to change the time window (default is 24 hours).
