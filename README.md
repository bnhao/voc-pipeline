# 📊 Customer Feedback Intelligence Pipeline (VoC)

**Author:** Mark Bui | Software Development, SAIT  
**Tech Stack:** Python, SQLite/MS SQL, Hugging Face (BERT), Google GenAI, Pandas

## 🚀 Project Overview

Financial institutions receive thousands of unstructured survey comments daily. This project automates the transition from "reading comments" to "taking strategic action." It is an end-to-end Voice of Client (VoC) pipeline that extracts raw feedback from a SQL database, evaluates the sentiment using a Natural Language Processing (NLP) model, and uses Generative AI to author an actionable executive strategy report.

## 🏗️ Architecture & Workflow

1. **Data Ingestion & Cleaning:** Extracts over 5,000 rows of simulated client feedback from a SQL database. Utilizes Pandas and Regex to aggressively normalize `NaN` values, HTML tags, and special characters, ensuring a high-quality data foundation.
2. **Intelligence Layer (BERT):** Leverages the `twitter-roberta-base-sentiment` transformer model to classify text into Positive, Negative, or Neutral categories, processing the data in efficient batches.
3. **Benchmarking Metrics:** Calculates the **F1 Score** to rigorously balance precision and recall, ensuring the model's reliability before any business decisions are made.
4. **Automated Reporting (Gemini):** Filters high-confidence negative feedback and passes it to the `gemini-2.5-flash` LLM. Uses strict prompt engineering to generate a structured Markdown report highlighting the top 3 critical pain points for branch management.

## 🛠️ Installation & Setup

```bash
# Clone the repository
git clone [https://github.com/bnhao/ATB_VoC_Pipeline.git](https://github.com/bnhao/ATB_VoC_Pipeline.git)

# Navigate into the directory
cd ATB_VoC_Pipeline

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install pandas sqlalchemy pyodbc transformers torch scikit-learn google-genai python-dotenv
```
