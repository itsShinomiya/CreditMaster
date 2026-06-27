import pandas as pd

# Carregar o dataset
df_bruto = pd.read_csv('accepted_2007_to_2018Q4.csv', low_memory=False)

# As colunas que vão virar texto para o modelo
colunas_selecionadas = [
    'loan_amnt', 'term', 'emp_title', 'emp_length', 'home_ownership',
    'annual_inc', 'purpose', 'dti', 'fico_range_low', 'delinq_2yrs',
    'inq_last_6mths', 'loan_status'
]

df_filtrado = df_bruto[colunas_selecionadas]

# Filtrar apenas os empréstimos que já terminaram (Pago ou Calote)
df_final = df_filtrado[df_filtrado['loan_status'].isin(['Fully Paid', 'Charged Off'])]
