# Coding in utf-8
# Develop by Bondol Team

# Copyright 2025 Henri.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# We import the necessary libraries
import time
import streamlit as st
import sqlite3 as sql
import json as js
import datetime
from streamlit_cookies_controller import CookieController

# We set the cookies controller
controller = CookieController()
try:
    # We import functions from other project files
    from functions import response as response_from_frontend
    from functions import save_history
except ImportError as e:
    # If there is an error during import, show a message and define dummy functions to prevent the app from crashing
    st.error(
        f"Error importing functions from FrontEnd.py: {e}. Make sure that the 'response' and 'save_history' functions are importable.")

    # Dummy response function
    def response_from_frontend(prompt, model, historial_list):
        yield "Error de código, reportar a soporte bajo el identificador: NON-RESPONSE-LOAD."
        historial_list.append({"role": "user", "content": prompt})
        historial_list.append({"role": "assistant", "content": "Response not generated."})

    # Dummy save history function
    def save_history(chat_id, name, historial_to_save, model_used, user_name):
        st.error("Error de código, reportar a soporte bajo el identificador: NON-SAVE-LOAD.")
        pass
    st.stop()

# We define the database name
DB_NAME = 'history.db'

# We set the page title
st.title("Historial de conversaciones")


# This function establishes and returns a connection to the database
def get_db_connection():
    conn = sql.connect(DB_NAME)
    return conn


