# Coding in utf-8
# Develop by Bondol Team

# Copyright 2025 Henri
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


# We import the necessary general libraries
import streamlit as st
import sqlite3 as sql

# We import functions of others Bondol's files
from functions import response, save_history
from Gemini.GeminiAPI import get_bondol_prompt


# We iniciate the historial
historial = []

# We set the page configuration
st.title("Bondol")

# We create the selectbox, so th user can choose the model
crude_model = st.selectbox(
    '¿Qué modelo quieres usar? Se puede cambiar durante la conversación',
    ('gemini-2.5-pro',
     'gemini-2.5-flash', 'gemini-2.5-flash-preview-04-17', 'gemini-2.5-flash-preview-05-20', 'gemini-2.5-flash-lite-preview-06-17',
     'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.0-flash-thinking-exp-01-21',
     'gemini-1.5-flash', 'gemini-1.5-flash-8b',
     'gemma-3-1b-it', 'gemma-3-4b-it', 'gemma-3-12b-it', 'gemma-3-27b-it',
     'gemma-2-2b-it', 'gemma-2-9b-it', 'gemma-2-27b-it',
     'mistral-small-2506', 'magistral-small-2506', 'magistral-small-2506', 'open-mistral-nemo',
     )
)

# We set Bondol's prompt, to give the AI personality
bondol_prompt = get_bondol_prompt()

# If isn't any message in the session, we comprehend that the user is running the app for the first time
if "messages" not in st.session_state:
    st.session_state.messages = [] # We define a list for the messages
    st.session_state.historial = [] # we define a list for the historial
    st.session_state.actual_id = int # We set that the id of the session is an integer

    #st.session_state.historial.append({"role": "system", "content": bondol_prompt}) # We add the bondol prompt to the historial

    with sql.connect('history.db') as conn:
        cursor = conn.cursor()
        st.session_state.actual_id = cursor.execute("SELECT MAX(id) FROM history").fetchone()[0] or 0 # We get the last id from the history database, or 0 if there is no history

    st.session_state.actual_id += 1 # The id of the database, is autoincremented, so that we can know the next id of the proxime conversation (this one)

# For each message in the session, we display it in the chat following the role of the message (user or assistant)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# If the user send a prompt....
if prompt := st.chat_input("Pregunta a Bondol:"):
    with st.chat_message("user"): # With the role of user, we display the prompt
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt}) # We append the prompt to the messages

    with st.chat_message("assistant"): # And with role of assistant, we respond the prompt
        response_without_thought = '' # We define a variable to store the response without thoughts
        status = None
        message = st.empty()
        for i in response(prompt, crude_model, st.session_state.historial):
            response_with_thoughts = "".join(i)

            if '<think>' in response_with_thoughts.split(' '):
                if not status:
                    status = st.status('Pensando...')
                    continue

            elif '</think>' in response_with_thoughts.split(' '):
                status.update(label='Pensando...', state='complete')
                status = None
                continue

            if status:
                status.markdown(i) # We update the status with the response, without a new line
                continue

            response_without_thought += i # We concatenate the response without thoughts
            message.markdown(response_without_thought) # We write the response in the chat, without a new line


    st.session_state.messages.append({"role": "assistant", "content": response_without_thought}) # We append the assistant's response to the historial

    if st.session_state.get('logged_in', False): # If the user is logged in, we save the conversation
        if st.session_state.username: # If is a valid user...
            save_history(st.session_state.actual_id, prompt, st.session_state.historial, crude_model, st.session_state.username)
