import streamlit as st
from utils.openai_chatbot import OpenAIChatClient
from openai import OpenAI
from utils.prompts import PROMPT_ABASTORES,PROMPT_ABASTORES_DATA
import sqlite3
import requests # requests para hablar con el api


def get_query_params():
    query_params = st.query_params()
    st.write("Parámetros de consulta:", query_params)
    token = query_params.get('token', [''])[0]
    st.write("Token:", token)
    return token

def Home():
    st.markdown("<h1 style='text-align: center;'>Demo</h1>", unsafe_allow_html=True)
    #st.markdown("Descubre la potencia de nuestro demo, donde puedes realizar consultas sobre precios de cultivo. Sumérgete en la experiencia de obtener insights con gráficos en tiempo real, ofreciéndote una visión dinámica y detallada de tus datos. ¡Explora las posibilidades y toma decisiones informadas de manera intuitiva con nuestra solución web!")
    #st.markdown("Explore the power of our demo, where you can make queries about crop prices. Immerse yourself in the experience of gaining insights with real-time graphs, providing you with a dynamic and detailed view of your data. Discover the possibilities and make informed decisions intuitively with our web solution!")
    
    st.sidebar.markdown("<h1 style='text-align: center; font-size: small;'>Powered by AGIA®</h1>", unsafe_allow_html=True)


def Chat():
    st.title("Abastores Assistant")
    st.write("¡Bienvenido al ChatBot! Aquí puedes hacer preguntas sobre datos y análisis relacionados con Precios de Cultivos. "
         "Recuerda que el ChatBot está en fase de pruebas, por lo que puede que no tenga respuestas para todas las preguntas.")

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
        
        # Call a endpoint que
        # input(prompt del usuario) -> lo que escribio a traves del chat (frontend)
        # 1. recibe el prompt del usuario 
        # 2. devuelve un query
        # 3. lo ejecuta y devuelve la info de la base de datos.
        # 4. luego con esta data vuelve a hacer call al llm para dar la respuest final
        # output(lo que devuele el endpoint)

        # Llamar al endpoint para obtener la respuesta
        response = requests.post('http://abastores/chat/rag/', json={"prompt": prompt,"token":token})
        if response.status_code == 200:
            response_text = response.json().get('response', "Error al generar la respuesta.")
        else:
            response_text = "Error al generar la respuesta."

        with st.chat_message("assistant"):
            st.markdown(response_text)
            st.session_state.messages.append({"role": "Abastores", "content": response_text})


page_name_to_funcs = {
    "Home": Home,
    "Chat": Chat,
}

token = get_query_params()
selected_page = st.sidebar.selectbox("Go to", list(page_name_to_funcs.keys()))
page_name_to_funcs[selected_page]()