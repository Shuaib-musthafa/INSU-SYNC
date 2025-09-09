# INSU-SYNC: Medicare Advantage Star Ratings Optimization Platform


**Live Demo:** [(http://3.110.131.222/)]

**YT Link:** [https://youtu.be/Pup3stD1O5A]
---

## 📖 Introduction
In today's healthcare landscape, organizations face the dual challenge of improving patient outcomes while meeting regulatory quality standards and maintaining financial sustainability. Traditional performance monitoring is often retrospective, leading to missed opportunities for early intervention.  

**INSU-SYNC** is a **Medicare Advantage Star Ratings Optimization Platform** — a data-driven decision support system designed for healthcare executives and caretakers. It shifts from a **reactive** to a **proactive** approach by enabling users to:  

- Upload performance datasets (CSV format)  
- Visualize results and trends  
- Predict outcomes and patient risks  
- Identify areas for improvement  
- Receive actionable recommendations  

A key highlight for executives is the **"What-If Calculator"**, which simulates intervention strategies to estimate potential impacts on performance scores and financial outcomes.  
Additionally, the platform provides **personalized recommendations** powered by the **Gemini API**.

---

## ✨ Key Features
- **📊 Data Upload & Visualization**: Upload structured healthcare datasets (CSV) and view metrics, trends, and distributions on an interactive dashboard.  
- **🤖 Predictive Analytics**: Forecasts performance scores (Star Ratings) and patient risk levels using ML models.  
- **⚠️ Weak Measure Identification**: Automatically highlights underperforming metrics for focused improvement.  
- **💡 Actionable Recommendations**: Suggests targeted actions to close care gaps and boost performance.  
- **🧮 What-If Calculator (Executives)**: Simulates strategies and projects their impact on scores & ROI.  
- **👥 Role-Based Access**: Tailored features for Executives and Caretakers.  
- **🔐 OTP Authentication**: Secure login with **One-Time Passwords (OTP)** via email for enhanced user authentication.  

---

## 🛠️ Technical Stack & Features
- **Backend**: Flask – lightweight Python framework for server-side logic  
- **Frontend**: HTML, CSS – responsive UI  
- **Visualization**: Chart.js – interactive charts & dashboards  
- **Machine Learning**:  
  - Scikit-learn  
  - XGBoost  
  - Random Forest  
- **Database**: SQLite – lightweight, serverless storage  
- **API Integration**: Gemini API – powers the "What-If Calculator" and recommendation system  
- **Authentication**: Flask-Mail / Twilio (for OTP delivery via email or SMS)  
- **Deployment**: AWS EC2 – scalable, reliable hosting  

---

## 👥 User Roles
- **Executives**  
  - Access strategic insights  
  - ROI-focused recommendations  
  - Use the **What-If Calculator** for scenario simulations  

- **Caretakers**  
  - Personalized chatbot for plan suggestions  
  - Care-gap closure alerts  
  - Role-based dashboards  

---

## 🚀 Getting Started

### ✅ Prerequisites
- Python 3.x  
- pip  

### 🔧 Installation
```bash
# Clone the repository
git clone https://github.com/Shuaib-musthafa/INSU-SYNC.git

# Navigate to the project directory
cd INSU-SYNC

# Install dependencies
pip install -r requirements.txt
