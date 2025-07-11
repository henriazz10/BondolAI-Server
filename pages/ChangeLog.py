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


import streamlit as st

st.title("Hoja de cambios")
st.caption('BondolAI - Inteligencia Artificial para todos')


st.divider()
st.header('v0.1.2')
st.caption('Fecha: 2025-6-23 (AA-MM-DD)')
st.write('''
* Se arreglaron Bugs fatales para la aplicación.\n
* Se cambió toda la logica de la interfaz grafica, ahora es más fluida y eficiente.\n
* Ahora puedes cerrar los paneles de "Iniciar sesión" y "Registrarse".\n

''')

st.divider()
st.header('v0.1.1')
st.caption('Fecha: 2025-6-17 (AA-MM-DD)')
st.write('''
* Empezó el testeo del "Dashboard" para la gestión de cuentas.\n
* Con ello: \n
    * Se añadió la capacidad de eliminar la cuenta.\n
    * Se añadió la capacidad de cambiar la contraseña.\n
    * Se añadió la capacidad de ver el estado de la cuenta.\n
    * Ahora, puedes optar por **NO guardar** tu historial si lo deseeas.\n
    * (Todavía no están habilitadas para todos los usuarios, por lo que pueden no funcionar)\n

''')

st.divider()
st.header('v0.1.0')
st.caption('Fecha: 2025-6-15 (AA-MM-DD)')
st.write('''
* Añadimos la capacidad de tener distintas conversaciones guardadas con la misma cuenta.\n
* Se añadió la capacidad de modificar historiales antiguos.\n
* Se añadió la capacidad de crear cuentas.\n
* Empezamos a desarrollar un "Dashboard" para la gestión de cuentas.\n
* Testamos todos los modelos de BondolAI y los dejamos listos para su uso.\n
* Cambiamos la eficiencia de la memoria de los modelos, ahora son más rápidos y eficientes.\n
* Ahora los modelos de Google son capaces de interactuar con el usuario de una manera más fluida, personalizada y natural.\n
* Se añadió la capacidad de cambiar el modelo durante una conversación, sin perder el historial.\n
* Se mejoró la gestión de errores y se añadieron mensajes de error más claros y concisos.\n
* Añadimos un sistema de notificaciones para informar al usuario del estado de la sesión de la cuenta.\n
* Ahora la aplicación guarda su sesión automáticamente, para que no tengas que iniciar sesión cada vez que entres.\n
* Se eliminó la posibilidad de acceder al historial de conversaciones sin iniciar sesión, para mejorar la seguridad y privacidad del usuario.\n
* Se añadió un sistema de autenticación de dos factores (Solo apto "Registrarse") para mejorar la seguridad de las cuentas.\n
* Cambiamos los nombres de las páginas de Bondol para que sea mas facil navegar por la aplicación.\n
* Ahora puedes eliminar conversaciones desde su respectiva página.\n
* Se añadió un sistema de búsqueda de conversaciones por nombre.\n
* Se añadió un sistema de búsqueda de conversaciones por modelo.\n
* Se añadió un sistema de búsqueda de conversaciones por fecha.\n
* Ahora puedes ver el estado de tu cuenta desde la barra lateral.\n
* Ahora se muestra la versión de la aplicación en la barra lateral.\n
* Se eliminó el modelo de 'gemini-1.5-pro' debido a las directivas de Google DeepMind.\n
* Se está pensando la posibilidad de añadir un filtro conocido como ShieldGemma, para evitar Prompts inapropiados o peligrosos en los modelos de Google.\n
* Ahora Bondol tiene personalidad propia, sin importar el modelo elegido
''')

st.divider()
st.header('Exp v0.0.13')
st.caption('Fecha: 2025-6-8 (AA-MM-DD)')
st.write('''

* Se añade la función de cuentas. \n


* Nota de desarrolladores: \n
    "Sus contraseñas se encuentran encriptadas y no se almacenan en texto plano, por lo que no podemos recuperar contraseñas perdidas. Si olvida su contraseña, deberá crear una nueva cuenta." \n
    "Por favor, asegúrese de guardar su contraseña en un lugar seguro, ya que no podremos ayudarle a recuperarla si la pierde." \n
''')

st.divider()
st.header('Exp v0.0.12')
st.caption('Fecha: 2025-5-26 (AA-MM-DD)')
st.write('''

* Se optimizaron las consultas al historial.\n
* Ahora puedes modificar historiales antiguos y que permanezcan esas modificaciones.\n
* Se agrego una nueva base de datos.\n
* Se arreglaron Bugs relacionados con la API de Gemini.\n
''')

st.divider()
st.header('ANUNCIO IMPORTANTE')
st.caption('Fecha: 2025-5-23 (AA-MM-DD)')
st.write('''

Nos complace anunciar la version 1.0.0 de BondolAI \n
se prevee que la misma salga a finales de este año.

Bondol team.
\n
''')

st.divider()
st.header('Exp v0.0.11')
st.caption('Fecha: 2025-5-23 (AA-MM-DD)')
st.write('''

* Se eliminó el modelo 'gemini-2.5-pro-exp-03-25' debido a las directivas de Google DeepMind.\n
* Se añadieron los modelos 'gemma3:1b-it-qat','gemma3:4b-it-qat','gemma3:12b-it-qat' y 'gemini-2.5-flash-preview-05-20'.\n
* Se agregó un apartado experimental de historial.\n
\n
''')



st.divider()
st.header('Exp v0.0.10')
st.caption('Fecha: 2025-5-10 (AA-MM-DD)')
st.write('''

* Se agregó la pestaña "Change Log".\n
* Se añadieron los modelos 'qwen3:0.6b', 'qwen3:1.7b', 'qwen3:4b', 'qwen3:8b', 'qwen3:30b-a3b'.\n
* Se corrigieron errores fundamentales respecto a la memoria de los modelos.\n
\n
''')
