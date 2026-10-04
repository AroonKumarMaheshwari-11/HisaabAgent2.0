<div align="center">

# 💰 HisaabAgent2.0

### AI-Powered RAG Business Co-Pilot for Pakistani Retailers

An intelligent assistant designed for small businesses in Pakistan to manage financial receivables, track credit, and provide expert retail advisory based on a custom knowledge playbook. Understands Roman Urdu and English.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?logo=google&logoColor=white)

</div>

---

## ✨ Overview

HisaabAgent2.0 combines **Retrieval-Augmented Generation (RAG)** with **Agentic Function Calling** using the Google Gemini API. It allows micro-business owners to query live receivables data and instantly retrieve professional retail guidance from a built-in playbook (`retail_playbook.md`).

* **Live App:** [View on Streamlit Cloud](https://hisaabagent20-hu3gqkctpvveczee99xacy.streamlit.app/)
* **Category:** Business / Retail Automation

---

## 🚀 Key Features

* 💸 **Receivables Management:** Real-time tracking of customer credit and dues (e.g., Ali and Ahmed receivables totaling 8,500 PKR).
* 🤖 **Agentic Function Calling:** The AI model intelligently chooses between database tools (`get_receivables`) and knowledge base search (`search_knowledge`) depending on the user's query.
* 📚 **RAG Knowledge Base:** Built-in `retail_playbook.md` containing expert advice on credit recovery, tax basics, and shop management.
* 🌐 **Bilingual Support:** Full conversational capability in English and Roman Urdu.

---

## 👥 Team Members

* **Aroon Kumar Maheshwari** (Team Leader)
* **Dua Burfat**
* **Jamal Zafar**
* **Rohan Raj**
* **Alishba Dilawar Shaikh**

---

## 🛠️ Architecture & Tech Stack

* **Frontend & Deployment:** Streamlit / Streamlit Community Cloud
* **AI Engine:** Google Gemini API (`google-genai` / `google-generativeai`)
* **Backend Logic:** Python, Custom Function Calling Tools, Markdown-based RAG
