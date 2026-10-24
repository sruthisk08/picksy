import os, json, requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("COLLEGE_SCORECARD_API_KEY")
URL = "https://api.data.gov/ed/collegescorecard/v1/schools"

fields = ",".join([
    # basics (already working)
    "id",
    "school.name",
    "school.city",
    "school.state",
    "school.school_url",
    "latest.student.size",
    "latest.admissions.admission_rate.overall",
    "latest.cost.avg_net_price.overall",
    "latest.completion.rate_suppressed.overall",
    "latest.earnings.10_yrs_after_entry.median",

    # new: type of school, cost, test scores, debt
    "school.ownership",
    "latest.cost.tuition.in_state",
    "latest.cost.tuition.out_of_state",
    "latest.admissions.sat_scores.average.overall",
    "latest.aid.median_debt.graduates.overall",

    # new: share of degrees by major area
    "latest.academics.program_percentage.agriculture",
    "latest.academics.program_percentage.resources",
    "latest.academics.program_percentage.architecture",
    "latest.academics.program_percentage.ethnic_cultural_gender",
    "latest.academics.program_percentage.communication",
    "latest.academics.program_percentage.communications_technology",
    "latest.academics.program_percentage.computer",
    "latest.academics.program_percentage.personal_culinary",
    "latest.academics.program_percentage.education",
    "latest.academics.program_percentage.engineering",
    "latest.academics.program_percentage.engineering_technology",
    "latest.academics.program_percentage.language",
    "latest.academics.program_percentage.family_consumer_science",
    "latest.academics.program_percentage.legal",
    "latest.academics.program_percentage.english",
    "latest.academics.program_percentage.humanities",
    "latest.academics.program_percentage.library",
    "latest.academics.program_percentage.biological",
    "latest.academics.program_percentage.mathematics",
    "latest.academics.program_percentage.military",
    "latest.academics.program_percentage.multidiscipline",
    "latest.academics.program_percentage.parks_recreation_fitness",
    "latest.academics.program_percentage.philosophy_religious",
    "latest.academics.program_percentage.theology_religious_vocation",
    "latest.academics.program_percentage.physical_science",
    "latest.academics.program_percentage.science_technology",
    "latest.academics.program_percentage.psychology",
    "latest.academics.program_percentage.security_law_enforcement",
    "latest.academics.program_percentage.public_administration_social_service",
    "latest.academics.program_percentage.social_science",
    "latest.academics.program_percentage.construction",
    "latest.academics.program_percentage.mechanic_repair_technology",
    "latest.academics.program_percentage.precision_production",
    "latest.academics.program_percentage.transportation",
    "latest.academics.program_percentage.visual_performing",
    "latest.academics.program_percentage.health",
    "latest.academics.program_percentage.business_marketing",
    "latest.academics.program_percentage.history",
])

all_schools = []
page = 0
while True:
    params = {
        "api_key": API_KEY,
        "fields": fields,
        "school.degrees_awarded.predominant": 3,
        "per_page": 100,
        "page": page,
    }
    data = requests.get(URL, params=params).json()
    results = data.get("results", [])
    if not results:
        break
    all_schools.extend(results)
    page += 1

with open("data/schools.json", "w") as f:
    json.dump(all_schools, f, indent=2)

print(f"Saved {len(all_schools)} schools")