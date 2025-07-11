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
import json as js
import os
import time
import streamlit as st
import sqlite3 as sql
import datetime
import hashlib
import smtplib
import random
from email.mime.text import MIMEText
from streamlit_cookies_controller import CookieController

# We import functions that allow to use Google's LLMs and Mistral LLMs
from Gemini.GeminiAPI import gemini_answer
from Mistral.MistralLlmAPI import mistral_answer

controller = CookieController() # Controller for cookies, it allows to manage cookies in the app

st.session_state.code_sent = False # Its for A2F dialog, it indicates if the code was sent or not

# In this one, are all the server models that can run on Google's Server
google_models = ['gemini-2.5-pro',
                'gemini-2.5-flash', 'gemini-2.5-flash-preview-04-17', 'gemini-2.5-flash-preview-05-20', 'gemini-2.5-flash-lite-preview-06-17',
                'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.0-flash-thinking-exp-01-21',
                'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.5-flash-8b',
                'gemma-3-1b-it', 'gemma-3-4b-it', 'gemma-3-12b-it', 'gemma-3-27b-it',
                'gemma-2-2b-it', 'gemma-2-9b-it', 'gemma-2-27b-it'
                 ]


# In this one, are all the server models that can run on Mistral's Server
mistral_models = ['mistral-small-2506', 'magistral-small-2506', 'magistral-small-2506', 'open-mistral-nemo']

client = Client() # We set Ollama client, it would allow to use Ollama's models

