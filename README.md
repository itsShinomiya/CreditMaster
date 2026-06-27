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

## 📋 Visão Geral

O **CreditMaster** é um microsserviço *headless* de Inteligência Artificial Generativa voltado para o setor bancário. O objetivo principal é a automação do fluxo de análise de risco e a geração automatizada de pareceres técnicos de crédito. 

A solução adota uma abordagem de execução **100% on-premise (local)**, mitigando riscos de conformidade com a LGPD e garantindo o sigilo bancário absoluto ao eliminar a necessidade de tráfego de dados para APIs proprietárias em nuvem.

---

## 🏗️ Arquitetura Híbrida

O núcleo do sistema opera através de uma composição de duas técnicas avançadas de engenharia de prompt e IA:

<table align="center" width="100%">
  <tr>
    <td width="50%" valign="top">
      <h3>🎯 Fine-Tuning (QLoRA)</h3>
      <p>Modificação estrutural dos pesos neurais do modelo base <strong>Llama 3.1 8B Instruct</strong> via biblioteca <strong>Unsloth</strong>.</p>
      <ul>
        <li>Internalização do jargão técnico bancário.</li>
        <li>Padronização do formato sintático dos pareceres.</li>
        <li>Otimização extrema para execução local.</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h3>📚 RAG (Retrieval-Augmented Generation)</h3>
      <p>Injeção dinâmica de contexto factual e normativo em tempo real através de um banco vetorial local.</p>
      <ul>
        <li>Consulta a manuais internos de crédito e resoluções do BACEN.</li>
        <li>Eliminação drástica de alucinações matemáticas ou normativas.</li>
        <li>Rastreabilidade vacinal das tomadas de decisão.</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🛠️ Stack Tecnológico

<div align="center">
  <table>
    <tr>
      <td><b>IA & Modelagem</b></td>
      <td>Llama 3.1 8B, Unsloth, QLoRA, GGUF</td>
    </tr>
    <tr>
      <td><b>Inferência & Motor Local</b></td>
      <td>Ollama, CUDA Toolkit</td>
    </tr>
    <tr>
      <td><b>Pipeline de Dados & Vetores</b></td>
      <td>ChromaDB / FAISS, LangChain, Pandas</td>
    </tr>
    <tr>
      <td><b>Interface de Serviço</b></td>
      <td>FastAPI / Flask (REST API), Python CLI</td>
    </tr>
  </table>
</div>

---

## 🗂️ Organização do Repositório

<details>
<summary>📂 Clique para expandir a árvore de diretórios</summary>

```text
├── .kaggle/                    # Credenciais de autenticação da API Kaggle
├── data/
│   ├── raw/                    # Massa de dados tabular bruta (.csv)
│   └── processed/              # Dataset de instruções mapeado (.jsonl)
├── src/
│   ├── data_engineering.py     # ETL e pipeline de geração sintética
│   ├── train.py                # Rotina de Fine-Tuning local (Unsloth)
│   ├── rag_pipeline.py         # Chunking, embeddings e busca vetorial
│   ├── api.py                  # Microsserviço HTTP REST
│   └── client_console.py       # Console de interface para validação
├── docs/                       # Manuais de políticas e regulação em PDF
├── Modelfile                   # Configuração de manifesto do Ollama
└── requirements.txt            # Dependências do ecossistema Python
