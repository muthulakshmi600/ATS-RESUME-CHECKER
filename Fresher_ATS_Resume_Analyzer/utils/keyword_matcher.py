"""
Keyword Matcher & Extraction Engine for Fresher ATS Resume Analyzer.
Extracts significant technical keywords and domain terminology from the Job Description,
ignores non-informative stopwords, and matches them against resume content.
"""

import re

# Comprehensive list of standard English stopwords to eliminate from JD keywords
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "responsibilities", "requirements", "candidate",
    "role", "job", "position", "experience", "looking", "ability", "work",
    "skills", "strong", "knowledge", "working", "team", "years", "plus", "must",
    "required", "preferred", "including", "across", "environment", "solutions"
}

# Domain technical terms and phrases commonly found in IT & fresher job descriptions
KNOWN_TECHNICAL_KEYWORDS = [
    # Languages & Core
    "python", "java", "c++", "c#", "c", "javascript", "typescript", "php", "ruby", "go", "rust", "r", "swift", "kotlin",
    # Web & Frameworks
    "html", "html5", "css", "css3", "react", "react.js", "angular", "vue", "vue.js", "node.js", "node", "express",
    "flask", "django", "fastapi", "spring", "spring boot", "bootstrap", "tailwind", "rest api", "restful", "graphql", "json",
    # Databases & Storage
    "sql", "sqlite", "mysql", "postgresql", "postgres", "mongodb", "redis", "oracle", "nosql", "firebase",
    # AI / ML / Data Science
    "machine learning", "deep learning", "artificial intelligence", "nlp", "natural language processing",
    "computer vision", "pandas", "numpy", "scikit-learn", "scipy", "matplotlib", "seaborn", "tensorflow", "keras",
    "pytorch", "data analysis", "data analytics", "data visualization", "statistics", "power bi", "tableau", "excel",
    # DevOps, Cloud & Tools
    "git", "github", "gitlab", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "unix", "bash", "ci/cd",
    "jenkins", "postman", "vs code", "visual studio", "jira", "agile", "scrum",
    # Computer Science Fundamentals
    "object-oriented programming", "oop", "data structures", "algorithms", "dsa", "unit testing", "debugging",
    "problem solving", "version control", "software development life cycle", "sdlc"
]


def extract_keywords_from_job_description(job_description: str):
    """
    Extract meaningful, prioritized technical and role-specific keywords
    from the Job Description text.
    """
    if not job_description:
        return []

    jd_lower = job_description.lower()
    extracted_keywords = []

    # 1. Match multi-word and known technical terminology first
    for term in KNOWN_TECHNICAL_KEYWORDS:
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
        if re.search(pattern, jd_lower):
            # Capitalize cleanly for display
            clean_term = term.title() if len(term) > 3 else term.upper()
            if clean_term not in extracted_keywords:
                extracted_keywords.append(clean_term)

    # 2. Extract any capitalized technical acronyms or specific technical tokens (e.g., API, SDK, AWS, MVC)
    tokens = re.findall(r"\b[A-Za-z0-9+#.-]+\b", job_description)
    for token in tokens:
        token_clean = token.strip(".-")
        token_lower = token_clean.lower()
        if (
            len(token_clean) >= 2
            and token_lower not in STOPWORDS
            and not token_clean.isnumeric()
        ):
            # Check if it has uppercase technical acronym appearance or capitalized term
            if token_clean.isupper() or (len(token_clean) > 2 and token_clean[0].isupper()):
                norm_term = token_clean.upper() if len(token_clean) <= 4 else token_clean.title()
                if norm_term not in extracted_keywords and norm_term.lower() not in [k.lower() for k in extracted_keywords]:
                    # Limit general capitalized terms to keep focus on relevant keywords
                    if norm_term.lower() in [k.lower() for k in KNOWN_TECHNICAL_KEYWORDS]:
                        extracted_keywords.append(norm_term)

    # Deduplicate while preserving order
    unique_keywords = []
    seen = set()
    for kw in extracted_keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            unique_keywords.append(kw)

    return unique_keywords


def check_keyword_in_text(keyword: str, text: str) -> bool:
    """
    Case-insensitive word boundary check for a keyword inside text.
    Correctly handles terms like 'C', 'C++', 'Node.js', and multi-word phrases.
    """
    kw_lower = keyword.lower().strip()
    text_lower = text.lower()

    if kw_lower in ["c++", "c#", "node.js", ".net"]:
        pattern = r"(?<!\w)" + re.escape(kw_lower) + r"(?!\w)"
    else:
        pattern = r"\b" + re.escape(kw_lower) + r"\b"

    return bool(re.search(pattern, text_lower))


def calculate_keyword_match(resume_text: str, job_description: str):
    """
    Calculate the exact Keyword Match metrics as specified in Section 15:
    - Formula:
        Keyword Match % = Matched Important Keywords / Total Important Keywords * 100
        Keyword Score = Keyword Match % * 30 / 100
    Returns:
      dict containing:
        - total_keywords: int
        - matched_keywords: list[str]
        - missing_keywords: list[str]
        - match_percentage: float (0.0 to 100.0)
        - keyword_score: float (0.0 to 30.0)
    """
    jd_keywords = extract_keywords_from_job_description(job_description)

    # Fallback if JD is short or generic
    if not jd_keywords:
        # Extract general words minus stopwords
        words = re.findall(r"\b[a-zA-Z]{3,}\b", job_description.lower())
        filtered = [w.title() for w in words if w not in STOPWORDS]
        # Take unique top words
        jd_keywords = list(dict.fromkeys(filtered))[:10]

    matched = []
    missing = []

    for kw in jd_keywords:
        if check_keyword_in_text(kw, resume_text):
            matched.append(kw)
        else:
            missing.append(kw)

    total_count = len(jd_keywords)
    matched_count = len(matched)

    if total_count > 0:
        match_pct = round((matched_count / total_count) * 100.0, 1)
        score = round((match_pct * 30.0) / 100.0, 1)
    else:
        match_pct = 0.0
        score = 0.0

    return {
        "total_keywords": total_count,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "match_percentage": match_pct,
        "keyword_score": score
    }
