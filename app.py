import streamlit as st
from groq import Groq
import json
import difflib
import ast
import re
from dotenv import load_dotenv
import os

# -------------------------
# SAFE API KEY
# -------------------------
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

st.title("AI-Powered Code Explainer")

# -------------------------
# SESSION HISTORY
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------
# PYTHON AST ANALYSIS
# -------------------------
def analyze_python_ast(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return {}

    result = {"functions": [], "loops": [], "conditions": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result["functions"].append(node.name)
        elif isinstance(node, (ast.For, ast.While)):
            result["loops"].append(f"Loop at line: {node.lineno}")
        elif isinstance(node, ast.If):
            result["conditions"].append(f"If at line: {node.lineno}")

    return result

# -------------------------
# JS ANALYSIS
# -------------------------
def analyze_js(code):
    funcs = re.findall(r"(?:function\s+([A-Za-z0-9_]+))|([A-Za-z0-9_]+)\s*=\s*\(", code)
    funcs_clean = [f[0] or f[1] for f in funcs]
    return {"functions": funcs_clean}

# -------------------------
# SAFE JSON PARSER
# -------------------------
def safe_parse(output):
    try:
        return json.loads(output)
    except:
        pass

    stack = []
    blocks = []
    start = None

    for i, ch in enumerate(output):
        if ch == "{":
            if not stack:
                start = i
            stack.append("{")
        elif ch == "}":
            if stack:
                stack.pop()
                if not stack and start is not None:
                    blocks.append(output[start:i+1])
                    start = None

    for block in reversed(blocks):
        try:
            return json.loads(block)
        except:
            continue

    repaired = (
        output.replace("“", "\"")
              .replace("”", "\"")
              .replace("'", "\"")
    )

    try:
        return json.loads(repaired)
    except:
        return None

# -------------------------
# UI INPUT
# -------------------------
language = st.selectbox("Language", ["Python", "JavaScript"])
code_input = st.text_area("Paste your code", height=250)

if st.button("Explain Code"):
    if not code_input.strip():
        st.warning("Please enter some code.")
        st.stop()

    highlights = analyze_python_ast(code_input) if language == "Python" else analyze_js(code_input)

    prompt = f"""
You must return ONLY valid JSON.

Explain this {language} code in 2–4 sentences.
Provide an optimized version.
Provide time & space complexity.

Return STRICT JSON:
{{
 "explanation": "...",
 "optimized_code": "...",
 "complexity": {{
     "time": "...",
     "space": "..."
 }}
}}
CODE:
{code_input}
"""

    # -------------------------
    # GROQ API CALL WITH ERROR HANDLING
    # -------------------------
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        raw = resp.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"Groq API Error: {e}")
        st.stop()

    parsed = safe_parse(raw)

    if parsed is None:
        st.error("AI returned invalid JSON")
        st.code(raw)
        st.stop()

    st.session_state.history.insert(0, {
        "code": code_input,
        "lang": language,
        "highlights": highlights,
        "result": parsed
    })

# -------------------------
# DISPLAY RESULTS
# -------------------------
st.subheader("Results History")

if not st.session_state.history:
    st.info("No results yet.")
else:
    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"History Item #{idx+1} — {item['lang']} Code", expanded=False):

            # --- Code Section ---
            st.markdown("Original Code")
            st.code(item["code"], language=item["lang"].lower())

            # --- Static Analysis --- 
            st.markdown("Static Highlights")
            st.json(item["highlights"])

            result = item["result"]

            tab1, tab2, tab3, tab4 = st.tabs(
                ["Explanation", "Optimized Code", "Diff View", "Complexity"]
            )

            with tab1:
                st.markdown("Explanation")
                st.write(result["explanation"])

            with tab2:
                st.markdown("Optimized Code")
                st.code(result["optimized_code"], language=item["lang"].lower())

            with tab3:
                st.markdown("Difference (Original → Optimized)")
                diff = difflib.unified_diff(
                    item["code"].splitlines(),
                    result["optimized_code"].splitlines(),
                    fromfile="Original",
                    tofile="Optimized",
                    lineterm=""
                )
                diff_output = "\n".join(diff)
                st.code(diff_output if diff_output.strip() else "No changes")

            with tab4:
                st.markdown("Time & Space Complexity")
                st.json(result["complexity"])
