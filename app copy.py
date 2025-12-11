import streamlit as st
from groq import Groq
import json
import difflib

# -------------------------
# SETUP GROQ CLIENT
# -------------------------
API_KEY = ""   # <- PUT DIRECTLY HERE
client = Groq(api_key=API_KEY)

# -------------------------
# STREAMLIT UI SETUP
# -------------------------
st.title("🔥 AI-Powered Code Explainer (LLaMA 3 Small - Groq)")
st.write("Explain, optimize, compare diff, and analyze complexity.")

# Working models dropdown
model = st.selectbox("Select AI Model (Groq)", [
    "llama-3.1-8b-instant"
])

# Language dropdown
language = st.selectbox("Select Code Language", ["Python", "JavaScript"])

# Input code
code_input = st.text_area("Paste your code here:", height=250)

if st.button("Explain Code"):
    if not code_input.strip():
        st.warning("Please enter code!")
    else:

        # AI prompt
        prompt = f"""
        Explain this {language} code in simple English (3–4 sentences).
        Then provide a more optimized version.
        Then give precise time & space complexity (state assumptions; include per-operation + overall).

        Return STRICT JSON only:

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

        # AI Call
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        raw_output = response.choices[0].message.content.strip()

        # -------------------------
        # FIX INVALID JSON
        # -------------------------
        def safe_json_parse(output):
            try:
                return json.loads(output)
            except:
                # Attempt to extract JSON part only
                import re
                match = re.search(r'\{.*\}', output, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group())
                    except:
                        return None
                return None

        data = safe_json_parse(raw_output)

        if data is None:
            st.error("❌ AI returned invalid JSON. Raw output:")
            st.code(raw_output)
            st.stop()

        explanation = data.get("explanation", "")
        optimized_code = data.get("optimized_code", "")
        complexity = data.get("complexity", "")

        # -------------------------
        # 1. Show Explanation
        # -------------------------
        st.subheader("📘 Explanation (Simple English)")
        st.write(explanation)

        # -------------------------
        # 2. Optimized Code
        # -------------------------
        st.subheader("⚡ Optimized Code")
        st.code(optimized_code, language.lower())

        # -------------------------
        # 3. Diff View using diff-match-patch
        # -------------------------
        st.subheader("🆚 Diff View (Original → Optimized)")

        if optimized_code:
            st.subheader("Optimized Code")
            st.code(optimized_code, language.lower())

            # -------------------------
            # 3. DIFF VIEW
            # -------------------------
            diff = difflib.unified_diff(
                code_input.splitlines(),
                optimized_code.splitlines(),
                fromfile="Original",
                tofile="Optimized",
                lineterm=""
            )

            diff_output = "\n".join(list(diff))

            st.subheader("Diff View (Original → Optimized)")
            st.code(diff_output)


        # -------------------------
        # 4. Complexity
        # -------------------------
        st.subheader("📈 Time & Space Complexity (Estimated)")
        st.write(complexity)
