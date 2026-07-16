#!/usr/bin/env python3
import argparse
import csv
import json
import math
import random
from pathlib import Path


COLUMNS = [
    "loan_amnt",
    "term",
    "emp_length",
    "home_ownership",
    "annual_inc",
    "purpose",
    "dti",
    "fico_range_low",
    "delinq_2yrs",
    "inq_last_6mths",
    "revol_util",
    "open_acc",
    "pub_rec",
    "loan_status",
]

POSITIVE_STATUS = "Fully Paid"
NEGATIVE_STATUS = "Charged Off"

PURPOSES = {
    "car": "vehicle purchase",
    "credit_card": "credit card refinancing",
    "debt_consolidation": "debt consolidation",
    "educational": "education",
    "home_improvement": "home improvement",
    "house": "housing",
    "major_purchase": "major purchase",
    "medical": "medical expenses",
    "moving": "moving expenses",
    "other": "other purpose",
    "renewable_energy": "renewable energy",
    "small_business": "small business",
    "vacation": "travel",
    "wedding": "wedding",
}

HOME_OWNERSHIP = {
    "ANY": "not provided",
    "MORTGAGE": "mortgaged home",
    "NONE": "not provided",
    "OTHER": "other",
    "OWN": "owned home",
    "RENT": "rented home",
}


def money(value):
    number = to_float(value)
    if number is None:
        return "not provided"
    return f"US$ {number:,.2f}"


def percent(value):
    number = to_float(value)
    if number is None:
        return "not provided"
    return f"{number:.2f}%"


def integer(value):
    number = to_float(value)
    if number is None:
        return "not provided"
    return str(int(round(number)))


def to_float(value):
    if value is None:
        return None
    text = str(value).strip().replace("%", "")
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if math.isnan(number):
        return None
    return number


def clean_text(value):
    value = (value or "").strip()
    return value if value else "not provided"


def translate_purpose(value):
    value = clean_text(value)
    return PURPOSES.get(value, value.replace("_", " "))


def translate_home(value):
    value = clean_text(value).upper()
    return HOME_OWNERSHIP.get(value, value.lower())


def translate_term(value):
    value = clean_text(value)
    if "36" in value:
        return "36 months"
    if "60" in value:
        return "60 months"
    return value


def classify_fico(score):
    if score is None:
        return "no score provided"
    if score >= 760:
        return "a very strong score"
    if score >= 720:
        return "a strong score"
    if score >= 680:
        return "an adequate score"
    if score >= 640:
        return "a moderate score"
    return "a weak score"


def risk_factors(row):
    factors = []
    strengths = []

    fico = to_float(row.get("fico_range_low"))
    dti = to_float(row.get("dti"))
    delinquencies = to_float(row.get("delinq_2yrs"))
    inquiries = to_float(row.get("inq_last_6mths"))
    revol_util = to_float(row.get("revol_util"))
    income = to_float(row.get("annual_inc"))
    loan = to_float(row.get("loan_amnt"))
    term = clean_text(row.get("term"))

    if fico is None:
        factors.append("missing FICO score")
    elif fico < 660:
        factors.append("low FICO score")
    elif fico >= 720:
        strengths.append("favorable FICO score")

    if dti is None:
        factors.append("DTI not provided")
    elif dti > 30:
        factors.append("high indebtedness based on DTI")
    elif dti <= 15:
        strengths.append("controlled DTI")

    if delinquencies is not None and delinquencies > 0:
        factors.append("recent delinquency history")
    elif delinquencies == 0:
        strengths.append("no delinquencies in the last two years")

    if inquiries is not None and inquiries >= 3:
        factors.append("many recent credit inquiries")

    if revol_util is not None:
        if revol_util >= 80:
            factors.append("high revolving credit utilization")
        elif revol_util <= 35:
            strengths.append("low revolving credit utilization")

    if income and loan and loan / income > 0.45:
        factors.append("requested amount is high relative to annual income")
    elif income and loan and loan / income <= 0.20:
        strengths.append("requested amount is proportional to annual income")

    if "60" in term:
        factors.append("long term increases risk exposure")

    return strengths[:3], factors[:3]


def build_input(row):
    return (
        "Prepare an objective credit opinion based on the data below.\n"
        f"Requested amount: {money(row.get('loan_amnt'))}\n"
        f"Term: {translate_term(row.get('term'))}\n"
        f"Annual income: {money(row.get('annual_inc'))}\n"
        f"Purpose: {translate_purpose(row.get('purpose'))}\n"
        f"Housing status: {translate_home(row.get('home_ownership'))}\n"
        f"Employment length: {clean_text(row.get('emp_length'))}\n"
        f"DTI: {percent(row.get('dti'))}\n"
        f"Minimum FICO: {integer(row.get('fico_range_low'))}\n"
        f"Delinquencies in 2 years: {integer(row.get('delinq_2yrs'))}\n"
        f"Inquiries in 6 months: {integer(row.get('inq_last_6mths'))}\n"
        f"Revolving utilization: {percent(row.get('revol_util'))}\n"
        f"Open accounts: {integer(row.get('open_acc'))}\n"
        f"Public records: {integer(row.get('pub_rec'))}"
    )


