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
    "car": "compra de veiculo",
    "credit_card": "refinanciamento de cartao de credito",
    "debt_consolidation": "consolidacao de dividas",
    "educational": "educacao",
    "home_improvement": "reforma residencial",
    "house": "moradia",
    "major_purchase": "compra relevante",
    "medical": "despesas medicas",
    "moving": "mudanca",
    "other": "outra finalidade",
    "renewable_energy": "energia renovavel",
    "small_business": "pequeno negocio",
    "vacation": "viagem",
    "wedding": "casamento",
}

HOME_OWNERSHIP = {
    "ANY": "nao informado",
    "MORTGAGE": "imovel financiado",
    "NONE": "nao informado",
    "OTHER": "outro",
    "OWN": "imovel proprio",
    "RENT": "aluguel",
}


def money(value):
    number = to_float(value)
    if number is None:
        return "nao informado"
    return f"US$ {number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def percent(value):
    number = to_float(value)
    if number is None:
        return "nao informado"
    return f"{number:.2f}%".replace(".", ",")


def integer(value):
    number = to_float(value)
    if number is None:
        return "nao informado"
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
    return value if value else "nao informado"


def translate_purpose(value):
    value = clean_text(value)
    return PURPOSES.get(value, value.replace("_", " "))


def translate_home(value):
    value = clean_text(value).upper()
    return HOME_OWNERSHIP.get(value, value.lower())


def translate_term(value):
    value = clean_text(value)
    if "36" in value:
        return "36 meses"
    if "60" in value:
        return "60 meses"
    return value


def classify_fico(score):
    if score is None:
        return "sem score informado"
    if score >= 760:
        return "score muito forte"
    if score >= 720:
        return "score forte"
    if score >= 680:
        return "score adequado"
    if score >= 640:
        return "score moderado"
    return "score fraco"


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
        factors.append("ausencia de score FICO informado")
    elif fico < 660:
        factors.append("score FICO baixo")
    elif fico >= 720:
        strengths.append("score FICO favoravel")

    if dti is None:
        factors.append("DTI nao informado")
    elif dti > 30:
        factors.append("endividamento elevado pelo DTI")
    elif dti <= 15:
        strengths.append("DTI controlado")

    if delinquencies is not None and delinquencies > 0:
        factors.append("historico recente de inadimplencia")
    elif delinquencies == 0:
        strengths.append("sem atrasos nos ultimos dois anos")

    if inquiries is not None and inquiries >= 3:
        factors.append("muitas consultas recentes de credito")

    if revol_util is not None:
        if revol_util >= 80:
            factors.append("alta utilizacao de credito rotativo")
        elif revol_util <= 35:
            strengths.append("baixa utilizacao de credito rotativo")

    if income and loan and loan / income > 0.45:
        factors.append("valor solicitado alto em relacao a renda anual")
    elif income and loan and loan / income <= 0.20:
        strengths.append("valor solicitado proporcional a renda anual")

    if "60" in term:
        factors.append("prazo longo aumenta exposicao ao risco")

    return strengths[:3], factors[:3]


def build_input(row):
    return (
        "Elabore um parecer de credito objetivo com base nos dados abaixo.\n"
        f"Valor solicitado: {money(row.get('loan_amnt'))}\n"
        f"Prazo: {translate_term(row.get('term'))}\n"
        f"Renda anual: {money(row.get('annual_inc'))}\n"
        f"Finalidade: {translate_purpose(row.get('purpose'))}\n"
        f"Moradia: {translate_home(row.get('home_ownership'))}\n"
        f"Tempo de emprego: {clean_text(row.get('emp_length'))}\n"
        f"DTI: {percent(row.get('dti'))}\n"
        f"FICO minimo: {integer(row.get('fico_range_low'))}\n"
        f"Atrasos em 2 anos: {integer(row.get('delinq_2yrs'))}\n"
        f"Consultas em 6 meses: {integer(row.get('inq_last_6mths'))}\n"
        f"Utilizacao do rotativo: {percent(row.get('revol_util'))}\n"
        f"Contas abertas: {integer(row.get('open_acc'))}\n"
        f"Registros publicos: {integer(row.get('pub_rec'))}"
    )


