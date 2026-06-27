<h1 align="center">🏦 CreditMaster</h1>
<p align="center">
  <strong>An NLP-powered credit analysis model designed to automate risk assessment and generate credit opinions for the banking sector.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Ollama-0.1+-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
  <img src="https://img.shields.io/badge/NVIDIA-RTX_5060_Ti-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="NVIDIA">
  <img src="https://img.shields.io/badge/Linux_Mint-Supported-9CE311?style=for-the-badge&logo=linuxmint&logoColor=white" alt="Linux Mint">
</p>

<hr>

## 📋 Overview

**CreditMaster** is a headless Generative Artificial Intelligence microservice tailored for the banking sector. Its primary objective is to automate the risk analysis workflow and generate technical credit opinions automatically.

The solution adopts a **100% on-premise (local)** execution approach, mitigating data privacy compliance risks (such as GDPR/LGPD) and ensuring absolute banking secrecy by eliminating the need to route sensitive financial data to proprietary cloud APIs.

---

## 🏗️ Hybrid Architecture

The core of the system operates through a composition of two advanced prompt engineering and AI techniques:

<table align="center" width="100%">
  <tr>
    <td width="50%" valign="top">
      <h3>🎯 Fine-Tuning (QLoRA)</h3>
      <p>Structural modification of the <strong>Llama 3.1 8B Instruct</strong> base model's neural weights via the <strong>Unsloth</strong> library.</p>
      <ul>
        <li>Internalization of banking technical jargon.</li>
        <li>Standardization of the syntactic format of credit opinions.</li>
        <li>Extreme memory optimization for local GPU execution.</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h3>📚 RAG (Retrieval-Augmented Generation)</h3>
      <p>Dynamic injection of factual and regulatory context in real-time through a local vector database.</p>
      <ul>
        <li>Queries against internal credit manuals and Central Bank resolutions.</li>
        <li>Drastic elimination of mathematical and regulatory hallucinations.</li>
        <li>Bulletproof traceability for decision-making processes.</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🛠️ Tech Stack

<div align="center">
  <table>
    <tr>
      <td><b>AI & Modeling</b></td>
      <td>Llama 3.1 8B, Unsloth, QLoRA, GGUF</td>
    </tr>
    <tr>
      <td><b>Inference & Local Engine</b></td>
      <td>Ollama, CUDA Toolkit</td>
    </tr>
    <tr>
      <td><b>Data Pipeline & Vectors</b></td>
      <td>ChromaDB / FAISS, LangChain, Pandas</td>
    </tr>
    <tr>
      <td><b>Service Interface</b></td>
      <td>FastAPI / Flask (REST API), Python CLI</td>
    </tr>
  </table>
</div>

---

## 🗂️ Repository Structure

<details>
<summary>📂 Click to expand the directory tree</summary>

```text
├── .kaggle/                    # Kaggle API authentication credentials
├── data/
│   ├── raw/                    # Raw tabular data mass (.csv)
│   └── processed/              # Mapped instruction dataset (.jsonl)
├── src/
│   ├── data_engineering.py     # ETL and synthetic generation pipeline
│   ├── train.py                # Local Fine-Tuning routine (Unsloth)
│   ├── rag_pipeline.py         # Chunking, embeddings, and vector search
│   ├── api.py                  # REST HTTP Microservice
│   └── client_console.py       # Console interface for validation
├── docs/                       # Policy and regulation manuals in PDF
├── Modelfile                   # Ollama manifest configuration
└── requirements.txt            # Python ecosystem dependencies
