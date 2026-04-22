import requests
import json
from datetime import datetime
from mistralai.client import Mistral

# --- CONFIGURACIÓN ---
TWELVE_DATA_API_KEY = "62149b43b7954bc8a3109a9eff9f01f4"
MISTRAL_API_KEY = "NNXFGfoEWQzEu5pXjZ2iNngw6mZ8vhhg"

client = Mistral(api_key=MISTRAL_API_KEY, timeout_ms=120000)
session = requests.Session()

def get_detailed_stock_data(symbol: str):
    """Extrae datos financieros y desarrollo de noticias."""
    base_url = "https://api.twelvedata.com"
    params = {"symbol": symbol, "apikey": TWELVE_DATA_API_KEY}
    
    try:
        # 1. Cotización
        quote = session.get(f"{base_url}/quote", params=params, timeout=10).json()
        
        # 2. Histórico (Tendencia de 5 días)
        ts_params = {**params, "interval": "1day", "outputsize": "5"}
        ts = session.get(f"{base_url}/time_series", params=ts_params, timeout=10).json()
        
        # 3. Noticias con desarrollo (traemos más info)
        news_data = session.get(f"{base_url}/press_releases", params=params, timeout=15).json()
        # Capturamos título y descripción para dar más contexto
        news = []
        for n in news_data.get("press_releases", [])[:3]:
            news.append({
                "titulo": n.get("title"),
                "fecha": n.get("date"),
                "resumen": n.get("description", "Sin descripción disponible.")
            })

        return {
            "info_mercado": {
                "empresa": quote.get("name"),
                "precio": quote.get("close"),
                "moneda": quote.get("currency"),
                "cambio": quote.get("percent_change"),
                "rango_dia": f"{quote.get('low')} - {quote.get('high')}"
            },
            "historico_precios": [v.get("close") for v in ts.get("values", [])],
            "noticias_detalladas": news
        }
    except Exception as e:
        return {"error": f"Fallo en la extracción de datos: {str(e)}"}

tools = [{
    "type": "function",
    "function": {
        "name": "get_detailed_stock_data",
        "description": "Obtiene información financiera y noticias de un activo a partir de su ticker.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "El ticker del activo (ej: MSFT, AAPL, BTC/USD)"}
            },
            "required": ["symbol"]
        }
    }
}]

def run_agent(user_input):
    # Obtener fecha de hoy
    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    
    system_instruction = f"""
    Hoy es {fecha_actual}. 
    Sos un Analista Senior. Tu tarea es:
    1. Identificar si el usuario menciona una empresa o activo.
    2. Usar 'get_detailed_stock_data' para obtener la info técnica.
    3. Redactar un informe ejecutivo extenso y profesional en Markdown.
    
    Para las noticias: No te limites a listarlas. Analizá cómo el contenido de la noticia 
    (resumen proporcionado) podría impactar en la confianza del inversor o en el precio.
    
    Formato del informe:
    # 📈 Informe Ejecutivo: [Empresa]
    **Fecha de análisis:** {fecha_actual}
    ---
    ## 1. Situación de Mercado
    ## 2. Comportamiento Reciente (Tendencia)
    ## 3. Análisis de Noticias y Eventos Clave
    (Aquí desarrollá cada noticia con su impacto potencial)
    ## 4. Perspectiva y Conclusión
    """

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.chat.complete(
            model="mistral-medium-latest",
            messages=messages,
            tools=tools,
        )

        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments)
                print(f"[*] Detectado activo: {args['symbol']}. Procesando informe...")
                
                data = get_detailed_stock_data(args['symbol'])
                
                messages.append({
                    "role": "tool",
                    "name": "get_detailed_stock_data",
                    "content": json.dumps(data),
                    "tool_call_id": tool_call.id,
                })
            
            final = client.chat.complete(model="mistral-medium-latest", messages=messages)
            return final.choices[0].message.content
        
        return msg.content

    except Exception as e:
        return f"Ocurrió un error en el sistema: {str(e)}"

if __name__ == "__main__":
    print("--- Sistema de Inteligencia Financiera ---")
    user_text = input("¿Qué activo o empresa te gustaría analizar hoy?\n> ")
    
    resultado = run_agent(user_text)
    print("\n" + resultado)