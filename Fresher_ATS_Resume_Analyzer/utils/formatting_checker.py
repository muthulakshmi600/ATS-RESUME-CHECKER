"""
Resume Section Detection, Formatting Inspection, and Contact Information Analysis.
Implements the exact 15-point Section Scoring, 15-point Formatting Scoring,
and 10-point Contact Information Scoring.
"""

import re

# Standard section header regex patterns
SECTION_PATTERNS = {
    "Contact Information": [
        r"\bcontact\b", r"\bcontact info\b", r"\bpersonal info\b", r"\bcontact details\b"
    ],
    "Professional Summary": [
        r"\bprofessional summary\b", r"\bsummary\b", r"\bcareer objective\b",
        r"\bobjective\b", r"\bprofile summary\b", r"\babout me\b"
    ],
    "Technical Skills": [
        r"\btechnical skills\b", r"\bskills\b", r"\bcore competencies\b",
        r"\bkey skills\b", r"\btechnologies\b", r"\btechnical proficiencies\b"
    ],
    "Education": [
        r"\beducation\b", r"\bacademics\b", r"\bacqdemic background\b",
        r"\beducational qualifications\b", r"\bqualifications\b"
    ],
    "Projects": [
        r"\bprojects\b", r"\bacqdemic projects\b", r"\bpersonal projects\b",
        r"\bkey projects\b", r"\bmajor projects\b", r"\bmini projects\b"
    ],
    "Internship / Training": [
        r"\binternship\b", r"\binternships\b", r"\btraining\b",
        r"\bindustrial training\b", r"\bvocational training\b", r"\bwork experience\b"
    ],
    "Certifications": [
        r"\bcertifications\b", r"\bcertificates\b", r"\bworkshops\b",
        r"\bcourses\b", r"\bachievements\b", r"\blicenses\b"
    ]
}


def detect_sections(text: str):
    """
    Detect presence of standard resume sections.
    Returns:
      dict: {section_name -> bool (True if present, False if missing)}
    """
    text_lower = text.lower()
    detected = {}

    for section, patterns in SECTION_PATTERNS.items():
        is_found = False
        for p in patterns:
            if re.search(p, text_lower):
                is_found = True
                break
        detected[section] = is_found

    # If contact info wasn't an explicit header, check if email or phone is present
    if not detected["Contact Information"]:
        has_email = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text))
        has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
        if has_email or has_phone:
            detected["Contact Information"] = True

    return detected


def calculate_section_score(detected_sections: dict):
    """
    Calculate the exact 15-point Section Score as specified in Section 17:
    - Contact Information   = 2
    - Professional Summary  = 2
    - Technical Skills      = 3
    - Education             = 3
    - Projects              = 3
    - Internship / Training = 1
    - Certifications        = 1
    TOTAL = 15 points
    """
    weights = {
        "Contact Information": 2.0,
        "Professional Summary": 2.0,
        "Technical Skills": 3.0,
        "Education": 3.0,
        "Projects": 3.0,
        "Internship / Training": 1.0,
        "Certifications": 1.0
    }

    score = 0.0
    breakdown = {}

    for sec, max_pts in weights.items():
        present = detected_sections.get(sec, False)
        pts = max_pts if present else 0.0
        score += pts
        breakdown[sec] = {
            "present": present,
            "points": pts,
            "max_points": max_pts
        }

    return round(score, 1), breakdown


def analyze_contact_information(text: str):
    """
    Extract and score contact details as specified in Section 20:
    - Name       = 2
    - Email      = 2
    - Phone      = 2
    - Location   = 1
    - LinkedIn   = 1.5
    - GitHub     = 1.5
    TOTAL = 10 points
    """
    text_lower = text.lower()

    # 1. Email detection
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    email_found = bool(email_match)
    email_val = email_match.group(0) if email_match else None

    # 2. Phone detection
    phone_match = re.search(r"(\+?\d{1,4}[-.\s]?)?(\(?\d{3,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}", text)
    phone_found = bool(phone_match) and len(phone_match.group(0).strip()) >= 10
    phone_val = phone_match.group(0).strip() if phone_found else None

    # 3. LinkedIn
    linkedin_found = bool(re.search(r"\blinkedin(?:\.com/in)?\b", text_lower))

    # 4. GitHub
    github_found = bool(re.search(r"\bgithub(?:\.com)?\b", text_lower))

    # 5. Location / City / State / Pincode
    location_keywords = [
        "bangalore", "bengaluru", "chennai", "hyderabad", "pune", "mumbai", "delhi", "noida",
        "gurgaon", "kolkata", "coimbatore", "kochi", "india", "remote", "address", "city",
        "pin", "postal code", "tamil nadu", "karnataka", "telangana", "maharashtra"
    ]
    location_found = any(loc in text_lower for loc in location_keywords)

    # 6. Name extraction heuristics:
    # First 3 non-empty lines usually have the candidate's name if not an email/phone/heading
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    candidate_name = None
    for line in lines[:5]:
        if len(line.split()) in [2, 3, 4] and not re.search(r"[@0-9|:/]", line):
            if not any(k in line.lower() for k in ["resume", "curriculum", "vitae", "contact", "developer"]):
                candidate_name = line
                break
    name_found = candidate_name is not None or len(lines) > 0
    if not candidate_name and lines:
        candidate_name = lines[0][:40]

    # Calculate exact 10-point contact score
    score = 0.0
    score += 2.0 if name_found else 0.0
    score += 2.0 if email_found else 0.0
    score += 2.0 if phone_found else 0.0
    score += 1.0 if location_found else 0.0
    score += 1.5 if linkedin_found else 0.0
    score += 1.5 if github_found else 0.0

    return {
        "candidate_name": candidate_name or "Candidate",
        "email": email_val,
        "phone": phone_val,
        "name_found": name_found,
        "email_found": email_found,
        "phone_found": phone_found,
        "location_found": location_found,
        "linkedin_found": linkedin_found,
        "github_found": github_found,
        "contact_score": round(score, 1),
        "max_score": 10.0
    }


