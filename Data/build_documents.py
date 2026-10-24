import json

def pct(x):
    return f"{x * 100:.0f}%" if x is not None else "not reported"

def money(x):
    return f"${x:,.0f}" if x is not None else "not reported"

with open("data/schools.json") as f:
    schools = json.load(f)

OWNERSHIP = {1: "public school", 2: "private nonprofit school", 3: "private for-profit school"}

MAJOR_LABELS = {
    "agriculture": "Agriculture",
    "resources": "Natural Resources and Conservation",
    "architecture": "Architecture",
    "ethnic_cultural_gender": "Ethnic, Cultural and Gender Studies",
    "communication": "Communication and Journalism",
    "communications_technology": "Communications Technology",
    "computer": "Computer Science",
    "personal_culinary": "Culinary and Personal Services",
    "education": "Education",
    "engineering": "Engineering",
    "engineering_technology": "Engineering Technology",
    "language": "Foreign Languages",
    "family_consumer_science": "Family and Consumer Sciences",
    "legal": "Legal Studies",
    "english": "English",
    "humanities": "Humanities",
    "library": "Library Science",
    "biological": "Biology",
    "mathematics": "Mathematics and Statistics",
    "military": "Military Technologies",
    "multidiscipline": "Interdisciplinary Studies",
    "parks_recreation_fitness": "Parks, Recreation and Fitness",
    "philosophy_religious": "Philosophy and Religious Studies",
    "theology_religious_vocation": "Theology",
    "physical_science": "Physical Sciences",
    "science_technology": "Science Technologies",
    "psychology": "Psychology",
    "security_law_enforcement": "Criminal Justice and Security",
    "public_administration_social_service": "Public Administration and Social Service",
    "social_science": "Social Sciences",
    "construction": "Construction Trades",
    "mechanic_repair_technology": "Mechanic and Repair Technologies",
    "precision_production": "Precision Production",
    "transportation": "Transportation",
    "visual_performing": "Visual and Performing Arts",
    "health": "Health Professions",
    "business_marketing": "Business and Marketing",
    "history": "History",
}

def top_majors(s, n=5):
    found = []
    for key, label in MAJOR_LABELS.items():
        value = s.get(f"latest.academics.program_percentage.{key}")
        if value:
            found.append((value, label))
    found.sort(reverse=True)
    return ", ".join(f"{label} ({value * 100:.0f}%)" for value, label in found[:n])

documents = []
for s in schools:
    url = s.get("school.school_url") or ""
    if url and not url.startswith("http"):
        url = "https://" + url

    text = (
        f"{s.get('school.name')} is a {OWNERSHIP.get(s.get('school.ownership'), 'school')} "
        f"located in {s.get('school.city')}, {s.get('school.state')}. "
        f"It has about {s.get('latest.student.size') or 'an unreported number of'} students. "
        f"Admission rate: {pct(s.get('latest.admissions.admission_rate.overall'))}. "
        f"Average SAT: {s.get('latest.admissions.sat_scores.average.overall') or 'not reported'}. "
        f"Tuition: {money(s.get('latest.cost.tuition.in_state'))} in-state, "
        f"{money(s.get('latest.cost.tuition.out_of_state'))} out-of-state. "
        f"Average net price per year: {money(s.get('latest.cost.avg_net_price.overall'))}. "
        f"Median debt for graduates: {money(s.get('latest.aid.median_debt.graduates.overall'))}. "
        f"Graduation rate: {pct(s.get('latest.completion.rate_suppressed.overall'))}. "
        f"Median earnings 10 years after entry: {money(s.get('latest.earnings.10_yrs_after_entry.median'))}. "
        f"Most popular fields of study (share of degrees): {top_majors(s) or 'not reported'}. "
        f"Website: {url or 'not reported'}"
    )

    documents.append({
        "id": str(s["id"]),
        "text": text,
        "metadata": {
            "name": s.get("school.name") or "",
            "city": s.get("school.city") or "",
            "state": s.get("school.state") or "",
            "ownership": OWNERSHIP.get(s.get("school.ownership"), ""),
            "net_price": s.get("latest.cost.avg_net_price.overall") or -1,
            "grad_rate": s.get("latest.completion.rate_suppressed.overall") or -1,
            "earnings": s.get("latest.earnings.10_yrs_after_entry.median") or -1,
            "website": url,
        },
    })

with open("data/documents.json", "w") as f:
    json.dump(documents, f, indent=2)

print(f"Built {len(documents)} documents")