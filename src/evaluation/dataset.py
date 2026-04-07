SYNTHETIC_JOBS = [
    {
        "job_id": "et-pilot-001",
        "title": "Trainee Pilot",
        "description": "Flight fundamentals, cockpit procedures, navigation basics, aviation safety communication and simulator training.",
        "company_name": "Ethiopian Airlines",
    },
    {
        "job_id": "et-cabin-001",
        "title": "Trainee Cabin Crew",
        "description": "In-flight passenger support, cabin safety checks, emergency response, hospitality and customer service excellence.",
        "company_name": "Ethiopian Airlines",
    },
    {
        "job_id": "et-mech-001",
        "title": "Trainee Aircraft Mechanic",
        "description": "Aircraft mechanical inspection, maintenance routines, tooling usage, fault diagnosis and maintenance documentation.",
        "company_name": "Ethiopian Airlines",
    },
    {
        "job_id": "et-avionics-001",
        "title": "Trainee Avionics Technician",
        "description": "Avionics systems troubleshooting, instrument calibration, wiring diagrams, electronic diagnostics and repair logging.",
        "company_name": "Ethiopian Airlines",
    },
    {
        "job_id": "et-power-001",
        "title": "Trainee Power Plant Technician",
        "description": "Aircraft engine systems, turbine maintenance, propulsion inspection, component testing and powerplant safety procedures.",
        "company_name": "Ethiopian Airlines",
    },
    {
        "job_id": "et-ground-001",
        "title": "Trainee Ground Operations Officer",
        "description": "Ramp coordination, baggage operations, dispatch communication, turnaround efficiency and airport ground safety.",
        "company_name": "Ethiopian Airlines",
    },
    {
        "job_id": "et-cs-001",
        "title": "Trainee Customer Service Agent",
        "description": "Airport check-in, passenger issue resolution, ticketing support, communication and customer care.",
        "company_name": "Ethiopian Airlines",
    },
    {
        "job_id": "et-finance-001",
        "title": "Trainee Finance / Accounting (College, Trainee)",
        "description": "Accounting principles, reconciliations, financial reporting, spreadsheet analysis and budget support.",
        "company_name": "Ethiopian Airlines",
    },
]


SYNTHETIC_SAMPLES = [
    {
        "sample_id": "cv-ground-ops",
        "cv_text": "Graduate intern in airport ramp and baggage flow, coordinated turnaround and dispatch communication.",
        "expected_top1_job_id": "et-ground-001",
    },
    {
        "sample_id": "cv-cabin-service",
        "cv_text": "Trained in onboard safety demonstrations, passenger support and hospitality for in-flight services.",
        "expected_top1_job_id": "et-cabin-001",
    },
    {
        "sample_id": "cv-mechanic-track",
        "cv_text": "Hands-on mechanical maintenance workshop, aircraft component inspection and fault diagnosis practice.",
        "expected_top1_job_id": "et-mech-001",
    },
    {
        "sample_id": "cv-avionics-track",
        "cv_text": "Electronics student with wiring diagram analysis, avionics troubleshooting and instrument calibration lab tasks.",
        "expected_top1_job_id": "et-avionics-001",
    },
    {
        "sample_id": "cv-finance-track",
        "cv_text": "Accounting graduate with reconciliation, reporting and budget support experience using spreadsheets.",
        "expected_top1_job_id": "et-finance-001",
    },
    {
        "sample_id": "cv-pilot-support",
        "cv_text": "Aviation trainee focused on navigation basics, cockpit communication and simulator practice.",
        "expected_top1_job_id": "et-pilot-001",
    },
]


def build_synthetic_dataset() -> dict:
    return {"jobs": SYNTHETIC_JOBS, "samples": SYNTHETIC_SAMPLES}


PHASE2_DATASET_VERSION = "v1"
PHASE2_CV_BUCKET_TARGETS = {
    "high": 70,
    "medium": 70,
    "low": 60,
}

ROLE_KEYWORDS = {
    "et-pilot-001": ["cockpit", "navigation", "flight", "aviation safety", "simulator"],
    "et-cabin-001": ["passenger care", "in-flight", "cabin safety", "hospitality", "service"],
    "et-mech-001": ["aircraft maintenance", "mechanical inspection", "tooling", "fault diagnosis", "repair"],
    "et-avionics-001": ["avionics", "wiring diagram", "calibration", "electronics", "instrument"],
    "et-power-001": ["engine", "turbine", "powerplant", "propulsion", "component testing"],
    "et-ground-001": ["ramp", "baggage", "turnaround", "dispatch", "ground safety"],
    "et-cs-001": ["check-in", "ticketing", "passenger issue", "communication", "customer support"],
    "et-finance-001": ["accounting", "reconciliation", "financial reporting", "budget", "spreadsheet"],
}

