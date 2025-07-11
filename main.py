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

# We import the necessary libraries
import streamlit as st
import sqlite3 as sql
from streamlit_cookies_controller import CookieController
from functions import login_dialog, register_dialog, A2F_dialog, create_account, change_password_dialog, change_password_2nd_dialog



#Define cookies' controller
controller = CookieController()

# Set the page configuration
st.set_page_config(
    page_title="Bondol",
    page_icon="🐶",
    layout="wide",
    #initial_sidebar_state="expanded",
)

# LCSVE = Local y Server Edition
# LCE = Local Edition
# SVE = Server Edition
app_version = "v0.1.2 SVE" # This is the app version, it will be shown in the sidebar

# Only the firts time the app is run, dialog_etape is set to ''
if 'dialog_etape' not in st.session_state:
    st.session_state.dialog_etape = ''

# We create de database and the tables if they do not exist
with sql.connect('history.db') as initial_conn:
    initial_cursor = initial_conn.cursor()
    initial_cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        user TEXT,
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        conversation BLOB ,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP 
    )""") # Create the history table
    initial_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        email TEXT,
        hashed_password BLOB NOT NULL,
        salt TEXT, 
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    
    )""") # Create the users table
    initial_conn.commit() # Apply the changes to the database


# This function checks if the user is already logged in, if not, the function tries to recover the session from cookies.
# If the function can sing in the user, or if the user is already logged in, the function returns True, otherwise it returns False.
def config_page():
    # If the user is already logged in, we show the username and the status, returns True
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        st.sidebar.markdown(f"**Usuario:** {st.session_state.username}")
        st.sidebar.markdown("**Estado:** Conectado")
        return True
    # If the user is not logged in, we check if there is a session saved in cookies, if there is, we try to recover the session
    elif 'logged_in' not in st.session_state or st.session_state.logged_in is False:
        st.session_state.logged_in = False
        username_cookie = controller.get('bondolusername') # Get the username from the cookies

        # If a cookie was find, it checks if the user exists in the database, and returns True, if the user exists, otherwise it returns False
        if username_cookie:
            # Connect to database to check information
            with sql.connect('history.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE user_name = ?", (controller.get('bondolusername'),)) # Check if the user exists in the database
                # If the user exists, we set the session state to logged in and return True
                if user_count := cursor.fetchone()[0] > 0:
                    st.session_state.logged_in = True
                    st.session_state.username = username_cookie
                    st.sidebar.markdown(f"**Usuario:** {st.session_state.username}")
                    st.sidebar.markdown("**Estado:** Conectado")
                    return True
                # If the user does not exist, we show a toast message
                elif user_count == 0:
                    st.toast("Tu usuario guardado no existe en la base de datos, prueba de nuevo más tarde.", icon="🔔")
        # If there isnt an username cookie, we show a toast message
        else:
            st.toast("No se ha encontrado una sesión abierta.", icon="🔔")

        # If the user is not logged in, we show the login and register buttons
        if st.sidebar.button("Iniciar sesión", key='login_button'):
            st.session_state.dialog_etape = 'login'

        if st.sidebar.button("Registrarse", key='register_button'):
            print("Alguien desea registrarse, comenzando operación")
            st.session_state.dialog_etape = 'register'



        # We use a system that, with each st.rerun(), we can close and open new dialogs, of distints types.
        # If the dialog_etape is 'login', we show the login dialog
        if st.session_state.dialog_etape == 'login':
            login_dialog()

        # If the dialog_etape is 'register', we show the register dialog
        elif st.session_state.dialog_etape == 'register':
            register_dialog()

        # If the dialog_etape is 'register_A2F', we show the A2F dialog, if it returns True, we set the session state to logged in,
        # create the account, and finally (ONLY IF THE ACCOUNT WAS CREATE) config_page() returns True
        elif st.session_state.dialog_etape == 'register_A2F':
            if A2F_dialog(st.session_state.remail):
                st.success("Cuenta creada exitosamente.")
                create_account()

        st.session_state.configurated = True # Set the configurated state to True, so the app can configure the pages correctely
        return False # If anything can be done, we return False, indicating thats the user isnt logged in

# Print the app version in the sidebar
st.sidebar.markdown(f"**Versión:** {app_version}")


# Always, we check if the user click the button "cambiar contraseña" (change password) in Accounts.py.
if st.session_state.dialog_etape == 'change_password':
    if change_password_dialog() is True:
        st.session_state.dialog_etape = 'change_password_A2F'
        st.rerun()

# When the users complete the change password dialog, we send an A2F code to his mail
elif st.session_state.dialog_etape == 'change_password_A2F':
    if A2F_dialog(st.session_state.cp_email):
        st.session_state.dialog_etape = 'change_password_approved'
        st.rerun()

# When the user completes the A2F code, we show a dialog to change the password
elif st.session_state.dialog_etape == 'change_password_approved':
    change_password_2nd_dialog()



st.session_state.configurated = config_page() # We set "...configurated" to the return of config_page(), which will be True if the user is logged in, or False if the user is not logged in.

# According to the state of "configurated", we set the pages to show in the app.
if st.session_state.configurated:
    pages = {
        "": [
            st.Page("pages/FrontEnd.py", title="Nueva conversación"),
            st.Page("pages/ChangeLog.py", title="Registro de cambios"),
        ],
        "Centro de cuentas": [
            st.Page("pages/HistoryViewer.py", title="Historial de conversaciones"),
            st.Page("pages/Accounts.py", title="Panel de control de cuentas"),
        ],
    }

else:
    pages = {
        "": [
            st.Page("pages/FrontEnd.py", title="Nueva conversación"),
            st.Page("pages/ChangeLog.py", title="Registro de cambios"),
        ],
    }

# We run the application and pray to work
pg = st.navigation(pages)
pg.run()

# Finally, we set the session state for dialog_etape to an empty string, so if the user close an opened dialog, it will not be opened again.
st.session_state.dialog_etape = ''
