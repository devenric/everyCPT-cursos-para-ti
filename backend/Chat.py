import ollama

# ============================================================
#  CLASE Chat
#  Cambios respecto a tu versión original, y el PORQUÉ de cada uno:
#
#  1. Ya NO hay dos objetos Chat encadenados (chat1 -> chat2).
#     Antes hacías 2 llamadas al modelo por cada pregunta:
#     una para "extraer" y otra para "adaptar al perfil".
#     Eso duplica el tiempo de espera del usuario sin necesidad,
#     porque las dos cosas se pueden pedir en UN solo prompt bien
#     escrito. Menos llamadas = más rápido, mismo resultado.
#
#  2. El "perfil" del usuario ya NO sustituye tus reglas de calidad,
#     se SUMA a ellas. Antes, si el usuario mandaba un perfil,
#     tu system prompt entero se perdía (set_system_prompt lo
#     pisaba). Ahora reglas_base + perfil siempre van juntos.
#
#  3. Hay una regla explícita de "no inventar". Antes no existía
#     ninguna instrucción sobre qué hacer si el modelo no sabe algo.
# ============================================================

class Chat:

    # Estas son las reglas que SIEMPRE se aplican, pase lo que pase
    # en el perfil del usuario. Son la base de calidad de tu producto.
    # Fíjate que están escritas como si le hablaras a una persona,
    # no como código: eso es literalmente lo que es un system prompt.
    REGLAS_BASE = """Eres el mentor de EveryCPT, una plataforma de cursos online. No eres un motor de respuestas neutro: eres como un amigo con más experiencia que explica las cosas con cercanía, paciencia y algo de cháchara natural (una coletilla, un "vale, vamos allá", un toque de humor si encaja) — pero sin relleno vacío tipo "¡Claro! Aquí tienes:" al principio de cada mensaje. Cercanía sí, muletillas de plantilla no.

REGLA DE VERDAD (nunca la rompas):
- Si no tienes certeza sobre un dato concreto (fecha, cifra, nombre propio, curso específico de la plataforma), no te lo inventes. Dilo abiertamente.
- Para cultura general (física, historia, programación...) usa tu conocimiento con normalidad si estás seguro.

REGLA DE PROFUNDIDAD:
- Tema amplio (una disciplina entera) → da primero un mapa de subtemas, no lo desarrolles todo de golpe.
- Tema concreto → desarróllalo con el detalle que haga falta para que quede claro, sin paja."""

    def __init__(self, modelo):
        self.modelo = modelo
        # El historial vive DENTRO del objeto Chat mientras dura la conversación.
        # Es una lista de diccionarios, tal y como los espera la librería ollama.
        self.historial = []

    def _construir_system_prompt(self, perfil_usuario):
        """
        Junta las reglas base (fijas) con el perfil que el usuario escribió
        en el cajón rosa del frontend (ej: "soy un niño de 10 años" o
        "soy ingeniero, sé explicaciones técnicas").

        OJO: esto es una función "privada" (empieza por _), significa que
        solo se usa dentro de esta clase, no se llama desde fuera.
        """
        if perfil_usuario and perfil_usuario.strip() != "":
            # OJO: este bloque va DESPUÉS de las reglas base a propósito, y no
            # está escrito como "si menciona X, haz Y" sino como orden directa
            # y obligatoria. Dos decisiones deliberadas:
            #
            # 1. Va al FINAL del prompt: los modelos (sobre todo los pequeños)
            #    dan más peso a lo último que leen justo antes de responder.
            #    Si esto va enterrado en medio, se diluye.
            #
            # 2. Es incondicional ("haz esto"), no condicional ("si menciona
            #    esto, entonces..."). Quitarle al modelo la decisión de "¿esto
            #    cuenta o no?" hace que lo cumpla de forma mucho más fiable.
            return (
                f"{self.REGLAS_BASE}\n\n"
                f"EJEMPLO de cómo se ve una buena adaptación (imita este ESTILO, no el contenido):\n"
                f"Perfil de ejemplo: \"Me llamo Marta, soy cocinera y quiero aprender a programar\".\n"
                f"Pregunta de ejemplo: \"¿Qué es un bucle for?\"\n"
                f"Respuesta de ejemplo: \"Vale Marta, piénsalo así: un bucle for es como una receta "
                f"que dice 'repite este paso con cada ingrediente de la lista'. Si tienes 6 huevos y "
                f"tu paso es 'cascar el huevo', el bucle hace ese paso 6 veces, uno por huevo, sin que "
                f"tengas que escribir 'casca el huevo' seis veces seguidas. En código sería así de simple...\"\n"
                f"Fíjate: usa su nombre, la analogía es de SU campo (cocina), y usa un tono cercano "
                f"sin sonar a manual.\n\n"
                f"ESTE USUARIO EN CONCRETO se ha descrito así: \"{perfil_usuario}\".\n"
                f"Tareas OBLIGATORIAS antes de responder (igual que en el ejemplo de arriba):\n"
                f"1. Si hay un nombre en esa descripción, úsalo al dirigirte a él.\n"
                f"2. Identifica un campo, afición o profesión que mencione. Busca una "
                f"analogía o comparación con ESE campo concreto para explicar el tema de "
                f"la pregunta. Esto es obligatorio si hay un campo identificable, no opcional.\n"
                f"3. Ajusta la dificultad del vocabulario a su nivel descrito.\n"
                f"Si la descripción no da ningún dato de nombre/campo/nivel, ignora estas "
                f"3 tareas y usa un tono cercano por defecto."
            )
        return self.REGLAS_BASE

    def procesarPrompt(self, mensaje_usuario, perfil_usuario=""):
        """
        Esta es la única llamada al modelo por pregunta (antes eran 2).

        messages es una lista que representa la conversación entera:
        - Un mensaje 'system' (las reglas, se manda siempre primero)
        - Los mensajes anteriores del historial (para que recuerde el contexto)
        - El mensaje nuevo del usuario

        Los modelos de chat no "recuerdan" nada entre llamadas por sí solos:
        cada vez que llamas a ollama.chat(), le mandas TODA la conversación
        de nuevo. Por eso guardamos el historial nosotros mismos.
        """
        system_prompt = self._construir_system_prompt(perfil_usuario)

        mensajes = (
            [{'role': 'system', 'content': system_prompt}]
            + self.historial
            + [{'role': 'user', 'content': mensaje_usuario}]
        )

        respuesta = ollama.chat(model=self.modelo, messages=mensajes)
        texto_respuesta = respuesta['message']['content']

        # Guardamos el turno en el historial para la siguiente pregunta.
        self.historial.append({'role': 'user', 'content': mensaje_usuario})
        self.historial.append({'role': 'assistant', 'content': texto_respuesta})

        # Truco sencillo para no dejar crecer el historial sin límite:
        # nos quedamos solo con los últimos 10 mensajes (5 turnos).
        # Un historial infinito hace las respuestas más lentas y puede
        # confundir a un modelo pequeño con demasiado contexto.
        if len(self.historial) > 10:
            self.historial = self.historial[-10:]

        return texto_respuesta