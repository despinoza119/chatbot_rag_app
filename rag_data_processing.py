import pandas as pd
import numpy as np
import re
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

def convert_to_strings(row):

    # Define mappings
    dia_mapping = {
        1: 'uno',
        2: 'dos',
        3: 'tres',
        4: 'cuatro',
        5: 'cinco',
        6: 'seis',
        7: 'siete',
        8: 'ocho',
        9: 'nueve',
        10: 'diez',
        11: 'once',
        12: 'doce',
        13: 'trece',
        14: 'catorce',
        15: 'quince',
        16: 'dieciséis',
        17: 'diecisiete',
        18: 'dieciocho',
        19: 'diecinueve',
        20: 'veinte',
        21: 'veintiuno',
        22: 'veintidós',
        23: 'veintitrés',
        24: 'veinticuatro',
        25: 'veinticinco',
        26: 'veintiséis',
        27: 'veintisiete',
        28: 'veintiocho',
        29: 'veintinueve',
        30: 'treinta',
        31: 'treinta y uno'
    }

    mes_mapping = {
        1: 'enero',
        2: 'febrero',
        3: 'marzo',
        4: 'abril',
        5: 'mayo',
        6: 'junio',
        7: 'julio',
        8: 'agosto',
        9: 'septiembre',
        10: 'octubre',
        11: 'noviembre',
        12: 'diciembre'
    }

    anio_mapping = {
        2000: 'dos mil',
        2001: 'dos mil uno',
        2002: 'dos mil dos',
        2003: 'dos mil tres',
        2004: 'dos mil cuatro',
        2005: 'dos mil cinco',
        2006: 'dos mil seis',
        2007: 'dos mil siete',
        2008: 'dos mil ocho',
        2009: 'dos mil nueve',
        2010: 'dos mil diez',
        2011: 'dos mil once',
        2012: 'dos mil doce',
        2013: 'dos mil trece',
        2014: 'dos mil catorce',
        2015: 'dos mil quince',
        2016: 'dos mil dieciséis',
        2017: 'dos mil diecisiete',
        2018: 'dos mil dieciocho',
        2019: 'dos mil diecinueve',
        2020: 'dos mil veinte',
        2021: 'dos mil veintiuno',
        2022: 'dos mil veintidós',
        2023: 'dos mil veintitrés',
        2024: 'dos mil veinticuatro'
    }

    dia_str = dia_mapping[row['dia']]
    mes_str = mes_mapping[row['mes']]
    anio_str = anio_mapping[row['anio']]

    return pd.Series([dia_str, mes_str, anio_str])


def data_processing (df):
    # Select the columns we are going to use from the total dataframe.
    df_ = df[['date','product.meta_product.name','price','data_source.name','province.name']]

    # Create new columns with day, month and year.
    df_['dia']=pd.to_datetime(df_['date']).dt.day
    df_['mes']=pd.to_datetime(df_['date']).dt.month
    df_['anio']=pd.to_datetime(df_['date']).dt.year

    # Create new columns to store string date values.
    df_['dia_str']=''
    df_['mes_str']=''
    df_['anio_str']=''

    # Apply the conversion function to each row of the dataframe.
    df_[['dia_str', 'mes_str', 'anio_str']] = df_[['dia', 'mes', 'anio']].apply(convert_to_strings, axis=1)

    # Create the first data store column "first_line" that will store price values.
    df_['first_line'] = ''

    # Storing Price for each date.
    df_['first_line'] = df_.apply(lambda row: 
        f'precio: {row["price"]} fecha: {row["date"]}', 
        axis=1)
    
    # We group the data per each month,year,product,data_source and province.
    grouped_chunks = df_.groupby(['mes', 'anio',\
                                'mes_str','anio_str',\
                                'product.meta_product.name',\
                                'data_source.name','province.name']).agg({
                                'first_line': ' '.join,
                                }).reset_index()
    
    # We create a new columm "title" that will store the meta-data for the RAG model.
    grouped_chunks['title']=''

    # We apply the conversion function to each row of the dataframe.
    grouped_chunks['title'] = grouped_chunks.apply(lambda row: 
                            f'Provincia: {row["province.name"]} '
                            f'Producto: {row["product.meta_product.name"]} '
                            f'Fuente de datos: {row["data_source.name"]} '
                            f'Fecha: mes: {row["mes"]}-{row["mes_str"]} '
                            f'año: {row["anio"]}-{row["anio_str"]}',
                            axis=1)


    df_chunk=grouped_chunks[['title','first_line','mes','anio','province.name','product.meta_product.name']]

    return df_chunk

def create_pages_and_chunks(df_chunk):
    # Create a variable to save the pages and chunks.
    pages_and_chunks = []

    for index, row in tqdm(df_chunk.iterrows(), total=len(df_chunk)):
        chunk_dict = {}
        joined_sentence_chunk = row['title'].replace(" ", " ").strip()
        joined_sentence_chunk = re.sub(r'\.([A-Z])', r'. \1', joined_sentence_chunk)
        
        chunk_dict["sentence_chunk"] = joined_sentence_chunk
        chunk_dict["first_line"] = row["first_line"]
        chunk_dict["chunk_char_count"] = len(joined_sentence_chunk)
        chunk_dict["chunk_word_count"] = len(joined_sentence_chunk.split(" "))
        chunk_dict["chunk_token_count"] = len(joined_sentence_chunk) / 4  # 1 token =~ 4 chars

        # Add 'mes' and 'anio' columns from df_chunk to chunk_dict
        chunk_dict["mes"] = row["mes"]
        chunk_dict["anio"] = row["anio"]
        chunk_dict["producto"] = row["product.meta_product.name"]
        chunk_dict["provincia"] = row["province.name"]
        
        pages_and_chunks.append(chunk_dict)

    # Save the data to the postgresql database.
    return pages_and_chunks

def embedding_model(pages_and_chunks_df):

    embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2", device="cpu")

    for item in tqdm(pages_and_chunks_df):
        item['embedding'] = embedding_model.encode(item["sentence_chunk"])

    return pages_and_chunks_df