# This function saves the conversation history in the database
def save_history(conversation_id, name, historial, model, user_name):
    try: # Start connection to the database
        with sql.connect('history.db') as save_conn:
            save_cursor = save_conn.cursor()

            # Check if this conversation already exists in the database, if it does, delete it
            if save_cursor.execute("SELECT * FROM history WHERE id = ?", (conversation_id,)).fetchone(): # Check if the conversation already exists
                save_cursor.execute("DELETE FROM history WHERE id = ?", (conversation_id,)) # Delete the conversation if it exists
                save_conn.commit() # Save the changes to the database

            json_historial = js.dumps(historial).encode('utf-8') # Convert the history to JSON format and encode it to bytes
            # Insert the JSON conversation into the database:
            save_cursor.execute("INSERT INTO history (user, id, name, model, conversation, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                           (user_name, conversation_id, name, model, json_historial, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            save_conn.commit() # Save the changes to the database

        st.toast(f"Conversación guardada exitosamente.", icon="✅") # Show a toast message indicating that the conversation was saved successfully
        return True # Return True if the conversation was saved successfully
    except sql.Error as s: # If there was an error while saving the conversation
        st.toast(f"Error al guardar la conversación: {s}. Por favor, inténtalo de nuevo.", icon="❌") # Show a toast message indicating that the conversation couldnt be saved
        return False

# This function generates the response, and clasify it in local or server models
def response(prompt, model, historial):
    historial.append({"role": "user", "content": prompt}) # Add the user prompt to the history
    answer_not_thoughts = "" # We iniciate a variable to the complete answer
    complete_answer = ''

    try:

        # If the model is in the list "google_models", we interpretate that it runs on Google's Server
        if model in google_models:
            answer_not_thoughts = ''
            for chunk in gemini_answer(prompt, model, historial):
                yield chunk
                complete_answer += chunk

            historial.append({"role": "assistant", "content": complete_answer})  # Finally, we add the complete answer to the history
            return complete_answer # Return the complete answer (with the thoughts) if the model is in the list of google models

        elif model in mistral_models: # If the model is in the list of mistral models, we interpretate that it runs on Mistral's Server
            for part in mistral_answer(prompt, model, historial): # For each part of the response...
                complete_answer += part # We add that part to the complete answer variable
                yield part # We yield that part to Bondol's frontend

    except TypeError: # If suddenly the API changes the response format, we will catch the error
        pass

    historial.append({"role": "assistant", "content": answer_not_thoughts}) # Finally, we add the complete answer to the history
    return answer_not_thoughts # And returns it

try:
    smtp_server = "smtp.gmail.com" # This is the SMTP server for Gmail
    smtp_port = 587 # This is the SMTP port for Gmail
    sender_email = st.secrets['EMAIL_SENDER_DIRECTION'] # This is the email address that will send the confirmation emails
    sender_password = st.secrets['EMAIL_SENDER_PASSWORD'] # This is the password for the sender email, it should be set as an environment variable for security reasons DONT HARDCODE IT ON PRODUCTATION

    # If the variables aren't set correctly, we show a warning message
    if not sender_email or not sender_password:
        st.warning("""
        **Advertencia de Configuración:**
        Las credenciales de correo electrónico (EMAIL_SENDER_ADDRESS, EMAIL_SENDER_PASSWORD) 
        no están configuradas como variables de entorno. 
        El registro de nuevas cuentas que requiere confirmación por email no funcionará.
        """)

    # This dialog is used to verificate the user, it consist in sending a confirmation code to the user's email
    @st.dialog('Confirma tu cuenta')
    def A2F_dialog(recipient_email):
        print(f"Se recibio un pedido de A2F al email: {recipient_email}")
        # If the A2F code isnt set, we create a random one, and save it
        if 'a2fcode' not in st.session_state:
            st.session_state.a2fcode = random.randint(100000, 999999)

        # This is the mail body and subject
        subject = "Confirmación de cuenta"
        body = f"""
        Hola! Este correo electronico proviene de Bondol,
        si has recibido este mensaje es porque has solicitado crear o realizar alguna acción en tu cuenta Bondol. De no ser así, por favor ignora este mensaje.

        Este es tu codigo de confirmación: {st.session_state.a2fcode} 

        Gracias por tu apoyo!!!.
        Si tienes alguna duda, o quieres reportar un error, no dudes en contactarnos

        Este es un mensaje automatizado, no hace falta responder a este correo.
        """

        # We set the mail message with the subject, body, sender and recipient
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email

        # We send the mail using the SMTP server define above
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # Start the TLS
            server.login(sender_email, sender_password) # We login to the STMP server
            server.sendmail(sender_email, recipient_email, msg.as_string()) # Finally, we send the mail
            print("Correo enviado exitosamente a:", recipient_email) # We print the message in the console
            st.session_state.code_sent = True

        input_code = str(st.text_input("Ingresa tu codigo de verificación aquí por favor:", key='confirmation_code')) # We put the text input for the user

        # If the user clicks a button; we check if the code is correct
        if st.button("Confirmar código"):
            int(st.session_state.a2fcode) # First, we convert the random code to an integer
            try:
                int_input_code = int(input_code) # Convert the input code to an integer
                if int_input_code == st.session_state.a2fcode: # We check the two codes, if match, we continue with the operation
                    st.success("Código ingresado correctamente! Continuando con la operación solicitada...")
                    print("El codigo ingresado es igual al enviado, continuando con la operación")
                    time.sleep(1.2)
                    return True # If the codes match, we return True

                # if the codes dont match, we dont continue, and wait for the user to try again
                elif int_input_code != st.session_state.a2fcode:
                    st.error("Código incorrecto, por favor intenta de nuevo.")
                    print("El codigo ingresado es diferente al enviado abortando operación")

            except ValueError: # If the user input a string or a non integrer, we catch the error
                st.error("Por favor, ingresa un código válido.")



    # This function, consist in creating a new account, generally, is called when an user wants to register
    def create_account():
        try:
            # We connect to the database, and create the account for the user
            with sql.connect('history.db') as register_conn:
                register_cursor = register_conn.cursor() # We set a cursor

                salt = os.urandom(16) # We generate a random salt for the hashing
                # We hash the password with the salt using SHA-256:
                hashed_password = hashlib.sha256(
                    salt + st.session_state.rpassword.encode('utf-8')).hexdigest()

                # Finally, we finish the creating of the account, adding the data to the users table
                register_cursor.execute(
                    "INSERT INTO users (user_name, email, hashed_password, salt, created_at) VALUES(?, ?, ?, ?, ?)",
                    (st.session_state.rusername.lower(), st.session_state.remail, hashed_password, salt,
                     datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                     ))
                register_conn.commit() # We summit the changes

            st.session_state.logged_in = True # Set login status to True
            st.session_state.username = st.session_state.rusername # Set the username in the session state

            # To save the session, we check if there is already an username registered in the cookies, and if is, we delete it
            if 'bondolusername' in controller.getAll():
                controller.remove('bondolusername')

            controller.set('bondolusername', st.session_state.username) # We set the username in the cookies
            st.session_state.dialog_etape = '' # We reset the dialog etape to avoid errors
            st.toast("Cuenta creada exitosamente!", icon="✅") # Show a toast message indicating that the account was created successfully
            return True # To finish, we return True to indicate that the account was created successfully

        # If there was an error, we catch it and show it to the user, to communicate to support if needed
        except Exception as i:
            st.error(f"Ocurrió un error al crear la cuenta: {i}. Por favor, inténtalo de nuevo.") # Show the error
            return False # return False to indicate that the account wasnt created

    # This dialog is where the user sing in on the app
    @st.dialog('Inicia sesión en tu cuenta')
    def login_dialog():

        #First, we ask to the user for his credentials, and we save it
        login_username = str(st.text_input('Usuario (nombre de usuario):')).lower() # IMPORTANT, we ALWAYS check the users in lowercase to avoid confusions
        login_password = st.text_input('Contraseña:', type='password') #This is the password

        # With this button, the user confirm his credentials, and we check if they match
        if st.button("Iniciar sesión", key='sing_in_login_button'):
            st.success("Iniciando sesión, por favor espera...")

            # First, we check if all the fields are complete
            if login_username and login_password:
                # Then, we connect to the database to check the credentials
                with sql.connect('history.db') as login_conn:
                    login_cursor = login_conn.cursor() # Create the cursor
                    login_cursor.execute("SELECT hashed_password, salt FROM users WHERE user_name = ?", (login_username,)) # Select user's data
                    user_data = login_cursor.fetchone() # Define user's data

                # If user's data was found... (Because it can be None if this user doesnt exists))
                if user_data:
                    db_salt = user_data[1] # Get the salt from the database
                    db_hashed_password = user_data[0] # Get the hashed password from the database

                    input_hashed_password = hashlib.sha256(db_salt + login_password.encode('utf-8')).hexdigest() # We hash the password like in the register etape

                    # Finally, we check if the hashed password from the input matches the one in the database
                    if input_hashed_password == db_hashed_password:
                        st.success("Inicio de sesión exitoso!" )
                        st.session_state.logged_in = True
                        st.session_state.username = login_username

                        try:
                            # To save the session, we check if there is already an username registered in the cookies, and if is, we delete it
                            if 'bondolusername' in controller.getAll():
                                controller.remove('bondolusername')
                        except:
                            pass
                        controller.set('bondolusername', st.session_state.username) # Set the session cookie...

                        st.session_state.dialog_etape = '' # We set dialog etape to ''  to avoid errors
                        time.sleep(2)
                        st.rerun() # We rerun to close the dialog
                    else:
                        st.error("La contraseña es incorrecta.") # If the password doesnt match, we communicate it
                else:
                    st.error("Usuario no encontrado, registrate por favor.") # If user cant be find, we communicate it
            else:
                st.error("Por favor, completa ambos campos.") # If the user didnt complete all the fields, we communicate it

    # this dialog is the first step to register in the platform; it consists in asking information
    @st.dialog('Crea tu cuenta')
    def register_dialog():

        # We ask the user for his future credentials
        st.session_state.rusername = str(st.text_input('Usuario (nombre de usuario):')).lower() # IMPORTANT, we ALWAYS check the users in lowercase to avoid confusions
        st.session_state.remail = str(st.text_input('Correo electrónico:')).lower() # We check the email in lowercase to avoid confusions
        st.session_state.rpassword = str(st.text_input('Contraseña:', type='password')) # We ask for his future password
        st.session_state.rconfirmpassword = str(st.text_input('Confirmar contraseña:', type='password')) # The user needs to input the password again to confirm it

        # Clicking this button, the user confirm his credentials
        if st.button("Registrarse", key='sing_up_login_button'):
            # We check if all the fields are complete
            if st.session_state.rusername and st.session_state.rpassword and st.session_state.remail and st.session_state.rconfirmpassword:
                # We check if the passwords match, if not, we communicate it
                if st.session_state.rpassword != st.session_state.rconfirmpassword:
                    st.error("Las contraseñas ingresadas no coinciden. Por favor, inténtalo de nuevo.")
                else: # If the passwords match...
                    try:
                        # We tried to connect to the database
                        with sql.connect('history.db') as register_conn:
                            register_cursor = register_conn.cursor() # We create a cursor
                            register_cursor.execute("SELECT COUNT(*) FROM users WHERE user_name = ?", (st.session_state.rusername.lower(),)) # We count how many users are in the application
                            user_count = register_cursor.fetchone()[0] # We got the number

                            register_cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (st.session_state.remail,)) # We count how many emails are in the application
                            email_count = register_cursor.fetchone()[0] # We got the integrer

                        if user_count > 0: # If there is at least one user with that username, we dont create the account
                            st.error("El nombre de usuario ya está en uso. Por favor, elige otro.")

                        # If there isnt a user using this username, we continue checking if other user is using the email
                        elif user_count == 0:
                            # If there is at least one user with that email, we dont create the account
                            if email_count > 0:
                                st.error("El correo electrónico ya está registrado. Por favor, utiliza otro.")

                            # If there isnt a user using this email we return True and continue with the A2F dialog
                            elif email_count == 0:
                                st.success("Los datos ingresados son correctos, por favor espera a que se envíe un correo de confirmación.")
                                time.sleep(1.5)
                                st.session_state.dialog_etape = 'register_A2F'
                                st.rerun() # We rerun to close the dialog and open the A2F dialog

                    except sql.Error as s:  # If an error occurs, we finish the code
                        st.error(f"Ocurrió un error al verificar los datos: {s}. Por favor, inténtalo de nuevo.")
                        return False

            else: # If the user didnt complete all the fields, we communicate it
                st.error("Por favor, completa todos los campos requeridos.")

    # This dialog is used to change the password of an existing user
    @st.dialog('Recuperar contraseña')
    def change_password_dialog():
        st.session_state.cp_username = None # We reset the username to None, to avoid errors
        st.session_state.cp_username = str(st.text_input('Usuario (nombre de usuario):')).lower() # We wait user's input

        # If the user clicks the button, we check if the user exists in the database
        if st.button('Continuar'):
            # First, we connect to the database to check if the user exists and
            with sql.connect('history.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE user_name = ?", (st.session_state.cp_username,))
                user_count = cursor.fetchone()[0]
                if user_count > 0: # If the user exists, we get his data
                    cursor.execute("SELECT id, user_name, email, created_at FROM users WHERE user_name = ?", (st.session_state.cp_username,))
                    user_data = cursor.fetchone()
                    print("Solicitud de cambio de contraseña del usuario:"
                          f"ID: {user_data[0]} | Nombre de usuario: {user_data[1]} | Email: {user_data[2]} | Creado a las: {user_data[3]}")

            # If the user doesnt exist, we communicate it
            if user_count == 0:
                st.error("El usuario inexistente, por favor, compruebe la información, e intente nuevamente.")
                return

            # If there is only 1 user with that username, we return True to continue with the next step
            elif user_count == 1:
                st.session_state.cp_email = user_data[2] # We save the email of the user
                return True # Return True to continue

            elif user_count > 1: # If there are 2 or more users with the same name, we communicate it
                st.error("Hay más de un usuario con el mismo nombre, por favor, contacta al soporte para resolver este problema.")
                return

    @st.dialog('Cambiar contraseña')
    def change_password_2nd_dialog():
        st.success("Por favor, ingresa tu nueva contraseña.")
        print("EXITO")
        return True
except Exception as e:
    st.error(f"Ocurrió un error inesperado: {e}. Por favor, inténtalo de nuevo más tarde.")
    st.stop()
