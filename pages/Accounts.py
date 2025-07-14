import time
import streamlit as st
import sqlite3 as sql
from streamlit_cookies_controller import CookieController
from functions import working_in


controller = CookieController()
st.title("Panel de control de cuentas")

if st.session_state.get('logged_in', False):
    if st.session_state.username:
        st.success(f"Bienvenido, {st.session_state.username}!")
        st.write("Aquí puedes administrar tu cuenta")

        if st.button("Cambiar contraseña"):
            st.session_state.dialog_etape = 'change_password'
            st.rerun()

        if st.button("Cerrar sesión"):
            st.session_state.logged_in = False
            st.session_state.username = None
            controller.remove('bondolusername')
            st.success("Has cerrado sesión exitosamente.")
            time.sleep(2)
            st.rerun()


        if st.button("Eliminar cuenta"):
            working_in()

        if st.button("Guardar cambios"):
            working_in()
