import pandas as pd
from google import genai  # <-- NEW 2026 SDK IMPORT
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
INPUT_PATH = 'data/scored_feedback_final.csv'
REPORT_OUTPUT_PATH = 'data/CX_Executive_Report.md'

def load_negative_feedback():
    """Extracts only the high-confidence negative comments for the report."""
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"❌ Input file {INPUT_PATH} not found. Run Phase 2 first.")
    
    df = pd.read_csv(INPUT_PATH)
    
    # Filter for Negative sentiment and drop empty comments
    negatives = df[df['predicted_sentiment'] == 'Negative'].dropna(subset=['clean_comment'])
    
    print(f"📊 Found {len(negatives)} negative comments.")
    
    # To save API tokens and time, we'll take the top 100 most relevant complaints
    sample_comments = negatives['clean_comment'].head(100).tolist()
    return sample_comments

def generate_executive_summary(comments_list):
    """Uses Google Gemini to synthesize unstructured text into strategic insights."""
    print("🤖 Connecting to Google Gemini API...")
    
    # Securely load API key from .env file
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ API Key missing. Please check your .env file.")
    
    # --- NEW SDK INITIALIZATION ---
    client = genai.Client(api_key=api_key)
    
    # --- PROMPT ENGINEERING ---
    prompt = f"""
    Act as a Senior Customer Experience (CX) Analyst for a major Canadian bank. 
    I will provide you with a list of recent negative client feedback.
    
    Your task is to analyze these comments and provide a structured executive summary for the Branch Management Team.
    
    Format the output EXACTLY like this using Markdown:
    ## 🚨 Top 3 Critical Pain Points
    [Identify the three most common issues across the feedback, using bullet points]
    
    ## 💡 Recommended Strategic Actions
    [Provide three actionable, operational recommendations to solve these pain points]
    
    ## 📝 Summary Context
    [A brief 2-sentence summary of the overall client mood]
    
    Here is the raw feedback data to analyze:
    {comments_list}
    """
    
    print("⏳ Synthesizing feedback into an executive report...")
    
    # --- NEW GENERATE CONTENT CALL ---
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Upgraded to the latest model version
        contents=prompt
    )
    
    return response.text

def run_reporting_phase():
    print("--- 📑 Starting Phase 3: Automated Executive Reporting ---")
    
    # 1. Load Data
    negative_comments = load_negative_feedback()
    
    if not negative_comments:
        print("✅ No negative comments found. No report needed.")
        return

    # 2. Generate Report via LLM
    report_content = generate_executive_summary(negative_comments)
    
    # 3. Save the Report
    with open(REPORT_OUTPUT_PATH, 'w') as f:
        f.write(report_content)
        
    print(f"✅ Success! Executive Report saved to: {REPORT_OUTPUT_PATH}")
    print("\n--- Report Preview ---")
    print(report_content)

if __name__ == "__main__":
    run_reporting_phase()