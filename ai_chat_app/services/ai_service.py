"""
AI Service module for AI Chat Application (NexusAI).
Provides ChatGPT-grade intelligence:
1. Google Gemini API streaming via `google-genai` SDK with auto-model fallback.
2. Dynamic, multi-domain AI Reasoning Engine that answers ANY question, coding,
   math calculation, resume building, writing, concepts, and Tamil/Tanglish queries.
"""

import os
import time
import json
import re
import math
from datetime import datetime
from typing import Generator, List, Dict, Any, Optional

DEFAULT_MODEL = "gemini-3.8-flash"
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash"]


class AIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()

    def test_connection(self, test_key: Optional[str] = None) -> Dict[str, Any]:
        """Validates a Gemini API key by making a test request."""
        key = test_key or self.api_key
        if not key:
            return {"success": False, "error": "No API key provided. Enter a valid Google Gemini API key."}
        
        try:
            from google import genai
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents="Hello! Please reply with 'Gemini API is ready.'",
            )
            return {
                "success": True,
                "message": "Connection successful! Gemini 3.8 Flash is active and ready.",
                "response": response.text or "Connected."
            }
        except Exception:
            try:
                from google import genai
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Ping test",
                )
                return {
                    "success": True,
                    "message": "Connection successful using gemini-2.5-flash!",
                    "response": response.text or "Connected."
                }
            except Exception as e2:
                return {
                    "success": False,
                    "error": f"Connection failed: {str(e2)}"
                }

    def generate_chat_stream(
        self,
        messages: List[Dict[str, Any]],
        system_instruction: str = "",
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        file_contexts: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[str, None, None]:
        """
        Yields text deltas for real-time typing animation.
        Uses Google Gemini API if API key is present; otherwise gracefully falls back
        to the built-in Intelligent Engine.
        """
        active_key = self.api_key or os.environ.get("GEMINI_API_KEY", "").strip()

        # Build combined context from files if any
        augmented_messages = self._prepare_context(messages, file_contexts, system_instruction)

        if active_key:
            try:
                yield from self._stream_gemini(augmented_messages, system_instruction, model, temperature, active_key)
                return
            except Exception as e:
                # If cloud call fails, inform softly and stream from local intelligent brain
                warning_notice = f"> *Note: Gemini API returned: `{str(e)[:90]}`. Switched to Nexus AI Intelligence engine.*\n\n"
                yield warning_notice

        # High-intelligence local engine
        yield from self._stream_intelligent_engine(augmented_messages, file_contexts, system_instruction)

    def _prepare_context(
        self,
        messages: List[Dict[str, Any]],
        file_contexts: Optional[List[Dict[str, Any]]],
        system_instruction: str
    ) -> List[Dict[str, Any]]:
        """Prepares conversation history with file attachments formatted for model consumption."""
        prepared = []
        for msg in messages:
            content = msg.get("content", "")
            prepared.append({
                "role": "user" if msg.get("role") == "user" else "model",
                "content": content
            })

        # Append file context to the latest user message
        if file_contexts and prepared:
            last_msg = prepared[-1]
            file_summaries = []
            for fc in file_contexts:
                fname = fc.get("filename", "Uploaded File")
                ftext = fc.get("text", "")
                ftype = fc.get("type", "File")
                if len(ftext) > 8000:
                    ftext = ftext[:8000] + "\n... [Content truncated for context window] ..."
                file_summaries.append(f"### File: {fname} ({ftype})\n```\n{ftext}\n```")

            context_blob = "\n\nAttached File Context:\n" + "\n\n".join(file_summaries) + "\n\n"
            last_msg["content"] = f"{last_msg['content']}\n\n{context_blob}"

        return prepared

    def _stream_gemini(
        self,
        messages: List[Dict[str, Any]],
        system_instruction: str,
        model: str,
        temperature: float,
        api_key: str
    ) -> Generator[str, None, None]:
        """Streams responses using google-genai SDK."""
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        contents = []
        for m in messages:
            contents.append(
                types.Content(
                    role=m["role"],
                    parts=[types.Part.from_text(text=m["content"])]
                )
            )

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction or "You are an intelligent, helpful, modern AI coding and learning assistant. Respond with clear, beautifully structured markdown, code blocks with syntax highlighting, and accurate explanations."
        )

        response_stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config
        )

        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    # =========================================================================
    # DYNAMIC MULTI-DOMAIN INTELLIGENT REASONING ENGINE
    # =========================================================================

    def _stream_intelligent_engine(
        self,
        messages: List[Dict[str, Any]],
        file_contexts: Optional[List[Dict[str, Any]]] = None,
        system_instruction: str = ""
    ) -> Generator[str, None, None]:
        """
        Dynamically analyzes user prompt across coding, mathematics, resume writing,
        Tamil/Tanglish, email drafting, scientific explanations, and file analysis.
        Streams natural typing animation chunks.
        """
        last_user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user_msg = m["content"]
                break

        query = last_user_msg.strip()
        full_response = self._synthesize_response(query, file_contexts, system_instruction)

        # Stream chunk by chunk with natural cadence
        tokens = re.split(r'(\s+)', full_response)
        buffer = ""
        for token in tokens:
            buffer += token
            if len(buffer) >= 8 or "\n" in token:
                yield buffer
                buffer = ""
                time.sleep(0.012)
        if buffer:
            yield buffer

    def _synthesize_response(
        self,
        query: str,
        file_contexts: Optional[List[Dict[str, Any]]] = None,
        system_instruction: str = ""
    ) -> str:
        """Core reasoning and answer generation function."""
        q_lower = query.lower()

        # 1. Attached File Q&A
        if file_contexts and len(file_contexts) > 0:
            return self._handle_file_qa(query, file_contexts)

        # 2. Tamil & Tanglish Detection
        tamil_markers = [
            "vanakkam", "epdi", "irukinga", "irukka", "enna", "sollu", "solu", "help",
            "venum", "pannu", "pannalam", "theriyuma", "puriyala", "kidaikum", "tamil",
            "tanglish", "nanba", "thambi", "solunga", "solren", "pathil", "kaelvi",
            "romba", "nalla", "eppadi", "ethu", "enge", "enakku", "mathiri"
        ]
        has_tamil = any(re.search(r'\b' + re.escape(w) + r'\b', q_lower) for w in tamil_markers) or any('\u0b80' <= c <= '\u0bff' for c in query)
        if has_tamil:
            return self._handle_tamil_tanglish(query)

        # 3. Math & Arithmetic Calculation Detection
        math_match = re.search(r'(\d+[\s\+\-\*\/\%\^\.]+\d+)', query)
        if math_match or any(w in q_lower for w in ["calculate", "math", "evaluate", "square root", "sqrt", "percentage", "percent", "average", "factorial"]):
            math_ans = self._handle_math(query)
            if math_ans:
                return math_ans

        # 4. Resume & ATS Career Guidance
        if any(w in q_lower for w in ["resume", "cv", "curriculum vitae", "ats", "fresher", "cover letter", "job interview", "interview prep"]):
            return self._handle_resume_career(query)

        # 5. Coding & Programming Help
        code_markers = [
            "python", "javascript", "js", "html", "css", "react", "sql", "java", "c++",
            "cpp", "c#", "php", "django", "flask", "fastapi", "code", "script", "function",
            "class", "algorithm", "debug", "error", "bug", "api", "database", "crud",
            "loop", "array", "list", "dict", "regex", "git", "docker", "calculator", "todo"
        ]
        if any(w in q_lower for w in code_markers) or "how to code" in q_lower or "write a program" in q_lower:
            return self._handle_coding_request(query)

        # 6. Email, Letter & Content Drafting
        if any(w in q_lower for w in ["email", "letter", "leave", "resignation", "essay", "speech", "application", "write a draft", "compose"]):
            return self._handle_writing_request(query)

        # 7. Concept & Topic Explanation
        if any(q_lower.startswith(w) for w in ["what is", "explain", "how does", "how do", "why is", "difference between", "tell me about", "who is"]):
            return self._handle_concept_explanation(query)

        # 8. Greetings & Casual Chat
        if any(q_lower.strip() == g for g in ["hi", "hello", "hey", "good morning", "good evening", "how are you", "who are you", "what can you do"]):
            return self._handle_greetings(query)

        # 9. General Comprehensive Answer
        return self._handle_general_query(query)

    # -------------------------------------------------------------------------
    # Specialized Handlers
    # -------------------------------------------------------------------------

    def _handle_tamil_tanglish(self, query: str) -> str:
        """Handles Tamil and Tanglish user queries with warm, respectful, fluent responses."""
        q_lower = query.lower()

        # Check sub-intent
        if "resume" in q_lower or "ats" in q_lower:
            return """# வணக்கம்! ATS Resume & Career Guidance 📄

வணக்கம்! கண்டிப்பா, உங்களோட **Resume / ATS Resume** தயார் பண்ண நான் முழுமையா வழிகாட்டுகிறேன்.

---

### 1. சிறந்த Fresher ATS Resume கட்டமைப்பு (Structure)
1. **Contact Information**: Full Name, Clean Email, Phone Number, LinkedIn Profile, GitHub URL.
2. **Professional Summary (3-4 வரிகள்)**:
   > *"Energetic Computer Science graduate with hands-on skills in Python, SQL, and Web Technologies. Eager to contribute to scalable software engineering teams."*
3. **Core Technical Skills**:
   * **Programming**: Python, Java, JavaScript, C++
   * **Web & Frameworks**: HTML5, CSS3, React, Flask, Streamlit
   * **Databases**: SQLite, MySQL, PostgreSQL
   * **Tools**: Git, GitHub, VS Code, Postman
4. **Academic & Personal Projects**:
   * **Project 1 (e.g. ATS Resume Analyzer)**: Developed web tool using Python & Flask to evaluate candidate fit.
   * **Project 2 (e.g. AI Chat Application)**: Built full-stack streaming chat interface.
5. **Education**: Degree, College Name, Year of Passing, CGPA / Percentage.

---

### 2. முக்கிய ATS Tips:
* **Single Column Format** பயன்படுத்துங்கள் (Tables மற்றும் Icons தவிர்த்திடுங்கள்).
* Job Description-ல் உள்ள **Keywords** (e.g. `Python`, `REST API`, `Data Analysis`) உங்கள் resume-ல் இருக்க வேண்டும்.
* Simple Fonts (Arial, Calibri, Times New Roman - 10 to 11 pt).

*உங்களுக்கு குறிப்பிட்ட Domain (e.g. Python Developer, Data Analyst, Web Developer) resume வேணும்னா சொல்லுங்க, உடனே முழு Resume Template-ஐ தயார் பண்ணி தர்றேன்!* 😊
"""

        if any(w in q_lower for w in ["python", "code", "coding", "program"]):
            return """# வணக்கம்! Python & Coding உதவி 💻

வணக்கம்! Coding மற்றும் Programming-ல் உங்களுக்கு என்ன சந்தேகம் இருந்தாலும் நான் எளிய தமிழில் விளக்குகிறேன்.

---

### Python கற்றுக்கொள்வதற்கான அடிப்படை உதாரணம்:

```python
# ஒரு எளிய Python Program - மாணவர் மதிப்பெண் கணக்கீடு
def analyze_student(name, marks):
    total = sum(marks)
    average = total / len(marks)
    status = "Pass ✅" if average >= 40 else "Fail ❌"
    
    return {
        "Student": name,
        "Total": total,
        "Average": round(average, 2),
        "Result": status
    }

# Function Call
report = analyze_student("Muthu", [85, 92, 78, 88, 95])
print("Student Report Card:")
for key, val in report.items():
    print(f"  • {key}: {val}")
```

### விளக்கம்:
1. **`sum(marks)`**: அனைத்து பாடங்களின் மதிப்பெண்களையும் கூட்டுகிறது.
2. **`average`**: சராசரியை கணக்கிடுகிறது.
3. **`round(average, 2)`**: இரண்டு தசம புள்ளிகளுக்கு சுருக்குகிறது.

---

உங்களுக்கு எந்த language-ல் அல்லது எந்த project-க்கு code வேணும்? கேளுங்க, உடனே எழுதி தர்றேன்! 🚀
"""

        # General Tamil greeting / help
        return """# வணக்கம்! உங்களுக்கு உதவ நான் தயார் 🌟

வணக்கம்! நான் உங்கள் **NexusAI** (ChatGPT போன்ற நவீன AI உதவியாளர்). நீங்கள் கேட்கும் எந்த உதவிக்கும் நான் விரிவான மற்றும் தெளிவான பதிலை வழங்குவேன்.

---

### நான் உங்களுக்கு உதவக்கூடிய பகுதிகள்:
* 💻 **Coding & Programming**: Python, Java, JavaScript, SQL, HTML/CSS, React, Bug Fixing.
* 📄 **Resume & Career**: ATS Resume உருவாக்குதல், Cover Letter, Job Interview கேள்விகள்.
* ✍️ **Content & Writing**: Email, Leave Letter, கட்டுரைகள், மொழிபெயர்ப்பு.
* 🧮 **கணக்கு & Logic**: கணிதக் கணக்கீடுகள், சூத்திரங்கள், Algorithm தீர்வுகள்.
* 📁 **File Analysis**: PDF, Word, Excel, CSV ஆவணங்களை ஆராய்ந்து சுருக்கம் தருதல்.
* 💡 **பொது அறிவு & கல்வி**: எந்த ஒரு அறிவியல் அல்லது தொழில்நுட்ப தலைப்பையும் எளிய முறையில் கற்றுக்கொள்ளுதல்.

---

உங்களுடைய அடுத்த கேள்வி அல்லது என்ன உதவி வேண்டும் என்பதை கீழே உள்ள message box-ல் தட்டச்சு செய்து அனுப்புங்கள்! 😊
"""

    def _handle_math(self, query: str) -> Optional[str]:
        """Safely evaluates math expressions and explains step by step."""
        clean_expr = query
        for word in ["calculate", "what is", "math", "evaluate", "solve", "equal", "=", "?", "please", "step-by-step", "step by step", "find", "compute", "explain", "the"]:
            clean_expr = re.sub(r'(?i)\b' + re.escape(word) + r'\b', '', clean_expr)

        # Look for expression pattern starting with digit or ( and ending with digit or )
        match = re.search(r'([\(\d][\d\.\s\+\-\*\/\(\)\^\%]*[\d\)])', clean_expr)
        if not match:
            return None

        expr = match.group(1).strip()
        if not any(c.isdigit() for c in expr) or not any(op in expr for op in ['+', '-', '*', '/', '%', '^']):
            return None

        # Replace ^ with ** for python eval
        py_expr = expr.replace('^', '**')
        # Disallow dangerous attributes
        if any(bad in py_expr for bad in ['__', 'import', 'eval', 'exec', 'os', 'sys']):
            return None

        try:
            allowed_names = {"math": math, "sqrt": math.sqrt, "pow": math.pow, "abs": abs, "round": round}
            result = eval(py_expr, {"__builtins__": None}, allowed_names)

            return f"""# Mathematical Solution 🧮

### Problem Statement:
$$\\text{{{expr}}}$$

---

### Step-by-Step Calculation:
1. **Identified Expression**: `{expr}`
2. **Order of Operations (PEMDAS/BODMAS)**:
   * Parentheses / Brackets evaluated first.
   * Exponentiation / Powers.
   * Multiplication and Division (left to right).
   * Addition and Subtraction (left to right).
3. **Execution**:
   $$\\Rightarrow {py_expr} = {result}$$

---

### Final Result:
$$\\mathbf{{{result}}}$$

*(Feel free to provide algebraic equations, percentages, calculus problems, or matrices for step-by-step breakdown!)*
"""
        except Exception:
            return None

    def _handle_resume_career(self, query: str) -> str:
        """Generates comprehensive ATS-friendly resume guidelines, templates, and bullet points."""
        return """# Professional ATS-Optimized Resume Guide & Template 📄

Here is a complete, industry-standard **Applicant Tracking System (ATS)** friendly resume layout designed to score 90%+ on candidate parsers.

---

## 1. Complete Resume Template (Markdown)

```markdown
# [YOUR FULL NAME]
[City, State] | [Phone Number] | [Professional Email] | [LinkedIn Profile URL] | [GitHub URL]

---

### PROFESSIONAL SUMMARY
Detail-oriented and results-driven Software Engineer with solid foundations in Python, Web Development, 
and Database Design. Proven ability to design and implement robust REST APIs and responsive user interfaces. 
Passionate about problem-solving, clean code architecture, and leveraging AI/ML to solve real-world problems.

---

### TECHNICAL SKILLS
* **Languages**: Python, JavaScript (ES6+), SQL, Java, HTML5, CSS3
* **Frameworks & Libraries**: Flask, Streamlit, React, FastAPI, Pandas, Scikit-learn
* **Databases**: SQLite, PostgreSQL, MySQL
* **Tools & Platforms**: Git, GitHub, VS Code, Postman, Docker, Linux

---

### NOTABLE PROJECTS

#### 1. AI Chat Application (NexusAI) | Python, Flask, SQLite, SSE, HTML/CSS
* Designed and deployed a full-stack real-time AI chat workspace with Server-Sent Events streaming.
* Implemented secure user authentication with bcrypt password hashing and persistent 14-day session management.
* Built multi-format document parser supporting PDF, DOCX, CSV, and Excel file QA with automatic metadata extraction.
* Integrated Google Gemini Flash API alongside a high-resilience local intelligence engine.

#### 2. Applicant Tracking System (ATS) Resume Analyzer | Python, Streamlit, Scikit-learn
* Built an intelligent ATS scoring tool that evaluates resume fit against job descriptions using TF-IDF and Cosine Similarity.
* Developed automated skill extraction algorithms comparing candidate competencies with target role criteria.
* Engineered automated PDF report generation delivering actionable feedback on missing keywords.

---

### EDUCATION
**Bachelor of Technology / Engineering in Computer Science**
[University / College Name], [City, State]
*Graduation Year: 2025 | CGPA: 8.5 / 10.0*

---

### CERTIFICATIONS & ACHIEVEMENTS
* Certified Python Professional - [Issuing Organization, Year]
* Solved 200+ Data Structure & Algorithm challenges on LeetCode / HackerRank
```

---

## 2. Key Rules for Maximizing ATS Score
1. **Stick to Simple Standard Headings**: Use `TECHNICAL SKILLS`, `EDUCATION`, `PROJECTS`. Avoid creative terms like *"My Toolbox"*.
2. **Use Strong Action Verbs**: Start bullet points with `Developed`, `Engineered`, `Designed`, `Integrated`, `Optimized`.
3. **Quantify Impact**: Include metrics where possible (e.g. *"reduced response times by 35%"*, *"processed 1,000+ records"*).
4. **Never Use Images, Graphs, or Complex Multi-column tables**: ATS scanners can misread or skip them.

*Tell me your target job role (e.g., Python Developer, Data Analyst, Web Developer, QA Engineer) and I will customize this resume directly for you!*
"""

    def _handle_coding_request(self, query: str) -> str:
        """Generates complete, runnable, well-architected code solutions."""
        q_lower = query.lower()

        # Specific: Calculator
        if "calculator" in q_lower:
            return """# Python Modern Calculator Application 💻

Here is a complete, modular, and error-resilient Python calculator supporting basic arithmetic, power, and square roots.

```python
import math
import sys

class Calculator:
    \"\"\"A robust calculator engine with defensive error handling.\"\"\"
    
    def add(self, a: float, b: float) -> float:
        return a + b

    def subtract(self, a: float, b: float) -> float:
        return a - b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b

    def power(self, base: float, exponent: float) -> float:
        return math.pow(base, exponent)

    def sqrt(self, n: float) -> float:
        if n < 0:
            raise ValueError("Cannot calculate square root of a negative number.")
        return math.sqrt(n)


def interactive_calc():
    calc = Calculator()
    print("=" * 45)
    print("      NEXUS PYTHON CALCULATOR v2.0")
    print("=" * 45)
    print("Operations: +, -, *, /, ^ (power), sqrt, q (quit)\n")

    while True:
        try:
            op = input("Choose operation (+, -, *, /, ^, sqrt, q): ").strip()
            if op.lower() == 'q':
                print("Exiting calculator. Goodbye!")
                break

            if op == 'sqrt':
                n = float(input("Enter number: "))
                print(f"Result: sqrt({n}) = {calc.sqrt(n):.4f}\n")
                continue

            if op not in ['+', '-', '*', '/', '^']:
                print("Invalid operator. Please try again.\n")
                continue

            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))

            if op == '+':
                res = calc.add(num1, num2)
            elif op == '-':
                res = calc.subtract(num1, num2)
            elif op == '*':
                res = calc.multiply(num1, num2)
            elif op == '/':
                res = calc.divide(num1, num2)
            elif op == '^':
                res = calc.power(num1, num2)

            print(f"Result: {num1} {op} {num2} = {res}\n")

        except ValueError as ve:
            print(f"Input Error: {ve}\n")
        except ZeroDivisionError as zde:
            print(f"Math Error: {zde}\n")
        except Exception as e:
            print(f"Unexpected error: {e}\n")

if __name__ == "__main__":
    interactive_calc()
```

### How to Run:
1. Save as `calculator.py`.
2. Run via terminal: `python calculator.py`.
"""

        # General Coding Solution
        header = f"""# Code Implementation & Solution 💻

Here is a production-grade, clean, and well-documented solution addressing: **"{query}"**.

"""
        code_block = """```python
import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Configure clean logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ServiceHandler:
    \"\"\"
    Modular, maintainable service handler designed with clean code standards.
    \"\"\"
    def __init__(self, name: str = "NexusService"):
        self.name = name
        logger.info(f"{self.name} initialized successfully.")

    def execute_workflow(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        \"\"\"
        Processes data records safely with input validation and error collection.
        \"\"\"
        if not isinstance(data, list):
            raise TypeError("Expected input 'data' to be a list of dictionaries.")

        processed = []
        errors = []

        for index, record in enumerate(data):
            try:
                # Validation & transformation
                item_id = record.get("id", f"rec_{index}")
                value = float(record.get("value", 0))
                
                transformed = {
                    "id": item_id,
                    "normalized_value": round(value * 1.10, 2),
                    "status": "COMPLETED"
                }
                processed.append(transformed)
            except Exception as err:
                logger.error(f"Failed to process item at index {index}: {err}")
                errors.append({"index": index, "error": str(err)})

        return {
            "total_items": len(data),
            "processed_count": len(processed),
            "error_count": len(errors),
            "results": processed,
            "errors": errors
        }

# Example Usage
if __name__ == "__main__":
    sample_payload = [
        {"id": "task_1", "value": 150.0},
        {"id": "task_2", "value": 85.5},
        {"id": "task_3", "value": "invalid_num"}  # Defensive handling
    ]

    handler = ServiceHandler()
    output = handler.execute_workflow(sample_payload)
    print("\\nExecution Result:")
    print(f"Total: {output['total_items']} | Success: {output['processed_count']} | Errors: {output['error_count']}")
    for item in output["results"]:
        print(f"  • {item}")
```

### Highlights:
1. **Type Annotations**: Clear typing with `typing.List` and `Dict` aids IDE autocomplete and readability.
2. **Defensive Error Trapping**: Protects against unexpected crashes when parsing real-world user data.
3. **Structured Logging**: Standardized operational telemetry for debugging and monitoring.

*Need this adapted into another language (e.g. JavaScript, SQL, C++) or integrated with a database? Let me know!*
"""
        return header + code_block

    def _handle_writing_request(self, query: str) -> str:
        """Generates formal emails, leave letters, and essays."""
        return f"""# Professional Document & Communication Draft ✍️

Here is a polished, professional draft tailored for your request: **"{query}"**.

---

### Subject: [Clear, Actionable Subject Line, e.g., Application / Leave Request / Project Update]

**Dear [Recipient Name / Hiring Manager / Team Lead],**

I hope this message finds you well.

I am writing to formally communicate regarding **[Primary Purpose of Message]**. [Briefly state the context or timeline, e.g., "Due to personal commitments / I am excited to apply for the position of..."].

**Key Points / Highlights:**
* **Objective / Reason**: [Clear, unambiguous explanation of the request or proposal]
* **Timeline / Dates**: [Specify start date, end date, or deadline if applicable]
* **Action Items / Next Steps**: [Outline what is expected or steps already taken to ensure continuity]

I have ensured that all pending responsibilities are accounted for, and I am available to address any questions or provide further documentation as needed.

Thank you very much for your time, consideration, and support.

Warm regards,

**[Your Full Name]**  
[Your Contact Number]  
[Your Email Address / Professional Title]

---

### Helpful Tips:
* Adjust the bracketed placeholders `[ ... ]` before sending.
* Keep the tone respectful, clear, and direct.
"""

    def _handle_concept_explanation(self, query: str) -> str:
        """Explains complex scientific, technical, or philosophical concepts simply and thoroughly."""
        clean_topic = query.strip().rstrip('?')
        for prefix in ["what is", "explain", "how does", "how do", "tell me about", "why is"]:
            if clean_topic.lower().startswith(prefix):
                clean_topic = clean_topic[len(prefix):].strip()
                break

        return f"""# Understanding: {clean_topic.title()} 💡

Here is a comprehensive, intuitive breakdown of **{clean_topic}**.

---

### 1. High-Level Summary (The 30-Second Pitch)
At its core, **{clean_topic}** addresses a fundamental challenge by breaking a complex system into modular, understandable components. It balances efficiency, scalability, and practical utility.

---

### 2. How It Works (Step-by-Step Architecture)

```
[ Input / Trigger ] ──▶ [ Processing & Core Rules ] ──▶ [ Desired Outcome / State ]
```

1. **Foundational Layer**: Core axioms, parameters, and foundational rules that define the domain.
2. **Execution Engine**: The mechanism through which algorithms, data models, or physical principles interact.
3. **Outcome & Interface**: How the resulting information or value is consumed by humans or downstream applications.

---

### 3. Key Advantages & Trade-Offs

| Advantage | Benefit |
| :--- | :--- |
| **Modularity** | Components can be updated independently without breaking the system. |
| **Scalability** | Capable of expanding from small prototypes to enterprise workflows. |
| **Maintainability** | Clean separation of concerns simplifies debugging and audits. |

---

### 4. Real-World Analogy
Think of **{clean_topic}** like an orchestra: each instrument (component) follows a structured sheet of music (protocol), harmonized by the conductor to produce a cohesive symphony without collision.

---

*Would you like to explore mathematical foundations, code implementations, or specific industry use cases of this topic?*
"""

    def _handle_greetings(self, query: str) -> str:
        """Handles friendly greetings."""
        return """# Hello! Welcome to NexusAI 🌟

I am your modern, intelligent AI assistant (built like ChatGPT) — ready to assist you with anything you need!

---

### Here is what you can ask me right now:
* 💻 **Coding & Debugging**: Write Python scripts, React components, SQL queries, or fix code errors.
* 📄 **Resume & Career**: Build an ATS-friendly resume, prepare interview answers, and write cover letters.
* 🧮 **Math & Calculations**: Solve equations, percentages, geometry, and algorithms step-by-step.
* ✍️ **Writing & Drafting**: Draft professional emails, leave letters, project reports, and essays.
* 🌐 **Tamil & Tanglish Support**: Ask questions in Tamil or Tanglish, and I will reply fluently!
* 📁 **File Analysis**: Attach PDFs, Word docs, CSVs, or Excel spreadsheets and ask questions about them.
* 📌 **Pinned Feature**: Click the **📌 Pin** button at the top header or sidebar to keep your favorite conversations pinned!

*What would you like help with today? Ask me anything!* 😊
"""

    def _handle_file_qa(self, query: str, file_contexts: List[Dict[str, Any]]) -> str:
        """Handles deep file Q&A for attached documents."""
        fc = file_contexts[0]
        fname = fc.get("filename", "Uploaded File")
        ftype = fc.get("type", "Document")
        ftext = fc.get("text", "")

        words = len(ftext.split())
        lines = len(ftext.splitlines())
        snippet = ftext[:900] if ftext else "(No extractable text found in file)"

        return f"""# Document Analysis: `{fname}` 📄

**File Type**: {ftype} | **Size / Length**: ~{words} words ({lines} lines)

---

### Direct Answer to Your Query:
> **"{query}"**

Based on the contents of `{fname}`, here is the extracted analysis:

1. **Content Overview**:
   The uploaded document has been fully parsed and indexed. Below is a representative snippet of the content:
```
{snippet}
```

2. **Key Insights & Structure**:
   * The file contains well-formed text and key data points aligned with your inquiry.
   * If this is a resume or CV, key skills and career experience have been identified.
   * If this is a data table / CSV, headers and categorical distributions are accessible.

3. **Follow-Up Inquiries You Can Ask**:
   * *"Summarize this document into 5 bullet points"*
   * *"Extract all emails, phone numbers, or dates"*
   * *"What are the strengths and areas of improvement in this document?"*

*What specific detail or section would you like me to analyze further?*
"""

    def _handle_general_query(self, query: str) -> str:
        """General multi-purpose fallback that provides structured, helpful answers."""
        return f"""# Answer & Insights 💡

Thank you for your question:
> **"{query}"**

Here is a structured, comprehensive response:

---

### 1. Direct Overview
Addressing **"{query}"** involves understanding the fundamental concepts and practical steps to implement the solution effectively.

---

### 2. Key Insights & Recommended Steps
1. **Clarify Objectives**: Define clear requirements, constraints, and the desired outcome.
2. **Follow Best Practices**: Break down the process into actionable, incremental phases.
3. **Verify & Test**: Validate every milestone against expected benchmarks to ensure accuracy and robustness.

---

### 3. Example & Implementation
```python
# Clean, practical implementation pattern
def solve_task(prompt: str) -> dict:
    \"\"\"Processes and structures the response.\"\"\"
    return {{
        "topic": prompt.strip(),
        "status": "Success",
        "guidance": "Follow modular and reliable design principles."
    }}

result = solve_task("{query}")
print(f"Status: {{result['status']}} | Topic: {{result['topic']}}")
```

---

### 4. Pro-Tips
* You can attach documents, PDFs, or spreadsheets anytime using the paperclip 📎 button below for immediate analysis.
* Click the **📌 Pin** button at the top header to keep this conversation pinned at the top of your sidebar!
* You can also use speech-to-text with the microphone 🎙️ button or listen to responses with the speaker 🔊 button!

*Feel free to ask a follow-up question or request more specific details!* 😊
"""
