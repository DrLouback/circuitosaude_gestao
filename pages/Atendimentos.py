import streamlit as st
import pandas as pd
from src.db.db import engine
from io import BytesIO

unidade = st.selectbox("Unidade", ['MOK', 'Shopping'])
mes = st.selectbox("Mês", [1,2,3,4,5,6,7,8,9,10,11,12])

@st.cache_data
def converter_xlsx(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def baixar_arquivo(df, mes, tabela):
    df = converter_xlsx(df)
    st.download_button("Download", data= df, file_name=f'{tabela}_{mes}.xlsx')

experimentais = pd.read_sql(f"""SELECT DISTINCT 
    "Cliente", 
    "Tipo Atendimento", 
    data, 
    EXTRACT(MONTH FROM data) AS mes,   -- 🔹 coluna mês
    unidade
FROM atendimentos
WHERE "Cliente" IN (
    SELECT "Cliente" 
    FROM atendimentos 
    WHERE "Tipo Atendimento" = 'Pilates Experimental'
)
AND "Tipo Atendimento" = 'Pilates Experimental'
AND unidade = '{unidade}'
AND EXTRACT(MONTH FROM data) = {mes}   -- 🔹 filtro por mês
ORDER BY data;

""", engine)


experimentais_matriculadas = pd.read_sql(f"""WITH primeira_ocorrencia AS (
    SELECT 
        "Cliente",
        "Tipo Atendimento",
        data,
        unidade,
        ROW_NUMBER() OVER (
            PARTITION BY "Cliente" 
            ORDER BY data ASC
        ) AS rn
    FROM atendimentos
    WHERE "Cliente" IN (
        SELECT "Cliente"
        FROM atendimentos
        WHERE "Tipo Atendimento" = 'Pilates Experimental'
    )
    AND "Tipo Atendimento" NOT IN ('Pilates Experimental')
)
SELECT 
    "Cliente",
    "Tipo Atendimento",
    data,
    EXTRACT(MONTH FROM data) AS mes,   -- 🔹 coluna mês
    unidade
FROM primeira_ocorrencia
WHERE rn = 1 
  AND unidade = '{unidade}'
  AND EXTRACT(MONTH FROM data) = {mes}   -- 🔹 filtro por mês
ORDER BY data; ;""", engine)

delay_matricula = pd.read_sql(f"""WITH experimental AS (
    SELECT 
        "Cliente",
        unidade,
        MIN(data) AS data_experimental
    FROM atendimentos
    WHERE "Tipo Atendimento" = 'Pilates Experimental' 
    GROUP BY "Cliente", unidade
),
primeira_aula AS (
    SELECT 
        "Cliente",
        "Tipo Atendimento",
        data,
        unidade,
        ROW_NUMBER() OVER (
            PARTITION BY "Cliente"
            ORDER BY data ASC
        ) AS rn
    FROM atendimentos
    WHERE "Tipo Atendimento" <> 'Pilates Experimental'
)
SELECT 
    p."Cliente",
    p."Tipo Atendimento",
    p.data AS data_primeira_aula,
    e.data_experimental,
    (p.data - e.data_experimental) AS dias_ate_primeira_aula,
    p.unidade
FROM primeira_aula p
JOIN experimental e 
    ON p."Cliente" = e."Cliente"
WHERE p.rn = 1 and p.unidade = '{unidade}'; """, engine)

faltas = pd.read_sql(f"""select "Cliente", "Profissional", "Status", "Tipo Atendimento", count(*) as quantidade, unidade from atendimentos
where "Status" in ('Não Compareceu', 'Ausência Justificada') and unidade = '{unidade}'
group by
"Cliente", "Profissional", "Status", "Tipo Atendimento", unidade
order by quantidade desc  """, engine)

ex_alunos = pd.read_sql(f""" WITH meses AS (
    SELECT 
        UPPER(TRIM(unaccent(cliente))) AS cliente,
        EXTRACT(MONTH FROM data_vencimento) AS mes,
        EXTRACT(YEAR FROM data_vencimento) AS ano,
        unidade
    FROM contas_receber
    WHERE unidade = '{unidade}'
    GROUP BY cliente, mes, ano, unidade
),
mes_atual AS (
    SELECT 
        UPPER(TRIM(unaccent(cliente))) AS cliente
    FROM contas_receber
    WHERE unidade = '{unidade}'
      AND EXTRACT(MONTH FROM data_vencimento) = EXTRACT(MONTH FROM CURRENT_DATE)
      AND EXTRACT(YEAR  FROM data_vencimento) = EXTRACT(YEAR  FROM CURRENT_DATE)
)
SELECT 
    m1.cliente,
    m1.mes AS mes_origem,
    m1.ano AS ano_origem,
    m1.unidade
FROM meses m1
LEFT JOIN meses m2 
       ON m2.cliente = m1.cliente
      AND (m2.ano * 12 + m2.mes) = (m1.ano * 12 + m1.mes + 1) -- mês seguinte
WHERE m2.cliente IS NULL
  AND m1.cliente NOT IN (SELECT cliente FROM mes_atual)
  AND m1.unidade = '{unidade}'
  AND m1.mes = {mes}   -- 🔹 filtro extra por mês
ORDER BY ano_origem, mes_origem DESC;
""", engine)

alunos_novos = pd.read_sql(f""" WITH primeira_aparicao AS (
    SELECT 
        UPPER(TRIM(unaccent(cliente))) AS cliente,
        EXTRACT(MONTH FROM data_vencimento) AS mes,
        EXTRACT(YEAR  FROM data_vencimento) AS ano,
        ROW_NUMBER() OVER (
            PARTITION BY UPPER(TRIM(unaccent(cliente))) 
            ORDER BY data_vencimento ASC
        ) AS rn,
        unidade
    FROM contas_receber
    WHERE valor > 0
)
SELECT 
    cliente,
    mes AS mes_entrada,
    ano AS ano_entrada,
    unidade 
FROM primeira_aparicao
WHERE rn = 1 
  AND unidade = '{unidade}'
  AND mes = '{mes}'   -- aqui usa mes em vez de mes_entrada
ORDER BY ano_entrada, mes_entrada DESC;
 """, engine)

alunos_professor = pd.read_sql(f""" SELECT 
    "Profissional",
    EXTRACT(YEAR FROM data) AS ano,
    EXTRACT(MONTH FROM data) AS mes,
    COUNT(DISTINCT UPPER(TRIM("Cliente"))) AS qtd_alunos, unidade
FROM atendimentos where unidade = '{unidade}' AND EXTRACT(MONTH FROM data) = '{mes}'
GROUP BY 
    "Profissional",
    EXTRACT(YEAR FROM data),
    EXTRACT(MONTH FROM data), unidade
ORDER BY ano, mes, qtd_alunos DESC ;
""", engine)

alunos_atendimentos = pd.read_sql(f"""SELECT 
    "Tipo Atendimento",
    EXTRACT(YEAR FROM data) AS ano,
    EXTRACT(MONTH FROM data) AS mes,
    COUNT(DISTINCT UPPER(TRIM("Cliente"))) AS qtd_alunos,
                                  unidade
FROM atendimentos
                                  where unidade = '{unidade}' AND EXTRACT(MONTH FROM data) = '{mes}'
GROUP BY 
    "Tipo Atendimento",
    EXTRACT(YEAR FROM data),
    EXTRACT(MONTH FROM data), unidade
ORDER BY ano, mes, qtd_alunos DESC;
 """, engine)

alunos_horario = pd.read_sql(f"""SELECT 
    hora,
    EXTRACT(YEAR FROM data) AS ano,
    EXTRACT(MONTH FROM data) AS mes,
    COUNT(DISTINCT UPPER(TRIM("Cliente"))) AS qtd_alunos,
                             unidade
FROM atendimentos where unidade = '{unidade}' AND EXTRACT(MONTH FROM data) =  '{mes}' 
GROUP BY hora, EXTRACT(YEAR FROM data), EXTRACT(MONTH FROM data), unidade
                            
ORDER BY ano, mes, qtd_alunos DESC;
 """, engine)

st.write("Lista de experimentais realizadas")
st.dataframe(experimentais )

if experimentais is not None:
    baixar_arquivo(experimentais, mes, 'Experimentais')

st.write("Lista de experimentais matriculados")
st.dataframe(experimentais_matriculadas)

if experimentais_matriculadas is not None:
    baixar_arquivo(experimentais_matriculadas, mes, 'Experimentais_Matriculadas')

st.write("Diferença de tempo experimental vs matrícula")
st.dataframe(delay_matricula)

if delay_matricula is not None:
    baixar_arquivo(delay_matricula, mes, 'Tempo_de_matricula')

st.write("Faltas")
st.dataframe(faltas)

if faltas is not None:
    baixar_arquivo(faltas, mes, 'Faltas')

st.write("Ex- alunos")
st.dataframe(ex_alunos)

if ex_alunos is not None:
    baixar_arquivo(ex_alunos, mes, 'Ex_alunos')

st.write("Alunos novos")
st.dataframe(alunos_novos)

if alunos_novos is not None:
    baixar_arquivo(alunos_novos, mes, 'Alunos novos')

st.write("Alunos por professor")
st.dataframe(alunos_professor)

st.write("Alunos por atendimento")
st.dataframe(alunos_atendimentos)

st.write("Horários mais cheios")
st.dataframe(alunos_horario)