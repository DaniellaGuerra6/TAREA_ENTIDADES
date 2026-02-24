# cleaner.py
import re
import unicodedata
import pandas as pd

def estandarizar_texto(texto):
    if pd.isna(texto):
        return texto

    texto = texto.lower()
    texto = re.sub(r'[.,;:]', '', texto)
    texto = re.sub(r'[\"“”\'’]', '', texto)
    texto = re.sub(r'[°*+]', ' ', texto)

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn" or ch == "ñ")

    texto = re.sub(r'\d+', '', texto)
    texto = re.sub(r'[^a-zñ\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto