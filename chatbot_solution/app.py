import streamlit as st
from utils.openai_chatbot import OpenAIChatClient
from openai import OpenAI
from utils.prompts import PROMPT_ABASTORES,PROMPT_ABASTORES_DATA
import sqlite3
from dotenv import load_dotenv
api_key=['OPENAI_API_KEY']

def retrieve_info_from_database(prompt):
    try:
        conn = sqlite3.connect('data/abastores.db')
        cursor = conn.cursor()

        client = OpenAIChatClient()
        query=client.ask(prompt,context=PROMPT_ABASTORES,model="gpt-4")

        cursor.execute(query)
        db_data = cursor.fetchall()
        cursor.close() 
        conn.close()  

        if db_data == []:
            return "No se encontraron resultados para la consulta realizada."
        else:
            return db_data
    
    except sqlite3.Error as e:
        cursor.close() 
        conn.close() 
        print("Error al ejecutar el query de selección:", e)
        return None 
    
def generate_answer(prompt,augmented_data):
    client_2 = OpenAIChatClient()
    response=client_2.ask_with_data(prompt,augmented_data,context=PROMPT_ABASTORES_DATA,model="gpt-4")
    return response

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

        augmented_data = retrieve_info_from_database(prompt)
        response = generate_answer(prompt,augmented_data)

        with st.chat_message("assistant"):
            st.markdown(response)
            st.session_state.messages.append({"role": "Abastores", "content": response})


page_name_to_funcs = {
    "Home": Home,
    "Chat": Chat,
}

selected_page = st.sidebar.selectbox("Go to", list(page_name_to_funcs.keys()))
page_name_to_funcs[selected_page]()