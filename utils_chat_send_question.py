
import re

yes_no_indicators_rich = [
    # 'is', 'are', 'does', 'do', 'has', 'have', 'can', 'could', 'es', 'hay', 'tiene', 'conoces',
    # r'^is\b', r'^are\b', r'^do\b', r'^does\b', r'^did\b', r'^was\b', r'^were\b', r'^can\b', r'^could\b',
    # r'^would\b', r'^should\b', r'^has\b', r'^have\b', r'^had\b', r'^will\b', r'^might\b', r'^must\b',
    # r'^es\b', r'^está\b', r'^están\b', r'^son\b', r'^hay\b', r'^ha\b', r'^tiene\b', r'^tienen\b',
    # r'^conoces\b', r'^sabes\b', r'^puede\b', r'^pueden\b', r'^te\b', r'^le\b', r'^se\b', r'^lo\b', r'^la\b',
    # r'^cree\b', r'^cree que\b', r'^piensa\b', r'^considera\b', r'^estaría\b', r'^sería\b',
    # r'^es usted\b',  r'^le ha tocado\b', r'^le gustaría\b', r'^ha tenido\b',
    # r'^estuvo\b', r'^fue\b', r'^tuvo\b', r'^alguna vez\b', r'^usted\b', r'^se considera\b',
    # r'^usted cree\b', r'^usted ha\b', r'^usted puede\b'
]

number_keywords_full = [
    'how many', 'how much', 'cuántos', 'cuántas', 'número', 'porcentaje', 'salario', 'cuánto gana',
    'expected salary', 'años de experiencia', 'salary', 'income', 'ratio', 'level', 'score', 'years', "años",
    "Remuneración", "Remuneration",
    # English - general quantities
    r'how many', r'how much', r'what is the number', r'what amount', r'what percentage',
    r'what percent', r'what is the total', r'what score', r'what level', r'what rating',
    r'total number', r'total', r'rate', r'ratio', r'number of years', r'years of experience',
    r'number of times', r'how often', r'what duration', r'how long', r'what frequency',

    # English - salary and financial
    r'salary', r'annual salary', r'monthly salary', r'expected salary', r'desired salary',
    r'required salary', r'income', r'wage',

    # Spanish - general quantities
    r'cuántos', r'cuántas', r'cuánto', r'cuánta', r'número', r'porcentaje', r'tasa', r'total',
    r'cantidad', r'qué número', r'cuál es el número', r'número total', r'cuál es el total',
    r'nivel', r'puntuación', r'calificación', r'cuántos años', r'antigüedad', r'experiencia',
    r'número de veces', r'cuántas veces', r'cuántos proyectos', r'métrica', r'estadística',
    r'qué tan frecuente', r'número aproximado', r'cuánto tiempo', r'por cuánto tiempo',
    r'duración', r'monto', r'volumen', r'frecuencia',

    # Spanish - salary and financial
    r'sueldo',r'salar',  r'salario', r'ingreso', r'remuneración', r'cuánto gana', r'cuánto desea ganar',
    r'ganancia', r'cuánto espera ganar', r'retribución',

    # Spanish - experience/time
    r'tiempo en el cargo', r'tiempo en el puesto', r'cuánto tiempo ha trabajado',
    r'cuántos años', r'experiencia laboral', r'experiencia profesional'
]


# Classify each question
def classify_question(q):
    q_lower = q.lower()
    ret = "text"
    if any(k in q_lower for k in yes_no_indicators_rich):
        ret = "yes_no"
    if any(k in q_lower for k in number_keywords_full):
        ret = "number"

    return ret



def normalize_question(question: str) -> str:
    # Split by line breaks
    parts = re.split(r'\r\n|\n|\r', question.strip())

    # Normalize for comparison: lowercase and remove common punctuation
    def simplify(text):
        return re.sub(r"[.,\-–—_!?¡¿\"'(){}\[\]:;]", "", text.lower()).strip()

    seen = set()
    unique_parts = []
    for part in parts:
        simplified = simplify(part)
        if simplified and simplified not in seen:
            seen.add(simplified)
            unique_parts.append(part.strip())

    return ' '.join(unique_parts)

# # Ask GPT
# def ask_openai(question, qtype, context):
#     if qtype == "yes_no":
#         instruction = "Answer briefly with yes or no, and a short justification:"
#     elif qtype == "number":
#         instruction = "Provide a concise numerical answer or range:"
#     else:
#         instruction = "Respond concisely and conversationally, based on the context:"
#
#     messages = [
#         {"role": "system", "content": "You are an assistant helping answer job interview questions about Luis Lecinana. Use only the provided CV and instructions."},
#         {"role": "user", "content": f"Context:\n{context}\n\n{instruction}\n{question}"}
#     ]
#
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=messages,
#             temperature=0.3,
#             max_tokens=500
#         )
#         return response["choices"][0]["message"]["content"].strip()
#     except Exception as e:
#         return f"Error: {e}"