import requests
import json
from datetime import datetime, timedelta
from mistralai.client import Mistral

# --- CONFIGURACIÓN ---
TWELVE_DATA_API_KEY = "62149b43b7954bc8a3109a9eff9f01f4"
MISTRAL_API_KEY = "NNXFGfoEWQzEu5pXjZ2iNngw6mZ8vhhg"
NEWS_API_KEY = "8f4b301015fe430b935bca3b6af0e720" # <--- Agregá tu clave aquí

client = Mistral(api_key=MISTRAL_API_KEY, timeout_ms=120000)
session = requests.Session()

def get_detailed_stock_data(symbol: str):
    """Extrae datos financieros y cotizaciones de Twelve Data."""
    base_url = "https://api.twelvedata.com"
    params = {"symbol": symbol, "apikey": TWELVE_DATA_API_KEY}
    
    try:
        # 1. Cotización
        quote = session.get(f"{base_url}/quote", params=params, timeout=10).json()
        
        # 2. Histórico (Tendencia de 5 días)
        ts_params = {**params, "interval": "1day", "outputsize": "5"}
        ts = session.get(f"{base_url}/time_series", params=ts_params, timeout=10).json()
        
        return {
            "info_mercado": {
                "empresa": quote.get("name"),
                "precio": quote.get("close"),
                "moneda": quote.get("currency"),
                "cambio": quote.get("percent_change"),
                "rango_dia": f"{quote.get('low')} - {quote.get('high')}"
            },
            "historico_precios": [v.get("close") for v in ts.get("values", [])]
        }
    except Exception as e:
        return {"error": f"Fallo en datos bursátiles: {str(e)}"}

def get_global_news(query: str):
    """Busca noticias globales usando NewsAPI (v2/everything)."""
    url = "https://newsapi.org/v2/everything"
    # Buscamos noticias de los últimos 7 días para mayor relevancia
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "relevancy",
        "language": "es", # Podés cambiar a 'en' para más volumen de noticias
        "apiKey": NEWS_API_KEY,
        "pageSize": 5
    }
    
    try:
        response = session.get(url, params=params, timeout=15).json()
        articles = response.get("articles", [])
        
        results = []
        for art in articles:
            results.append({
                "fuente": art.get("source", {}).get("name"),
                "titulo": art.get("title"),
                "descripcion": art.get("description"),
                "contenido": art.get("content")[:200] + "..." # Fragmento
            })
        return {"noticias_globales": results}
    except Exception as e:
        return {"error": f"Fallo en NewsAPI: {str(e)}"}

# --- DEFINICIÓN DE HERRAMIENTAS ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_detailed_stock_data",
            "description": "Obtiene información técnica, precios y tendencia de un activo financiero.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "El ticker del activo (ej: MSFT, AAPL, BTC/USD)"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_global_news",
            "description": "Busca noticias mundiales sobre una empresa, industria o evento económico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Palabra clave o nombre de empresa para buscar noticias."}
                },
                "required": ["query"]
            }
        }
    }
]

def run_agent(user_input):
    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    
    system_instruction = f"""
    Hoy es {fecha_actual}. 
    Sos un Analista Senior de Inversiones. Tu tarea es:
    1. Usar 'get_detailed_stock_data' para los números técnicos.
    2. Usar 'get_global_news' para entender el contexto macro y noticias recientes.
    3. Redactar un informe ejecutivo extenso en Markdown.
    
    Analizá el cruce entre los datos de precio y las noticias. ¿La noticia justifica la caída/subida? 
    ¿Hay un riesgo sistémico mencionado en la prensa?
    
    Formato:
    # 📈 Informe de Inteligencia: [Activo]
    ---
    ## 1. Métricas de Mercado
    ## 2. Análisis de Sentimiento (Noticias Globales)
    ## 3. Correlación Precio-Noticia
    ## 4. Conclusión y Recomendación
    """

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_input}
    ]

    try:
        # Primera llamada para que el modelo decida qué herramientas usar
        response = client.chat.complete(
            model="mistral-medium-latest",
            messages=messages,
            tools=tools,
        )

        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"[*] Ejecutando: {func_name} con {args}...")
                
                if func_name == "get_detailed_stock_data":
                    data = get_detailed_stock_data(args['symbol'])
                elif func_name == "get_global_news":
                    data = get_global_news(args['query'])
                
                messages.append({
                    "role": "tool",
                    "name": func_name,
                    "content": json.dumps(data),
                    "tool_call_id": tool_call.id,
                })
            
            # Segunda llamada para generar el informe final con todos los datos
            final = client.chat.complete(model="mistral-medium-latest", messages=messages)
            return final.choices[0].message.content
        
        return msg.content

    except Exception as e:
        return f"Error en el sistema: {str(e)}"

if __name__ == "__main__":
    print("--- Sistema de Inteligencia Financiera Avanzado ---")
    user_text = input("¿Qué activo o sector analizamos? (ej: Nvidia, Bitcoin, Sector Energético)\n> ")
    
    resultado = run_agent(user_text)
    print("\n" + resultado)