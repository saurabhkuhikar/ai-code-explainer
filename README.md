# 🤖 AI Code Explainer (Python + JavaScript)

This project is an interactive Streamlit-based AI code explainer that analyzes Python and JavaScript code, provides optimized versions, and computes time/space complexity using Groq LLaMA models.

---

## 🚀 Features
- Code explanation (Python + JavaScript)
- Automatic optimization suggestions
- Time & space complexity generation
- Static code analysis using AST + Regex
- Diff view of original vs optimized code
- Full history panel with collapsible items

---

## 🧠 System Architecture

The application follows a modular architecture consisting of:

1. **Frontend (Streamlit UI)**  
   Displays inputs, results, history, diffs, and explanations in a clean interface.

2. **Static Code Analysis Layer**  
   - Python AST for detecting functions, loops, conditions  
   - Regex for analyzing JavaScript functions  

3. **AI Processing Layer (Groq LLaMA Models)**  
   The user’s code and metadata are sent to a Groq LLaMA model, which returns:
   - Explanation  
   - Optimized code  
   - Time & space complexity in strict JSON  

4. **Data Rendering Layer**  
   Results are parsed safely using a custom JSON recovery parser and displayed via Streamlit.

---

## 🤖 AI Model Selection

Groq’s **LLaMA 3.1 8B Instant** model was chosen due to:
- Extremely low inference latency  
- High reasoning ability for code explanation  
- Strongly structured output reliability  
- Ideal for real-time interactive applications  

It provides the best combination of **speed + accuracy** for this use case.

---

## ▶️ Running the App

1. Install dependencies:
```bash
pip install -r requirements.txt
