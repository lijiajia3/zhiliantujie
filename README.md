# 智鏈圖解 — 智能人力資源分析平台  
Zhilian Insight — Intelligent Human Resource Analysis Platform  
Zhilian Insight — Plateforme d’analyse intelligente des ressources humaines

由 [山西瑞佳恒创科技有限公司](https://github.com/lijiajia3) 主導研發，本系統致力於為第二、第三產業提供一站式智能化人員評估與崗位推薦服務。  
Developed by [Shanxi Ruijia Hengchuang Technology Co., Ltd.](https://github.com/lijiajia3), this platform offers intelligent workforce evaluation and job-matching services for secondary and tertiary industries.  
[Développée par [Shanxi Ruijia Hengchuang Technology Co., Ltd.](https://github.com/lijiajia3), cette plateforme propose des services intelligents d’évaluation du personnel et de recommandation de postes pour les secteurs secondaire et tertiaire.
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build with FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Frontend: React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react)](https://reactjs.org/)
[![Platform: Cross-industry HR](https://img.shields.io/badge/Platform-跨行业人力平台-blueviolet)]()
[![Language: 中文/EN/FR](https://img.shields.io/badge/Languages-中文%2FEN%2FFR-orange)]()
---

## 📌 功能特色 / Features / Fonctionnalités

- 🧠 **LLM + 機器學習** 智能推薦算法  
  Intelligent recommendation based on LLM and machine learning  
  Recommandation intelligente basée sur LLM et apprentissage automatique

- 📋 支援簡歷解析、自動匹配、任務追蹤  
  Resume parsing, auto-matching, task tracking  
  Analyse de CV, appariement automatique, suivi des tâches

- 📊 完善的數據可視化（雷達圖、PR 曲線、ROC 曲線等）  
  Comprehensive visualizations (radar, PR curve, ROC, etc.)  
  Visualisation complète des données (radar, courbes PR, courbes ROC, etc.)

- 🔐 權限管理（admin / HR / 員工）  
  Role-based permission system (admin, HR, staff)  
  Gestion des autorisations basée sur les rôles (admin, RH, employés)

- 🌐 基於 FastAPI + React 的全棧系統  
  Full-stack system powered by FastAPI and React  
  Système full-stack propulsé par FastAPI et React

---

## 📁 專案結構 / Project Structure / Structure du projet

```
project/
├── hr-backend/       # FastAPI 後端 / backend
├── client/           # React 前端 / frontend
└── README.md         # 說明文件 / documentation
```

---

## 🚀 快速啟動 / Quick Start / Démarrage rapide

### 📦 安裝依賴 / Install dependencies / Installer les dépendances

```bash
# 後端 / Backend
cd hr-backend
pip install -r requirements.txt

# 前端 / Frontend
cd client
npm install
```

### ▶️ 啟動系統 / Run the system / Lancer le système

```bash
# 啟動 FastAPI
uvicorn main:app --reload

# 啟動前端 / Start frontend
cd client
npm run dev
```

---

## 📃 授權聲明 / License / Licence

本項目採用 MIT 授權許可，允許商用、修改與分發。請參閱 [LICENSE](LICENSE) 了解詳情。  
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.  
Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.

---

## 📞 聯繫方式 / Contact / Contact

李佳轩（董事長 / CEO / Président）  
📫 郵箱 / Email :  
lijiaxuan@sxrjhc.cn  
xuanxuanshiliu@gmail.com  
🏢 公司 / Company : 
山西瑞佳恒创科技有限公司  

---

## Git 提交訊息樣板建議

建議用英文提交訊息格式如下：
```
Initial commit: upload FastAPI backend and project structure
```

可依類型分類為：
- `Initial commit: ...`
- `Add: ...`
- `Fix: ...`
- `Update: ...`
- `Docs: update README and LICENSE`
- `Refactor: ...`