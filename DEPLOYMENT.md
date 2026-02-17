# Deployment Guide: Student Loan NELFUND Chatbot

Deploy **frontend** on **Vercel** and **backend** on **Render** or **Railway**. The backend runs your FastAPI app and builds the vector database at deploy time.

---

## Before You Start

- [ ] Code is on **GitHub** (or GitLab).
- [ ] You have an **OpenAI API key**.
- [ ] The **data** folder is in the repo: `data/nelfund_docs/` with your PDF/txt files (so ingestion can run during backend build).

---

## Part 1: Deploy the Backend (Render or Railway)

### Option A: Render

1. **Sign up / log in**  
   Go to [render.com](https://render.com) and sign in (e.g. with GitHub).

2. **New Web Service**  
   - Dashboard → **New +** → **Web Service**.  
   - Connect your **GitHub** account if needed and select the repo `Student_loan_Nelify` (or your repo name).

3. **Settings**
   - **Name:** e.g. `student-loan-backend`
   - **Region:** pick one close to you
   - **Root Directory:** `backend`
   - **Runtime:** Python
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python -m app.rag.ingest
     ```
   - **Start Command:**
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance type:** Free (or paid if you prefer)

4. **Environment variables** (in Render dashboard)
   - **OPENAI_API_KEY** = your OpenAI API key  
   - **FRONTEND_URL** = your Vercel frontend URL (add this after you deploy the frontend, e.g. `https://your-app.vercel.app`)

5. **Deploy**  
   Click **Create Web Service**. Render will build (install deps + run ingestion) then start the app. Wait until the service is **Live**.

6. **Backend URL**  
   Copy the URL, e.g. `https://student-loan-backend.onrender.com`. You’ll use this for the frontend.

---

### Option B: Railway

1. **Sign up / log in**  
   Go to [railway.app](https://railway.app) and sign in with GitHub.

2. **New project**  
   - **New Project** → **Deploy from GitHub repo** → select `Student_loan_Nelify`.

3. **Configure the service**
   - After the repo is connected, click the service (or add a **Web Service**).
   - Set **Root Directory** to `backend`.
   - **Build:** Railway often auto-detects Python. If you need a custom build, use:
     - Build command: `pip install -r requirements.txt && python -m app.rag.ingest`
   - **Start command:**  
     `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Settings** → **Networking** → enable **Public networking** and note the generated URL.

4. **Environment variables** (Railway dashboard → Variables)
   - **OPENAI_API_KEY** = your OpenAI API key  
   - **FRONTEND_URL** = your Vercel frontend URL (add after frontend deploy)

5. **Deploy**  
   Railway will build and deploy. Copy the public URL (e.g. `https://xxx.up.railway.app`).

---

## Part 2: Deploy the Frontend (Vercel)

1. **Sign up / log in**  
   Go to [vercel.com](https://vercel.com) and sign in with GitHub.

2. **Import project**  
   - **Add New** → **Project** → import the same repo `Student_loan_Nelify`.

3. **Configure**
   - **Root Directory:** leave default (repo root) or set to `frontend` if your app lives only there.
   - **Framework Preset:** Vite (Vercel usually detects it).
   - **Build Command:** `npm run build` (default for Vite).
   - **Output Directory:** `dist` (default for Vite).

4. **Environment variable**
   - **Name:** `VITE_API_BASE_URL`  
   - **Value:** your backend URL from Render or Railway (no trailing slash), e.g.  
     `https://student-loan-backend.onrender.com`

5. **Deploy**  
   Click **Deploy**. When it’s done, copy the frontend URL (e.g. `https://your-app.vercel.app`).

---

## Part 3: Connect Frontend and Backend

1. **Backend CORS**  
   In **Render** or **Railway**, add or update the env var:
   - **FRONTEND_URL** = your Vercel URL, e.g. `https://your-app.vercel.app`  
   (No trailing slash.)

2. **Redeploy backend**  
   Trigger a redeploy so the backend picks up `FRONTEND_URL` and allows requests from your Vercel domain.

3. **Test**  
   Open your Vercel URL, ask a question (e.g. “Who is eligible for NELFUND?”). It should hit the backend and return an answer.

---

## Quick Reference

| What        | Where to set | Example |
|------------|--------------|---------|
| Backend URL for frontend | Vercel → env: `VITE_API_BASE_URL` | `https://student-loan-backend.onrender.com` |
| Frontend URL for CORS    | Render/Railway → env: `FRONTEND_URL` | `https://your-app.vercel.app` |
| OpenAI key               | Render/Railway → env: `OPENAI_API_KEY` | (your key) |

---

## Troubleshooting

- **Backend build fails on ingestion**  
  Ensure `data/nelfund_docs/` exists in the repo and contains at least one PDF or `.txt` file.

- **Frontend: “Failed to fetch” or CORS errors**  
  - Check `FRONTEND_URL` on the backend matches the Vercel URL exactly (no trailing slash).  
  - Redeploy the backend after changing env vars.

- **Backend uses Python 3.14 locally but Render/Railway need 3.12**  
  The repo has `backend/runtime.txt` with `python-3.12.7` for Render. Railway will use the Python version from your runtime or buildpack; 3.12 is recommended.

- **Cold starts (Render free tier)**  
  The first request after idle can take 30–60 seconds while the service starts. Later requests are fast.
