# FixMyPaper: Vercel Deployment & AWS Integration Guide

This guide details exactly how to deploy your frontend to Vercel and establish a secure, high-performance connection to your existing AWS backend.

---

## 1. Environment Configuration

Next.js requires the `NEXT_PUBLIC_` prefix for any variables used on the client-side.

### Local Configuration (`frontend/.env.local`)
Create this file for local testing against your production API:
```bash
NEXT_PUBLIC_API_URL=https://api.fixmypaper.com
```

### Vercel Dashboard Configuration
1.  Go to your project in the [Vercel Dashboard](https://vercel.com/dashboard).
2.  Navigate to **Settings** > **Environment Variables**.
3.  Add the following:
    - **Key**: `NEXT_PUBLIC_API_URL`
    - **Value**: `https://api.fixmypaper.com`

---

## 2. Backend Configuration (The "Missing Link")

Even though your backend is already running on AWS, you **must** update its CORS policy to allow your new Vercel domain to communicate with it.

### FastAPI CORS Snippet
Update your `backend/app/main.py` (or equivalent) with this production-ready configuration:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# List of allowed origins
origins = [
    "https://api.fixmypaper.com",      # Your API domain
    "https://your-app.vercel.app",     # Your specific Vercel deployment
    "http://localhost:3000",           # Local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    # OR use allow_origin_regex for all Vercel previews:
    # allow_origin_regex="https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### AWS S3 CORS Configuration
If you choose **Approach B (Direct S3 Upload)**, you must enable CORS on your S3 bucket in the AWS Console:

1.  Go to **S3** > **[Your-Bucket]** > **Permissions** > **CORS**.
2.  Paste this JSON:
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET"],
    "AllowedOrigins": ["https://your-app.vercel.app", "http://localhost:3000"],
    "ExposeHeaders": ["ETag"]
  }
]
```

---

## 3. Deployment Steps

1.  **Push to GitHub**: Ensure your `frontend` directory is in your repository.
2.  **Import to Vercel**:
    - Select your repository.
    - Set the **Root Directory** to `frontend`.
    - Ensure **Framework Preset** is set to `Next.js`.
3.  **Deploy**: Vercel will build and serve your app at a `.vercel.app` URL.

---

## 4. Debugging Checklist

> [!WARNING]
> **Mixed Content Error**: If your frontend is HTTPS (Vercel always is) and your backend is HTTP, the browser will block all requests. Ensure your ALB uses an SSL certificate from ACM.

*   **CORS Error?**: Check the `Access-Control-Allow-Origin` header in the browser's Network tab. It must match your Vercel URL exactly.
*   **Preflight (OPTIONS) Failed?**: Ensure your ALB/EKS isn't blocking `OPTIONS` requests before they reach FastAPI.
*   **File Upload Limit?**: If uploads fail for large files, check the `client_max_body_size` in your NGINX or ALB configuration (usually defaults to 1MB).
