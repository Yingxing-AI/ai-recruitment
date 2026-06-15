import re
from io import BytesIO
from pathlib import Path
from typing import Any

from docx import Document
from pypdf import PdfReader


EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")
NAME_PATTERN = re.compile(r"(?:姓名|Name)[:：\s]*([\u4e00-\u9fa5]{2,4}|[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})")

SECTION_ALIASES = {
    "education": ["教育经历", "教育背景", "学历", "Education"],
    "work_experience": ["工作经历", "工作经验", "职业经历", "Work Experience", "Experience"],
    "skills": ["技能", "专业技能", "技能清单", "Skills"],
    "projects": ["项目经历", "项目经验", "Projects"],
}

SKILL_KEYWORDS = [
    "Python",
    "Java",
    "Go",
    "JavaScript",
    "TypeScript",
    "React",
    "Vue",
    "FastAPI",
    "Django",
    "Spring",
    "PostgreSQL",
    "MySQL",
    "Redis",
    "Docker",
    "Kubernetes",
    "微服务",
    "架构",
    "数据分析",
    "机器学习",
    "招聘运营",
    "沟通",
    "项目管理",
]


def normalize_resume_text(text: str | None) -> str:
    if not text:
        return ""
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def extract_text_from_file(content: bytes, file_name: str, content_type: str | None = None) -> str:
    suffix = Path(file_name).suffix.lower()
    if suffix == ".pdf" or content_type == "application/pdf":
        return extract_pdf_text(content)
    if suffix == ".docx" or content_type in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }:
        return extract_docx_text(content)
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("utf-8", errors="ignore")


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    lines: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            lines.append(page_text)
    return normalize_resume_text("\n".join(lines))


def extract_docx_text(content: bytes) -> str:
    document = Document(BytesIO(content))
    return normalize_resume_text("\n".join(paragraph.text for paragraph in document.paragraphs))


def parse_resume_text(text: str) -> dict[str, Any]:
    normalized = normalize_resume_text(text)
    lines = normalized.splitlines()
    sections = extract_sections(lines)
    skills = extract_skills(normalized, sections.get("skills", []))
    return {
        "name": extract_name(normalized, lines),
        "phone": extract_first(PHONE_PATTERN, normalized),
        "email": extract_first(EMAIL_PATTERN, normalized),
        "education": sections.get("education", []),
        "work_experience": sections.get("work_experience", []),
        "skills": skills,
        "projects": sections.get("projects", []),
        "text_length": len(normalized),
    }


def extract_first(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1 if pattern.groups else 0).strip() if match else None


def extract_name(text: str, lines: list[str]) -> str | None:
    explicit = extract_first(NAME_PATTERN, text)
    if explicit:
        return explicit
    for line in lines[:8]:
        stripped = line.strip().strip("：:")
        if 2 <= len(stripped) <= 12 and not EMAIL_PATTERN.search(stripped) and not PHONE_PATTERN.search(stripped):
            if re.fullmatch(r"[\u4e00-\u9fa5]{2,4}", stripped):
                return stripped
    return None


def extract_sections(lines: list[str]) -> dict[str, list[str]]:
    current_key: str | None = None
    sections: dict[str, list[str]] = {key: [] for key in SECTION_ALIASES}
    alias_to_key = {
        alias.lower(): key for key, aliases in SECTION_ALIASES.items() for alias in aliases
    }

    for line in lines:
        compact = line.strip().strip("：:").lower()
        matched_key = alias_to_key.get(compact)
        if matched_key:
            current_key = matched_key
            continue
        for alias, key in alias_to_key.items():
            if compact.startswith(alias.lower()) and len(compact) <= len(alias) + 8:
                current_key = key
                break
        else:
            if current_key and line.strip():
                sections[current_key].append(line.strip())

    if not any(sections.values()):
        sections.update(extract_sections_by_keywords(lines))
    return sections


def extract_sections_by_keywords(lines: list[str]) -> dict[str, list[str]]:
    sections = {key: [] for key in SECTION_ALIASES}
    for line in lines:
        if any(keyword in line for keyword in ["大学", "本科", "硕士", "博士", "学院"]):
            sections["education"].append(line)
        if any(keyword in line for keyword in ["公司", "负责", "任职", "工作"]):
            sections["work_experience"].append(line)
        if any(keyword in line for keyword in ["项目", "系统", "平台"]):
            sections["projects"].append(line)
    return sections


def extract_skills(text: str, skill_lines: list[str]) -> list[str]:
    haystack = "\n".join(skill_lines) if skill_lines else text
    found = [skill for skill in SKILL_KEYWORDS if skill.lower() in haystack.lower()]
    split_candidates = re.split(r"[,，/、\s]+", haystack)
    for item in split_candidates:
        cleaned = item.strip("；;。.")
        if 2 <= len(cleaned) <= 24 and cleaned in SKILL_KEYWORDS and cleaned not in found:
            found.append(cleaned)
    return found
