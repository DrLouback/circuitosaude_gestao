import pandas as pd

def add_month_recebimento(df: pd.DataFrame):
    df = df
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], dayfirst=True, errors='coerce')
    df['data_recebimento'] = pd.to_datetime(df['data_recebimento'], errors='coerce', dayfirst=True)
    df['mes_recebimento'] = df['data_recebimento'].dt.month
    return df

def add_month_pagamento(df: pd.DataFrame):
        df['data_pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce', dayfirst = True)
        df['mes_pagamento'] = df['data_pagamento'].dt.month
        return df