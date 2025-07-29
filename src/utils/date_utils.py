import pandas as pd
import numpy as np

def add_month_recebimento(df: pd.DataFrame):
    df = df
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], dayfirst=True, errors='coerce')
    df['data_recebimento'] = pd.to_datetime(df['data_recebimento'], errors='coerce', dayfirst=True)
    df['mes_recebimento'] = np.where(
    df['forma'] == "Cartão de crédito",
    (df['data_recebimento'] + pd.Timedelta(days=30)).dt.month,
    df['data_recebimento'].dt.month)
    
    return df

def add_month_pagamento(df: pd.DataFrame):
        df['data_pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce', dayfirst = True)
        df['mes_pagamento'] = df['data_pagamento'].dt.month
        return df