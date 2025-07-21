import pandas as pd

def agrupar_por_coluna(df, mes, coluna):
    if mes and mes != 'Sem Filtro':
        df = df[df['mes_pagamento'] == int(mes)]
    return df.groupby(coluna)['valor'].sum().reset_index()

def calcular_percentual(df, campo):
    df_agrupado = df.groupby(campo)['valor'].sum().reset_index()
    df_agrupado['Percentual'] = df_agrupado['valor'].pct_change() * 100
    df_agrupado['Percentual'] = df_agrupado['Percentual'].round(2)
    df_agrupado['Percentual_str'] = df_agrupado['Percentual'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")
    return df_agrupado

def filtrar_por_mes(df, campo_mes, mes):
    if mes != 'Sem Filtro':
        return df[df[campo_mes] == int(mes)]
    return df

def contar_clientes(df:pd.DataFrame, mes=None):
    df_pagaram = df[df['valor'] > 0]
    df_filtrado = filtrar_por_mes(df_pagaram, 'mes_pagamento', mes)
    return df_filtrado['cliente'].nunique()

def clientes_unicos_por_mes(df):
    # Agrupa por mes_pagamento e conta clientes únicos
    clientes_mes = df.groupby('mes_pagamento')['cliente'].nunique().reset_index(name='clientes')
    # Transpõe para que cada coluna seja um mês
    clientes_mes = clientes_mes.set_index('mes_pagamento').T
    return clientes_mes

def somar_valores_recebidos(df, mes=None):
    df_recebido = df[df['data_recebimento'].notnull()]
    df_recebido = filtrar_por_mes(df_recebido, 'mes_recebimento', mes)
    return float(df_recebido['valor'].sum())

def somar_valores_faturados(df, mes=None):
    df_pago = df[df['data_pagamento'].notnull()]
    df_pago = filtrar_por_mes(df_pago, 'mes_pagamento', mes)
    return float(df_pago['valor'].sum())

def despesas_por_categoria(df, mes=None):
    return agrupar_por_coluna(df, mes, 'categoria')

def despesas_por_fornecedor(df, mes=None):
    return agrupar_por_coluna(df, mes, 'fornecedor')

def despesas_por_centro_custo(df, mes=None):
    return agrupar_por_coluna(df, mes, 'centro_de_custo')

def despesas_por_forma(df, mes=None):
    return agrupar_por_coluna(df, mes, 'forma')

def fluxo_caixa_total(receber_df, pagar_df, mes=None):
    entradas = somar_valores_recebidos(receber_df, mes)
    saidas = somar_valores_faturados(pagar_df, mes)
    saldo = entradas - saidas
    return {'Entradas': entradas, 'Saídas': saidas, 'Saldo': saldo}

def evolucao_fluxo_caixa(receber_df, pagar_df):
    entradas = receber_df.groupby('mes_recebimento')['valor'].sum().reset_index(name='Entradas')
    saidas = pagar_df.groupby('mes_pagamento')['valor'].sum().reset_index(name='Saídas')
    df_merged = pd.merge(entradas, saidas, left_on='mes_recebimento', right_on='mes_pagamento', how='outer')
    df_merged['mes'] = df_merged['mes_recebimento'].combine_first(df_merged['mes_pagamento'])
    df_merged['Saldo'] = df_merged['Entradas'].fillna(0) - df_merged['Saídas'].fillna(0)
    df_merged = df_merged[['mes', 'Entradas', 'Saídas', 'Saldo']].sort_values('mes')
    df_merged = df_merged.set_index('mes').T  # Transpõe: meses viram colunas
    return df_merged