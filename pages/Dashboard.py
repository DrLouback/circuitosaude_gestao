import pandas as pd
import streamlit as st
from src.db.db import engine

unidade = st.segmented_control('Unidade', ['MOK','Shopping'], default='MOK')
mes = st.segmented_control('Mês', [5,6,7,8,9,10,11,12], default=7)
receitas = pd.read_sql(f"""select sum(valor_bruto) + (select sum(valor) from contas_receber where mes_pagamento = {mes} and unidade = '{unidade}' and forma not in ('Cartão de crédito', 'Cartão de débito'))  from stone where mes_venda = {mes} and unidade = '{unidade}'""", engine)

despesas_sem_comissões = pd.read_sql_query(f"""select * from contas_pagar
where unidade = '{unidade}'
and titulo not in  ('Comissão')
and mes_pagamento = {mes}""", engine)

despesas_com_comissões = pd.read_sql_query(f"""select * from contas_pagar
where unidade = '{unidade}'
and titulo = 'Comissão'
and mes_pagamento = {int(mes)+1}""", engine) #type: ignore

despesas = pd.concat([despesas_com_comissões, despesas_sem_comissões])


seufisio_recebido = pd.read_sql(f"""
    SELECT
        SUM(valor) AS valor_recebido_sf,
        mes_recebimento AS mes
    FROM contas_receber
    WHERE
        forma NOT IN ('Cartão de crédito', 'Cartão de débito')
        AND mes_recebimento IS NOT NULL
        AND unidade = '{unidade}'
    GROUP BY mes_recebimento
""", engine)

stone_recebido = pd.read_sql_query(f"""
    SELECT
        SUM(valor_bruto) AS valor_recebido_stone,
        mes_vencimento AS mes
    FROM stone
    WHERE
        unidade = '{unidade}'
    GROUP BY mes_vencimento
""", engine)

seufisio_pagas = pd.read_sql(f"""
    SELECT
        SUM(valor) AS valor_pago_sf,
        mes_pagamento AS mes
    FROM contas_pagar
    WHERE
        unidade = '{unidade}'
    GROUP BY mes_pagamento
""", engine)


def categorizar(row):
    titulo = str(row['titulo']).lower()
    fornecedor = str(row['fornecedor']).lower()

    if any(x in titulo for x in ['material', 'limpeza', 'condomínio', 'luz', 'manutenção', 'sistema de informática', 'telefone']):
        return 'Despesas Operacionais'
    elif any(x in titulo for x in ['comissão', 'salário']):
        return 'Despesas com Pessoal'
    elif any(x in titulo for x in [ 'mensalidade', 'venda']):
        return 'Receita'
    elif 'pró-labore' in titulo:
        return 'Pro Labore'
    elif 'contabilidade' in titulo:
        return 'Despesas Administrativas'
    elif 'marketing' in titulo:
        return 'Despesas de Vendas'
    elif 'receita federal' in fornecedor or 'imposto' in titulo:
        return 'Impostos'
    elif 'aplicação financeira' in titulo:
        return 'Despesas Financeiras'
    else:
        return 'Outros'

# Aplicando a função de categorização
despesas['categoria'] = despesas.apply(categorizar, axis=1)

# Somando valores por categoria
agrupado = despesas.groupby('categoria')['valor'].sum()

# Separando valores de receita e despesas
receita_total = receitas.iloc[0,0]
despesas_operacionais = agrupado.get('Despesas Operacionais', 0)
despesas_pessoal = agrupado.get('Despesas com Pessoal', 0)
pro_labore = agrupado.get('Pro Labore', 0)
despesas_adm = agrupado.get('Despesas Administrativas', 0)
despesas_vendas = agrupado.get('Despesas de Vendas', 0)
impostos = agrupado.get('Impostos', 0)
despesas_financeiras = agrupado.get('Despesas Financeiras', 0)
outros = agrupado.get('Outros', 0)



# Cálculos
lucro_bruto = receita_total - (despesas_operacionais + despesas_pessoal)

# Lucro Operacional: O cálculo deve subtrair despesas administrativas e de vendas do lucro bruto.

lucro_operacional = lucro_bruto - (despesas_adm + despesas_vendas)

