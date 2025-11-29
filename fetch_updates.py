import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Configuration
HF_MODELS_API = "https://huggingface.co/api/models"
HF_DATASETS_API = "https://huggingface.co/api/datasets"
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))

def fetch_new_items(api_url, item_type="Model"):
    params = {
        "sort": "createdAt",
        "direction": "-1",
        "limit": 50,
        "full": "true"
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    items = response.json()
    
    new_items = []
    # Get items from the last 24 hours
    threshold_time = datetime.utcnow() - timedelta(hours=24)
    
    for item in items:
        created_at_str = item.get("createdAt")
        if not created_at_str:
            continue
            
        # Handle different timestamp formats if necessary, HF usually uses ISO 8601
        try:
            created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            try:
                created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue

        if created_at > threshold_time:
            new_items.append({
                "id": item.get("id"),
                "likes": item.get("likes", 0),
                "downloads": item.get("downloads", 0),
                "url": f"https://huggingface.co/{item.get('id')}",
                "description": item.get("description", "No description available") or "No description available",
                "created_at": created_at
            })
    
    return new_items

def send_email(models, datasets):
    if not models and not datasets:
        print("No new items to report.")
        return

    subject = f"Hugging Face Daily Updates - {datetime.now().strftime('%Y-%m-%d')}"
    
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .container { padding: 20px; }
            .item { border-bottom: 1px solid #eee; padding: 10px 0; }
            .title { font-size: 18px; font-weight: bold; color: #333; }
            .meta { font-size: 12px; color: #666; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Hugging Face Daily Updates</h2>
    """
    
    if models:
        html_content += "<h3>🚀 New Trending Models (Last 24h)</h3>"
        for item in models[:10]: # Top 10
            html_content += f"""
            <div class="item">
                <div class="title"><a href="{item['url']}">{item['id']}</a></div>
                <div class="meta">Likes: {item['likes']} | Downloads: {item['downloads']} | Created: {item['created_at'].strftime('%Y-%m-%d %H:%M')}</div>
            </div>
            """
            
    if datasets:
        html_content += "<h3>📊 New Trending Datasets (Last 24h)</h3>"
        for item in datasets[:10]: # Top 10
            html_content += f"""
            <div class="item">
                <div class="title"><a href="{item['url']}">{item['id']}</a></div>
                <div class="meta">Likes: {item['likes']} | Downloads: {item['downloads']} | Created: {item['created_at'].strftime('%Y-%m-%d %H:%M')}</div>
            </div>
            """
            
    html_content += """
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    print("Fetching new models...")
    new_models = fetch_new_items(HF_MODELS_API, "Model")
    print(f"Found {len(new_models)} new models.")
    
    print("Fetching new datasets...")
    new_datasets = fetch_new_items(HF_DATASETS_API, "Dataset")
    print(f"Found {len(new_datasets)} new datasets.")
    
    if new_models or new_datasets:
        # Sort by likes to show most popular new items first
        new_models.sort(key=lambda x: x['likes'], reverse=True)
        new_datasets.sort(key=lambda x: x['likes'], reverse=True)
        
        if EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECEIVER:
            send_email(new_models, new_datasets)
        else:
            print("Email credentials not set. Skipping email.")
            # For debugging/logging purposes
            for m in new_models[:5]:
                print(f"Model: {m['id']} - Likes: {m['likes']}")
    else:
        print("No new updates found in the last 24 hours.")

if __name__ == "__main__":
    main()