ADJACENT_ROLE_IDS = {
    "et-pilot-001": {"et-ground-001", "et-cabin-001"},
    "et-cabin-001": {"et-cs-001", "et-ground-001"},
    "et-mech-001": {"et-power-001", "et-avionics-001"},
    "et-avionics-001": {"et-mech-001", "et-power-001"},
    "et-power-001": {"et-mech-001", "et-avionics-001"},
    "et-ground-001": {"et-cs-001", "et-pilot-001"},
    "et-cs-001": {"et-cabin-001", "et-ground-001"},
    "et-finance-001": {"et-cs-001", "et-ground-001"},
}

LOW_MATCH_TOPICS = [
    "retail merchandising, fashion blogging and influencer campaign planning",
    "crop irrigation planning, agronomy field surveys and seed procurement analysis",
    "social media content scheduling, podcast editing and audience engagement analytics",
    "restaurant menu costing, food photography and cafe event promotion",
    "construction site landscaping, furniture polishing and decorative lighting setup",
]


def build_phase2_jobs() -> list[dict]:
    return list(SYNTHETIC_JOBS)


def _compose_high_match_text(job_id: str, sample_idx: int) -> str:
    keywords = ROLE_KEYWORDS[job_id]
    return (
        f"Candidate {sample_idx} completed aviation trainee practice in {keywords[0]}, {keywords[1]}, "
        f"{keywords[2]}, and {keywords[3]} with reliable teamwork and operational discipline."
    )


def _compose_medium_match_text(job_id: str, sample_idx: int) -> str:
    adjacent_job_id = sorted(ADJACENT_ROLE_IDS[job_id])[sample_idx % 2]
    target_keywords = ROLE_KEYWORDS[job_id]
    adjacent_keywords = ROLE_KEYWORDS[adjacent_job_id]
    return (
        f"Candidate {sample_idx} built adjacent airline experience around {adjacent_keywords[0]} and "
        f"{adjacent_keywords[1]}, plus transferable exposure to {target_keywords[2]} and {target_keywords[3]}."
    )


def _compose_low_match_text(sample_idx: int) -> str:
    topic = LOW_MATCH_TOPICS[sample_idx % len(LOW_MATCH_TOPICS)]
    return (
        f"Candidate {sample_idx} profile focuses on {topic}, with limited direct airline vocational alignment."
    )


def build_phase2_cvs() -> list[dict]:
    jobs = build_phase2_jobs()
    job_ids = [job["job_id"] for job in jobs]
    cvs: list[dict] = []
    cv_counter = 1

    for bucket_name in ("high", "medium", "low"):
        target_count = PHASE2_CV_BUCKET_TARGETS[bucket_name]
        for i in range(target_count):
            target_job_id = job_ids[i % len(job_ids)]
            sample_idx = cv_counter
            if bucket_name == "high":
                cv_text = _compose_high_match_text(target_job_id, sample_idx)
            elif bucket_name == "medium":
                cv_text = _compose_medium_match_text(target_job_id, sample_idx)
            else:
                cv_text = _compose_low_match_text(sample_idx)

            cvs.append(
                {
                    "cv_id": f"cv-{PHASE2_DATASET_VERSION}-{cv_counter:03d}",
                    "cv_text": cv_text,
                    "target_job_id": target_job_id,
                    "match_bucket": bucket_name,
                }
            )
            cv_counter += 1

    return cvs


def expected_label_for_pair(cv_record: dict, job_id: str) -> str:
    target_job_id = cv_record["target_job_id"]
    bucket = cv_record["match_bucket"]

    if bucket == "low":
        return "bad"
    if job_id == target_job_id:
        return "good" if bucket == "high" else "medium"
    if job_id in ADJACENT_ROLE_IDS.get(target_job_id, set()):
        return "medium"
    return "bad"


def expected_rank_for_pair(cv_record: dict, job_id: str) -> int:
    target_job_id = cv_record["target_job_id"]
    if job_id == target_job_id:
        return 1
    if job_id in ADJACENT_ROLE_IDS.get(target_job_id, set()):
        return 2
    return 3


def build_phase2_pairs(cvs: list[dict], jobs: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for cv in cvs:
        for job in jobs:
            rows.append(
                {
                    "dataset_version": PHASE2_DATASET_VERSION,
                    "cv_id": cv["cv_id"],
                    "cv_text": cv["cv_text"],
                    "job_id": job["job_id"],
                    "job_title": job["title"],
                    "job_description": job["description"],
                    "company_name": job["company_name"],
                    "expected_label": expected_label_for_pair(cv, job["job_id"]),
                    "expected_rank": expected_rank_for_pair(cv, job["job_id"]),
                    "match_bucket": cv["match_bucket"],
                    "target_job_id": cv["target_job_id"],
                }
            )
    return rows