def analyze_formatting(text: str, metadata: dict):
    """
    Evaluate resume formatting against the exact 15-point criteria in Section 18:
    1. Text extraction successful       = 3
    2. Standard headings                = 2
    3. Clear single-column structure    = 2
    4. No problematic tables            = 2
    5. No excessive graphics/images     = 2
    6. Reasonable spacing               = 2
    7. No excessive special characters  = 1
    8. No excessively long paragraphs   = 1
    TOTAL = 15 points
    """
    scores = {}
    details = []

    # 1. Text extraction successful (3 pts)
    text_ok = len(text.strip()) >= 50
    scores["text_extraction"] = 3.0 if text_ok else 0.0
    details.append({
        "rule": "Text extraction successful",
        "passed": text_ok,
        "score": scores["text_extraction"],
        "max": 3.0,
        "status": "✅ Extracted cleanly" if text_ok else "❌ Extraction failed"
    })

    # 2. Standard headings (2 pts)
    detected_secs = detect_sections(text)
    standard_headings_count = sum(1 for v in detected_secs.values() if v)
    headings_ok = standard_headings_count >= 3
    scores["standard_headings"] = 2.0 if headings_ok else (1.0 if standard_headings_count >= 1 else 0.0)
    details.append({
        "rule": "Standard headings",
        "passed": headings_ok,
        "score": scores["standard_headings"],
        "max": 2.0,
        "status": f"✅ {standard_headings_count} standard sections identified" if headings_ok else "⚠️ Few standard headings found"
    })

    # 3. Clear single-column structure (2 pts)
    # Heuristic: multi-column resumes often have strange wrapped short lines or tab stops
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    short_interleaved_lines = sum(1 for l in lines if len(l) < 20 and not l.isupper())
    single_column = (short_interleaved_lines / max(len(lines), 1)) < 0.35
    scores["single_column"] = 2.0 if single_column else 1.0
    details.append({
        "rule": "Clear single-column structure",
        "passed": single_column,
        "score": scores["single_column"],
        "max": 2.0,
        "status": "✅ Linear single-column flow" if single_column else "⚠️ Potential multi-column or disjointed text"
    })

    # 4. No problematic tables (2 pts)
    # If DOCX, check table_count; if PDF, check metadata or vertical pipe characters
    tables_count = metadata.get("table_count", 0)
    no_bad_tables = tables_count <= 2
    scores["tables"] = 2.0 if no_bad_tables else 1.0
    details.append({
        "rule": "No problematic tables",
        "passed": no_bad_tables,
        "score": scores["tables"],
        "max": 2.0,
        "status": "✅ Clean layout without complex nested tables" if no_bad_tables else "⚠️ Complex tables detected"
    })

    # 5. No excessive graphics/images (2 pts)
    image_count = metadata.get("image_count", 0)
    no_excessive_images = image_count <= 2
    scores["images"] = 2.0 if no_excessive_images else 0.5
    details.append({
        "rule": "No excessive graphics/images",
        "passed": no_excessive_images,
        "score": scores["images"],
        "max": 2.0,
        "status": f"✅ Minimal/No graphics ({image_count} image{'s' if image_count!=1 else ''})" if no_excessive_images else f"⚠️ High graphic content ({image_count} images)"
    })

    # 6. Reasonable spacing (2 pts)
    # Check word count vs char count ratio (average word length between 4 and 8)
    words = text.split()
    avg_word_len = len(text) / max(len(words), 1)
    reasonable_spacing = 4.0 <= avg_word_len <= 10.0
    scores["spacing"] = 2.0 if reasonable_spacing else 1.0
    details.append({
        "rule": "Reasonable spacing",
        "passed": reasonable_spacing,
        "score": scores["spacing"],
        "max": 2.0,
        "status": "✅ Normal word density and line spacing" if reasonable_spacing else "⚠️ Spacing abnormalities detected"
    })

    # 7. No excessive special characters (1 pt)
    special_chars = len(re.findall(r"[^\w\s.,;:()\-/@+]", text))
    special_char_ratio = special_chars / max(len(text), 1)
    no_excess_specials = special_char_ratio < 0.03
    scores["special_chars"] = 1.0 if no_excess_specials else 0.0
    details.append({
        "rule": "No excessive special characters",
        "passed": no_excess_specials,
        "score": scores["special_chars"],
        "max": 1.0,
        "status": "✅ Clean typography without distracting icons" if no_excess_specials else "⚠️ Decorative symbols detected"
    })

    # 8. No excessively long paragraphs (1 pt)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]
    no_long_paragraphs = len(long_paragraphs) == 0
    scores["long_paragraphs"] = 1.0 if no_long_paragraphs else 0.0
    details.append({
        "rule": "No excessively long paragraphs",
        "passed": no_long_paragraphs,
        "score": scores["long_paragraphs"],
        "max": 1.0,
        "status": "✅ Bullet-friendly concise text" if no_long_paragraphs else f"⚠️ {len(long_paragraphs)} long paragraph(s) detected (use bullet points)"
    })

    total_score = round(sum(scores.values()), 1)

    return {
        "formatting_score": total_score,
        "max_score": 15.0,
        "details": details
    }
