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
