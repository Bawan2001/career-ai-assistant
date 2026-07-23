import re
from typing import Dict, Any, List
import pypdf

class CVParser:
    """
    Parses PDF resumes and extracts structured text, contact details, and core CV sections.
    """

    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """Extract raw text from uploaded PDF file object or file path."""
        try:
            reader = pypdf.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""

    @staticmethod
    def parse_structured_cv(raw_text: str) -> Dict[str, Any]:
        """
        Parses raw text into structured CV sections using regex heuristics.
        """
        sections = {
            "contact_info": CVParser._extract_contact_info(raw_text),
            "skills": CVParser._extract_section(raw_text, ["skills", "technical skills", "technologies", "competencies"]),
            "experience": CVParser._extract_section(raw_text, ["experience", "work experience", "employment history", "professional experience"]),
            "education": CVParser._extract_section(raw_text, ["education", "academic background", "qualification"]),
            "projects": CVParser._extract_section(raw_text, ["projects", "personal projects", "academic projects"]),
            "certifications": CVParser._extract_section(raw_text, ["certifications", "licenses", "certificates"]),
            "summary": CVParser._extract_section(raw_text, ["summary", "profile", "objective", "about me"]),
            "raw_text": raw_text
        }
        return sections

    @staticmethod
    def _extract_contact_info(text: str) -> Dict[str, str]:
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        linkedin_match = re.search(r'(linkedin\.com/in/[\w-]+)', text, re.IGNORECASE)
        github_match = re.search(r'(github\.com/[\w-]+)', text, re.IGNORECASE)

        return {
            "email": email_match.group(0) if email_match else "Not found",
            "phone": phone_match.group(0) if phone_match else "Not found",
            "linkedin": linkedin_match.group(0) if linkedin_match else "Not found",
            "github": github_match.group(0) if github_match else "Not found"
        }

    @staticmethod
    def _extract_section(text: str, keywords: List[str]) -> str:
        lines = text.split('\n')
        matched_lines = []
        capturing = False

        heading_pattern = re.compile(r'^[A-Z\s]{3,30}$', re.IGNORECASE)

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue

            # Check if this line is a target section header
            is_target_header = any(re.search(rf'\b{kw}\b', clean_line, re.IGNORECASE) for kw in keywords) and len(clean_line) < 40

            if is_target_header:
                capturing = True
                continue
            elif capturing and heading_pattern.match(clean_line) and len(clean_line) < 35:
                # Reached another header, stop capturing
                break

            if capturing:
                matched_lines.append(clean_line)

        return "\n".join(matched_lines) if matched_lines else ""
