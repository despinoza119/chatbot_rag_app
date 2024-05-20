from dotenv import load_dotenv
import pandas as pd
import numpy as np
import torch
from sentence_transformers import util, SentenceTransformer
import streamlit as st
from openai import OpenAI

api_key=['OPENAI_API_KEY']

device = "cpu"
embeddings_df_save_path = "data/text_chunks_and_embeddings_abastores.csv"

# Import text and embedding df
text_chunks_and_embedding_df=pd.read_csv(embeddings_df_save_path)

# Convert embedding column back to np.array (it got converted to string when it saved to CSV)
text_chunks_and_embedding_df["embedding"] = text_chunks_and_embedding_df["embedding"].apply(lambda x: np.fromstring(x.strip("[]"),sep=" "))

# Convert our embeddings into a torch.tensor
embeddings = torch.tensor(np.stack(text_chunks_and_embedding_df["embedding"].tolist(),axis=0),dtype=torch.float32).to(device)

# Convert texts and embedding df to list of dicts
pages_and_chunks = text_chunks_and_embedding_df.to_dict(orient="records")

embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2",
                                      device=device)


import textwrap
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def print_wrapped(text,wrap_length=80):
  wrapped_text = textwrap.fill(text,wrap_length)
  print(wrapped_text)
    
def retrieve_relevant_resources(query: str,
                                embeddings: torch.tensor,
                                pages_and_chunks,
                                model: SentenceTransformer=embedding_model,
                                n_resources_to_return: int=5,
                                print_time: bool=True):
    """
    Embeds a query with model and returns top k scores and indices from embeddings.
    """

    # Embed the query
    query_embedding = model.encode(query,
                                   convert_to_tensor=True)
    
    dot_scores = util.dot_score(a=query_embedding, b=embeddings)[0]
    text_chunk_strings = [item["sentence_chunk"] for item in pages_and_chunks]
    vectorizer = CountVectorizer()
    text_chunk_bow = vectorizer.fit_transform(text_chunk_strings)
    query_bow = vectorizer.transform([query])
    bow_scores = cosine_similarity(query_bow, text_chunk_bow)[0]

    dot_weight = 0.7  # Weight for dot product similarity scores
    bow_weight = 0.3  # Weight for BoW similarity scores
    final_scores = dot_weight * dot_scores + bow_weight * bow_scores

    
    # Get dot product scores on embeddings
    dot_scores = util.dot_score(query_embedding, embeddings)[0]

    #if print_time:
        #print(f"[INFO] Time taken to get scores on {len(embeddings)} embeddings: {end_time-start_time:.5f} seconds.")

    scores, indices = torch.topk(input=final_scores,
                                 k=n_resources_to_return)

    return scores, indices

def print_top_results_and_scores(query: str,
                                 embeddings: torch.tensor,
                                 pages_and_chunks: list[dict]=pages_and_chunks,
                                 n_resources_to_return: int=5):
    """
    Takes a query, retrieves most relevant resources and prints them out in descending order.

    Note: Requires pages_and_chunks to be formatted in a specific way (see above for reference).
    """

    scores, indices = retrieve_relevant_resources(query=query,
                                                  embeddings=embeddings,pages_and_chunks=pages_and_chunks,
                                                  n_resources_to_return=n_resources_to_return)

    return pages_and_chunks[indices[0]]["sentence_chunk"],pages_and_chunks[indices[0]]["first_line"]

def Home():
    st.markdown("<h1 style='text-align: center;'>Demo</h1>", unsafe_allow_html=True)
    #st.markdown("Descubre la potencia de nuestro demo, donde puedes realizar consultas sobre precios de cultivo. Sumérgete en la experiencia de obtener insights con gráficos en tiempo real, ofreciéndote una visión dinámica y detallada de tus datos. ¡Explora las posibilidades y toma decisiones informadas de manera intuitiva con nuestra solución web!")
    #st.markdown("Explore the power of our demo, where you can make queries about crop prices. Immerse yourself in the experience of gaining insights with real-time graphs, providing you with a dynamic and detailed view of your data. Discover the possibilities and make informed decisions intuitively with our web solution!")
    
    st.sidebar.markdown("<h1 style='text-align: center; font-size: small;'>Powered by AGIA®</h1>", unsafe_allow_html=True)


def Chat():
    st.title("Abastores Assistant")
    st.write("¡Bienvenido al ChatBot! Aquí puedes hacer preguntas sobre datos y análisis relacionados con Precios de Cultivos. "
         "Recuerda que el ChatBot está en fase de pruebas, por lo que puede que no tenga respuestas para todas las preguntas.")

    client=OpenAI()

    def consulta(query):
        topic, text = print_top_results_and_scores(query=query, embeddings=embeddings)

        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "assistant", "content": "Eres un experto analista parte de una organizacion llamada Abastores que se encarga de responder preguntas de usuario relacionadas al precio de ciertos granos que se venden en tu plataforma"},
                {"role": "system", "content": f"Toda pregunta debe ser respondida en base a la siguiente data, siempre y cuando la metadata se relacione a la pregunta del usuario (si no se relaciona contestar como si fueras chatgpt normal):"},
                {"role": "system", "content": f"La metadata de la data que te brindo debajo es la siguiente: {topic}, incluye la metadata en la respuesta para que el usuario sepa de que provincia, fuente de datos es la informacion siempre y cuando sea relacionado a la pregunta del usuario"},
                {"role": "system", "content": f"Esta es la data: {text}"},
                {"role": "system", "content": f"La pregunta del usuario es esta: {query}, si ves que la pregunta no tiene relacion con la metadata, puedes responder en base a la respuesta anterior en caso este relacionada la pregunta, sino pide que porfavor reformulen la pregunta"},
                {"role": "system", "content": f"Algunas cosas que considerar: precios en euros por tonelada, da la informacion como bullet points y usa un lenguaje profesional, no devuelvas datos incluye un pequeño texto, luego un pequeño resumen como texto"},
            ],
            stream=False,
        )

        responses = []
        print(stream)
        return stream.choices[0].message.content
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input()

    if prompt:
        with st.chat_message("You"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "Abastores", "content": prompt})

        response = consulta(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)
            st.session_state.messages.append({"role": "Abastores", "content": response})

page_name_to_funcs = {
    "Home": Home,
    "Chat": Chat,
}

selected_page = st.sidebar.selectbox("Go to", list(page_name_to_funcs.keys()))
page_name_to_funcs[selected_page]()