# Lucro Antes dos Impostos: Este é o resultado antes de deduzir o imposto de renda e contribuição social.

lucro_antes_impostos = lucro_operacional - (despesas_financeiras + outros)

# Lucro Líquido Antes das Participações: Subtrai os impostos do lucro antes dos impostos.
lucro_liquido_antes_participacoes = lucro_antes_impostos - impostos

# Lucro Líquido Final: Subtrai o Pro Labore/Participações do lucro líquido antes das participações.
lucro_liquido_final = lucro_liquido_antes_participacoes - pro_labore

dre = pd.DataFrame({
    'Conta': [
        'Receita Bruta',
        '(-) Despesas Operacionais',
        '(-) Despesas com Pessoal',
        'Lucro Bruto',
        '(-) Despesas Administrativas',
        '(-) Despesas de Vendas',
        'Lucro Operacional',
        '(-) Despesas Financeiras',
        '(-) Outros',
        'Lucro Antes de Impostos',
        '(-) Impostos',
        'Lucro Líquido (antes das participações)',
        '(-) Pro Labore / Participações',
        'Lucro Líquido Final'
    ],
    'Valor': [
        receita_total,
        despesas_operacionais,
        despesas_pessoal,
        lucro_bruto,
        despesas_adm,
        despesas_vendas,
        lucro_operacional,
        despesas_financeiras,
        outros,
        lucro_antes_impostos,
        impostos,
        lucro_liquido_antes_participacoes,
        pro_labore,
        lucro_liquido_final
    ]
})


st.dataframe(dre, hide_index=True)



seufisio_recebido.rename(columns={'mes_recebimento': 'mes', 'valor': 'valor_recebido_sf'}, inplace=True)
stone_recebido.rename(columns={'mes_vencimento': 'mes', 'valor_bruto': 'valor_recebido_stone'}, inplace=True)
seufisio_pagas.rename(columns={'mes_pagamento': 'mes', 'valor': 'valor_pago_sf'}, inplace=True)

# Unir os dataframes
df_recebimentos = pd.merge(seufisio_recebido, stone_recebido, on='mes', how='outer')
df_completo = pd.merge(df_recebimentos, seufisio_pagas, on='mes', how='outer')

# Preencher valores nulos com zero, para não atrapalhar os cálculos
df_completo = df_completo.fillna(0)

df_completo = df_completo[df_completo['mes'] >= 5]

# Calcular total de recebimentos e pagamentos
df_completo['total_recebimentos'] = df_completo['valor_recebido_sf'] + df_completo['valor_recebido_stone']
df_completo['total_pagamentos'] = df_completo['valor_pago_sf']

# Calcular o fluxo de caixa do mês
df_completo['fluxo_caixa_mensal'] = df_completo['total_recebimentos'] - df_completo['total_pagamentos']

# Ordenar por mês
df_completo.sort_values(by='mes', inplace=True)

# Adicionar Saldo Inicial e Lucro Acumulado
# Inicializar o saldo acumulado com zero para o primeiro mês.
saldo_acumulado = 0
saldo_inicial_lista = []
saldo_acumulado_lista = []

for fluxo in df_completo['fluxo_caixa_mensal']:
    saldo_inicial_lista.append(saldo_acumulado)
    saldo_acumulado += fluxo
    saldo_acumulado_lista.append(saldo_acumulado)

df_completo['saldo_inicial'] = saldo_inicial_lista
df_completo['fluxo_caixa_mensal'] = df_completo['total_recebimentos'] - df_completo['total_pagamentos']
df_completo['lucro_acumulado'] = saldo_acumulado_lista

# Criar a tabela final de fluxo de caixa
fluxo_caixa_final = df_completo[['mes', 'saldo_inicial', 'total_recebimentos', 'total_pagamentos', 'fluxo_caixa_mensal','lucro_acumulado']].copy()

# Opcional: Renomear colunas para melhor visualização
fluxo_caixa_final.columns = ['Mês', 'Saldo Inicial', 'Total de Recebimentos', 'Total de Pagamentos','Lucro do Mês', 'Lucro Acumulado']

st.dataframe(fluxo_caixa_final, hide_index=True)