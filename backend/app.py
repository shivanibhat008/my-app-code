import os
from flask import Flask

app = Flask(__name__)

@app.route("/health")
def health():
    # Kept simple for Kubernetes readiness/liveness probes
    return "OK", 200

@app.route("/")
def home():
    # Fetch the dynamically injected version tag from Kubernetes ConfigMap
    # Defaults to 'Local Development' if running outside the cluster
    app_version = os.environ.get("APP_VERSION", "Local Development")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Backend Application</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #0F172A;
                color: #F9FAFB;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background-color: #1E293B;
                padding: 40px 50px;
                border-radius: 12px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
                text-align: center;
                border-top: 4px solid #06B6D4;
                max-width: 400px;
            }}
            h1 {{
                margin-top: 0;
                color: #06B6D4;
                font-size: 2rem;
            }}
            p {{
                color: #94A3B8;
                line-height: 1.5;
            }}
            .version-badge {{
                display: inline-block;
                background-color: #2563EB;
                color: #F9FAFB;
                padding: 6px 16px;
                border-radius: 9999px;
                font-size: 0.875rem;
                font-weight: 600;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>!!Hello!!</h1>
            <p>Welcome to the backend API. The deployment pipeline is successfully configured.</p>
            <div class="version-badge">{app_version}</div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
