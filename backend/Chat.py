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
    REGLAS_BASE = """Eres el asistente de EveryCPT, una plataforma de cursos online.

REGLA DE VERDAD (la más importante, nunca la rompas):
- Si no tienes certeza sobre un dato concreto (una fecha, una cifra, un nombre propio, un curso específico de la plataforma), NO te lo inventes.
- Si no lo sabes, dilo explícitamente ("no tengo información suficiente sobre esto") en vez de rellenar con algo que suene plausible.
- Para temas de cultura general (física, historia, programación, etc.) puedes usar tu conocimiento con normalidad, siempre que estés seguro.

REGLA DE FORMATO:
- Responde de forma clara y ordenada, sin relleno tipo "¡Claro! Aquí tienes:" ni despedidas innecesarias.
- Usa listas o párrafos cortos cuando ayude a la claridad, no bloques de texto pegados.
- Responde siempre en el mismo idioma en que está escrita la pregunta del usuario.

REGLA DE PROFUNDIDAD:
- Si el tema es amplio (una disciplina entera, ej: "aprender programación"), da primero un índice o mapa de subtemas, no lo desarrolles todo de golpe.
- Si el tema es concreto (una pregunta o concepto específico), desarróllalo con el detalle necesario para que quede claro, sin excederte innecesariamente."""

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
            return (
                f"{self.REGLAS_BASE}\n\n"
                f"PERSONALIZACIÓN SEGÚN EL USUARIO:\n"
                f"El usuario se ha descrito así: \"{perfil_usuario}\".\n"
                f"- Si en esa descripción aparece su nombre, dirígete a él por ese nombre "
                f"de forma natural (no hace falta repetirlo en cada frase, pero sí que se note).\n"
                f"- Si menciona su nivel, edad o profesión, ajusta el vocabulario de forma "
                f"explícita: evita jerga técnica si parece principiante o es joven, y úsala con "
                f"normalidad si dice tener experiencia en el tema.\n"
                f"- Si la descripción no da ningún dato útil de este tipo, ignórala y usa un "
                f"tono neutro-cercano por defecto.\n"
                f"Todo esto SIN romper ninguna de las reglas anteriores (verdad, formato, profundidad)."
            )
        # Si no hay perfil, usamos solo las reglas base. Antes, en tu código,
        # esto devolvía la respuesta "cruda" sin ninguna adaptación de tono.
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