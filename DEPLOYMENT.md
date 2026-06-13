# 🚀 FLEX-IT-OUT Deployment Guide

## 📋 Prerequisites

1. **GitHub Account** - To host your code
2. **Vercel Account** - For frontend deployment (free)
3. **Railway Account** - For backend deployment (free tier available)
4. **Supabase Account** - For database (free tier available)

---

## 🎯 Step-by-Step Deployment

### **Step 1: Prepare Your Code**

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/flex-flow-fusion.git
   git push -u origin main
   ```

### **Step 2: Deploy Backend to Railway**

1. **Go to [Railway.app](https://railway.app)**
2. **Sign up/Login** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. **Select the `backend` folder**
7. **Add Environment Variables:**
   ```
   DATABASE_URL=your_supabase_postgres_connection_string
   JWT_SECRET=your_secret_key_here
   ```
8. **Click "Deploy"**
9. **Wait for deployment and copy the generated URL** (e.g., `https://your-app.railway.app`)

### **Step 3: Deploy Frontend to Vercel**

1. **Go to [Vercel.com](https://vercel.com)**
2. **Sign up/Login** with GitHub
3. **Click "New Project"**
4. **Import your GitHub repository**
5. **Configure project:**
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
6. **Add Environment Variable:**
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```
7. **Click "Deploy"**

### **Step 4: Set Up Supabase Postgres**

1. **Go to [Supabase](https://supabase.com)**
2. **Create a new project**
3. **Open the database settings and copy the Postgres connection string**
4. **Add it to your Render or Railway environment variables as `DATABASE_URL`**

---

## 🔧 Configuration Files

### **Frontend (Vercel)**
- `vercel.json` - Vercel configuration
- `vite.config.ts` - Vite configuration
- Environment variable: `VITE_API_URL`

### **Backend (Railway or Render)**
- `railway.json` - Railway configuration
- `Procfile` - Process definition
- `runtime.txt` - Python version
- Environment variables: `DATABASE_URL`, `JWT_SECRET`

---

## 🌐 Your Live URLs

After deployment, you'll have:
- **Frontend:** `https://your-app.vercel.app`
- **Backend:** `https://your-app.railway.app`
- **API Docs:** `https://your-app.railway.app/docs`

---

## 🔍 Troubleshooting

### **Common Issues:**

1. **CORS Errors:**
   - Update backend CORS settings in `app/main.py`

2. **Environment Variables:**
   - Double-check all environment variables are set correctly

3. **Build Failures:**
   - Check build logs in Vercel/Railway dashboard
   - Ensure all dependencies are in `package.json`/`requirements.txt`

4. **Database Connection:**
   - Verify Supabase Postgres connection string
   - Check network access settings

---

## 📱 Testing Your Deployment

1. **Visit your Vercel URL**
2. **Register a new account**
3. **Test the workout interface**
4. **Check if pose detection works**
5. **Verify notifications and points system**

---

## 💰 Cost Breakdown

- **Vercel:** Free tier (unlimited deployments)
- **Railway:** Free tier (limited usage)
- **Supabase:** Free tier available for Postgres hosting
- **Total Cost:** $0/month

---

## 🔄 Updates & Maintenance

To update your deployed app:
1. **Push changes to GitHub**
2. **Vercel/Railway will auto-deploy**
3. **Monitor deployment logs**
4. **Test the live version**

---

## 🆘 Support

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Test locally first
4. Check this guide for common solutions 