def build_opinion(row):
    status = row.get("loan_status")
    approved = status == POSITIVE_STATUS
    strengths, factors = risk_factors(row)
    fico = classify_fico(to_float(row.get("fico_range_low")))
    decision = "Aprovar" if approved else "Negar"
    risk = "baixo a moderado" if approved else "elevado"

    strengths_text = "; ".join(strengths) if strengths else "nao ha pontos fortes relevantes nos campos analisados"
    factors_text = "; ".join(factors) if factors else "os principais indicadores informados nao apontam restricoes severas"
    conclusion = (
        "O contrato historico foi quitado, portanto o perfil e aderente para aprovacao, "
        "mantendo acompanhamento regular da capacidade de pagamento."
        if approved
        else
        "O contrato historico evoluiu para perda, portanto o perfil deve ser recusado ou submetido a mitigadores fortes."
    )

    return {
        "recomendacao": decision,
        "risco": risk,
        "parecer": (
            f"Recomendacao: {decision}. Risco estimado {risk}. "
            f"O proponente apresenta {fico}, DTI de {percent(row.get('dti'))}, "
            f"renda anual de {money(row.get('annual_inc'))} e solicitacao de {money(row.get('loan_amnt'))} "
            f"para {translate_purpose(row.get('purpose'))}. Pontos favoraveis: {strengths_text}. "
            f"Pontos de atencao: {factors_text}. {conclusion}"
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
            raise ValueError(f"Colunas ausentes no CSV: {', '.join(missing)}")

        for row in reader:
            status = row.get("loan_status")
            if status == POSITIVE_STATUS:
                positive_seen = reservoir_add(positive, row, positive_seen, per_class, rng)
            elif status == NEGATIVE_STATUS:
                negative_seen = reservoir_add(negative, row, negative_seen, per_class, rng)

    if len(positive) < per_class or len(negative) < per_class:
        raise ValueError(
            f"Amostra insuficiente: {len(positive)} positivos e {len(negative)} negativos para alvo {per_class}."
        )

    rows = positive + negative
    rng.shuffle(rows)
    return rows, positive_seen, negative_seen


def write_jsonl(rows, output_path):
    system = (
        "Voce e um analista de credito. Gere pareceres objetivos em portugues, "
        "sem inventar dados ausentes e usando apenas as informacoes fornecidas."
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
        "entrada",
        "recomendacao",
        "risco",
        "parecer",
        *[column for column in COLUMNS if column != "loan_status"],
    ]
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            opinion = build_opinion(row)
            writer.writerow(
                {
                    "label": "bom_pagador" if row.get("loan_status") == POSITIVE_STATUS else "perda",
                    "loan_status": row.get("loan_status"),
                    "entrada": build_input(row),
                    "recomendacao": opinion["recomendacao"],
                    "risco": opinion["risco"],
                    "parecer": opinion["parecer"],
                    **{column: row.get(column, "") for column in COLUMNS if column != "loan_status"},
                }
            )


def parse_args():
    parser = argparse.ArgumentParser(description="Gera pareceres de credito para fine tuning.")
    parser.add_argument("--input", default="accepted_2007_to_2018Q4.csv", help="CSV de emprestimos aceitos.")
    parser.add_argument("--total", type=int, default=2000, help="Total de exemplos a gerar. Deve ser par.")
    parser.add_argument("--seed", type=int, default=42, help="Semente da amostragem.")
    parser.add_argument("--jsonl", default="pareceres_credito_2000.jsonl", help="Arquivo JSONL de saida.")
    parser.add_argument("--csv", default="pareceres_credito_2000.csv", help="Arquivo CSV de auditoria.")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.total <= 0 or args.total % 2 != 0:
        raise SystemExit("--total deve ser um numero par e maior que zero.")

    input_path = Path(args.input)
    rows, positive_seen, negative_seen = sample_rows(input_path, args.total // 2, args.seed)
    write_jsonl(rows, Path(args.jsonl))
    write_csv(rows, Path(args.csv))
    print(f"Gerados {len(rows)} exemplos.")
    print(f"Base elegivel encontrada: {positive_seen} Fully Paid e {negative_seen} Charged Off.")
    print(f"JSONL: {args.jsonl}")
    print(f"CSV: {args.csv}")


if __name__ == "__main__":
    main()