# We check if the user is logged in, either via cookies or session state
if user_name := controller.get('bondolusername') or st.session_state.get('username', None):

    # If the user is authenticated, connect to the database to get their list of conversations
    conn_list = get_db_connection()
    cursor_list = conn_list.cursor()
    # We execute a query to get all conversations for the user, ordered by timestamp descending
    cursor_list.execute("SELECT id, name, model, timestamp FROM history WHERE user = ? ORDER BY timestamp DESC ", (user_name,))
    complete_historial = cursor_list.fetchall()
    conn_list.close()

    # If there are no conversations, we show a warning
    if not complete_historial:
        st.warning("No tienes conversaciones guardadas en este usuario!.")
    else:
        # We create a list of options for the conversation selector
        conversations_options = []
        for row_h in complete_historial:
            # We format the text to be displayed in the selector
            visible_text = f"{row_h[1]} ({row_h[2]}) - {datetime.datetime.strptime(row_h[3], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')}"
            conversations_options.append((visible_text, row_h[0]))  # (display_text, conversation_id)

        # We create the selectbox for the user to choose a conversation
        selected_option = st.selectbox(
            "Selecciona una conversación para continuar:",
            options=conversations_options,
            format_func=lambda option: option[0],
            key="conversation_selector_history_viewer"  # Use a unique key for the widget
        )

        # If the user has selected an option...
        if selected_option:
            # We get the ID of the selected conversation
            selected_chat_id_from_selectbox = selected_option[1]


            # We connect to the database again to get the full details of the conversation
            conn_detail = get_db_connection()
            cursor_detail = conn_detail.cursor()
            cursor_detail.execute(
                "SELECT id, name, model, conversation, timestamp FROM history WHERE id = ? AND user = ?",
                (selected_chat_id_from_selectbox, user_name,))
            selected_chat_data_tuple = cursor_detail.fetchone()
            conn_detail.close()

            # If the conversation data was found...
            if selected_chat_data_tuple:

                # We unpack the conversation data into local variables
                current_chat_db_id = selected_chat_data_tuple[0]
                current_chat_name = selected_chat_data_tuple[1]
                current_chat_model = selected_chat_data_tuple[2]
                current_conversation_blob = selected_chat_data_tuple[3]
                current_chat_timestamp = selected_chat_data_tuple[4]

                # We create a button to delete the current conversation
                if st.button("Eliminar conversación", key=f"delete_chat_{current_chat_db_id}"):
                    try:
                        # We connect and execute the deletion in the database
                        conn_delete = get_db_connection()
                        cursor_delete = conn_delete.cursor()
                        cursor_delete.execute("DELETE FROM history WHERE id = ?", (current_chat_db_id,))
                        conn_delete.commit()
                        conn_delete.close()
                        st.toast(f"Conversación '{current_chat_name}' eliminada.")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error eliminando la conversación: {e}")

                # We show a subheader and a caption with the conversation details
                st.subheader(f"Continuando: {current_chat_name}")
                st.caption(
                    f"ID: {current_chat_db_id} | Modelo: {current_chat_model} | Ultimo cambio: {datetime.datetime.strptime(current_chat_timestamp, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')}")

                # We define unique keys for the session state to prevent conversations from mixing up
                session_key_historial = f"historial_chat_viewer_{current_chat_db_id}"
                session_key_messages_display = f"messages_display_viewer_{current_chat_db_id}"

                # If the history for this chat is not loaded in the session, or if the chat was switched, we load it from the DB
                if session_key_historial not in st.session_state or st.session_state.get(
                        f"loaded_chat_id_viewer") != current_chat_db_id:
                    if current_conversation_blob:
                        try:
                            # We decode the history (which is in BLOB format) to a JSON string
                            json_string = current_conversation_blob.decode('utf-8')
                            # We load the JSON into the session state for internal logic
                            st.session_state[session_key_historial] = js.loads(json_string)
                            # We create a copy to display the messages in the UI
                            st.session_state[session_key_messages_display] = list(
                                st.session_state[session_key_historial])
                        except js.JSONDecodeError:
                            # If the JSON is invalid, show an error and start with an empty history
                            st.error("Error de codificación (invalid JSON). Empezando conversación vacía; reporta este error con el identificador: 'HISTORY-JSON-ERROR'.")
                            st.session_state[session_key_historial] = []
                            st.session_state[session_key_messages_display] = []
                        except Exception as e:
                            # We capture any other errors during loading
                            st.error(f"Error cargando la conversación desde el historial: {e}. Comenzando uno vacio.")
                            st.session_state[session_key_historial] = []
                            st.session_state[session_key_messages_display] = []
                    else:
                        # If there is no history in the DB, we initialize an empty one
                        st.session_state[session_key_historial] = []
                        st.session_state[session_key_messages_display] = []
                    # We save the current chat ID in the session to know which one is active
                    st.session_state[f"loaded_chat_id_viewer"] = current_chat_db_id

                status = None  # Initialize the status variable to None for real-time response updates
                # We display the existing messages from the loaded conversation
                for message in st.session_state.get(session_key_messages_display, []):
                    time.sleep(0.05)  # Small delay to simulate real-time response

                    with st.chat_message(message["role"]) as msg_role:
                        time.sleep(0.05)  # Small delay to simulate real-time response
                        msg = st.empty()  # Create an empty message container to update later
                        if msg_role == "assistant":
                                msg.markdown(i)  # We write the response in the chat, without a new line
                        else:
                            msg.markdown(message["content"])

                # If the user sends a new message...
                if prompt := st.chat_input(f"Escribiendo a: '{current_chat_name}'..."):
                    # We add the user's message to the list of messages to display
                    st.session_state[session_key_messages_display].append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    # We get the active history to pass to the function that generates the response
                    historial_activo_para_respuesta = st.session_state[session_key_historial]

                    # We display the assistant's response, writing it in real-time (stream)
                    with st.chat_message("assistant"):
                        full_response_content = "".join(
                            st.write_stream(
                                response_from_frontend(prompt, current_chat_model, historial_activo_para_respuesta)
                            )
                        )

                    # The 'response_from_frontend' function updates the history. We sync the list of messages to display.
                    if historial_activo_para_respuesta and historial_activo_para_respuesta[-1]["role"] == "assistant":
                        st.session_state[session_key_messages_display] = list(historial_activo_para_respuesta)

                    try:
                        # We save the updated conversation to the database. The save_history function handles the JSON conversion.
                        # The 'historial_activo_para_respuesta' is the list of dicts that needs to be saved.
                        if not save_history(current_chat_db_id, current_chat_name, historial_activo_para_respuesta, current_chat_model, user_name):
                            st.error("Error guardando el historial. Por favor, intenta de nuevo.")

                    except Exception as e:
                        st.error(f"Error guardando la conversación: {e}")

                    # We rerun the app to update the timestamp in the selectbox
                    st.rerun()
            else:
                # If the conversation data couldn't be loaded, we show an error
                st.error("No se pudo cargar la conversación seleccionada. Por favor, intenta de nuevo más tarde.")
else:
    # If no user is authenticated, we show an error message
    st.error("No estás autenticado. Por favor, inicia sesión para ver tu historial de conversaciones.")