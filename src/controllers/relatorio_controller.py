from src.controllers.dados_financeiros import (
    contar_clientes, somar_valores_recebidos, somar_valores_faturados,
    despesas_por_categoria, despesas_por_fornecedor, despesas_por_centro_custo,
    despesas_por_forma, fluxo_caixa_total, evolucao_fluxo_caixa, clientes_unicos_por_mes
)

def get_total_clientes(df, mes=None):
    return contar_clientes(df, mes)

def get_total_clientes_mes(df, mes=None):
    return clientes_unicos_por_mes(df)
    

def get_recebimentos_totais(df, mes=None):
    return somar_valores_recebidos(df, mes)

def get_pagamentos_totais(df, mes=None):
    return somar_valores_faturados(df, mes)

def get_despesas_categoria(df, mes=None):
    return despesas_por_categoria(df, mes)

def get_despesas_fornecedor(df, mes=None):
    return despesas_por_fornecedor(df, mes)

def get_despesas_centro_custo(df, mes=None):
    return despesas_por_centro_custo(df, mes)

def get_despesas_forma(df, mes=None):
    return despesas_por_forma(df, mes)