def build_opinion(row):
    status = row.get("loan_status")
    approved = status == POSITIVE_STATUS
    strengths, factors = risk_factors(row)
    fico = classify_fico(to_float(row.get("fico_range_low")))
    decision = "Approve" if approved else "Deny"
    risk = "low to moderate" if approved else "high"

    strengths_text = "; ".join(strengths) if strengths else "there are no relevant strengths in the analyzed fields"
    factors_text = "; ".join(factors) if factors else "the main reported indicators do not show severe restrictions"
    conclusion = (
        "The historical contract was fully repaid, so the profile is suitable for approval, "
        "with regular monitoring of repayment capacity."
        if approved
        else
        "The historical contract resulted in a loss, so the profile should be declined or subject to strong mitigants."
    )

    return {
        "recommendation": decision,
        "risk": risk,
        "opinion": (
            f"Recommendation: {decision}. Estimated risk is {risk}. "
            f"The applicant has {fico}, DTI of {percent(row.get('dti'))}, "
            f"annual income of {money(row.get('annual_inc'))}, and requested amount of {money(row.get('loan_amnt'))} "
            f"for {translate_purpose(row.get('purpose'))}. Strengths: {strengths_text}. "
            f"Risk factors: {factors_text}. {conclusion}"
        ),
    }


def reservoir_add(bucket, row, seen, target, rng):
    seen += 1
    if len(bucket) < target:
        bucket.append(dict(row))
    else:
        index = rng.randrange(seen)
        if index < target:
            bucket[index] = dict(row)
    return seen


def sample_rows(input_path, per_class, seed):
    rng = random.Random(seed)
    positive = []
    negative = []
    positive_seen = 0
    negative_seen = 0

    with input_path.open(newline="", encoding="utf-8", errors="replace") as csv_file:
        reader = csv.DictReader(csv_file)
        missing = [column for column in COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing columns in CSV: {', '.join(missing)}")

        for row in reader:
            status = row.get("loan_status")
            if status == POSITIVE_STATUS:
                positive_seen = reservoir_add(positive, row, positive_seen, per_class, rng)
            elif status == NEGATIVE_STATUS:
                negative_seen = reservoir_add(negative, row, negative_seen, per_class, rng)

    if len(positive) < per_class or len(negative) < per_class:
        raise ValueError(
            f"Insufficient sample: {len(positive)} positive and {len(negative)} negative records for target {per_class}."
        )

    rows = positive + negative
    rng.shuffle(rows)
    return rows, positive_seen, negative_seen


def write_jsonl(rows, output_path):
    system = (
        "You are a credit analyst. Generate objective credit opinions in English, "
        "do not invent missing data, and use only the information provided."
    )
    with output_path.open("w", encoding="utf-8", newline="") as jsonl_file:
        for row in rows:
            record = {
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": build_input(row)},
                    {"role": "assistant", "content": json.dumps(build_opinion(row), ensure_ascii=False)},
                ]
            }
            jsonl_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_csv(rows, output_path):
    fields = [
        "label",
        "loan_status",
        "input",
        "recommendation",
        "risk",
        "opinion",
        *[column for column in COLUMNS if column != "loan_status"],
    ]
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            opinion = build_opinion(row)
            writer.writerow(
                {
                    "label": "good_payer" if row.get("loan_status") == POSITIVE_STATUS else "loss",
                    "loan_status": row.get("loan_status"),
                    "input": build_input(row),
                    "recommendation": opinion["recommendation"],
                    "risk": opinion["risk"],
                    "opinion": opinion["opinion"],
                    **{column: row.get(column, "") for column in COLUMNS if column != "loan_status"},
                }
            )


def parse_args():
    parser = argparse.ArgumentParser(description="Generate credit opinions for fine tuning.")
    parser.add_argument("--input", default="accepted_2007_to_2018Q4.csv", help="Accepted loans CSV.")
    parser.add_argument("--total", type=int, default=2000, help="Total number of examples to generate. Must be even.")
    parser.add_argument("--seed", type=int, default=42, help="Sampling seed.")
    parser.add_argument("--jsonl", default="credit_opinions_2000.jsonl", help="Output JSONL file.")
    parser.add_argument("--csv", default="credit_opinions_2000.csv", help="Audit CSV file.")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.total <= 0 or args.total % 2 != 0:
        raise SystemExit("--total must be an even number greater than zero.")

    input_path = Path(args.input)
    rows, positive_seen, negative_seen = sample_rows(input_path, args.total // 2, args.seed)
    write_jsonl(rows, Path(args.jsonl))
    write_csv(rows, Path(args.csv))
    print(f"Generated {len(rows)} examples.")
    print(f"Eligible base found: {positive_seen} Fully Paid and {negative_seen} Charged Off.")
    print(f"JSONL: {args.jsonl}")
    print(f"CSV: {args.csv}")


if __name__ == "__main__":
    main()
