import pandas as pd
import pdfplumber

def extract_pdf(data):

    """Extract datas for each line in archive .pdf"""
    
    data_extracted = []

    with pdfplumber.open(data) as pdf:
        for page in pdf.pages:
            
            tables = page.extract_tables()
            if tables:
                for line in tables[0]:
                    data_extracted.append(line)

    df = pd.DataFrame(data_extracted[1:], columns=data_extracted[0])
    df.reset_index(inplace= True)
    return df