import { useEffect, useRef, useState } from "react";
import { Send, TrendingUp, Sparkles } from "lucide-react";

/**
 * Tipo de un mensaje en la conversación.
 * - role: indica quién lo emitió (user = humano, bot = asistente)
 * - content: texto del mensaje
 * - id: clave única para React
 */
type Message = {
  id: number;
  role: "user" | "bot";
  content: string;
};

// Preguntas sugeridas que aparecen al iniciar el chat
const SUGGESTIONS = [
  "¿Qué es la inflación?",
  "Diferencia entre PIB nominal y real",
  "¿Cómo funcionan las tasas de interés?",
  "¿Qué es un mercado bajista?",
];

// Respuestas demo (frontend-only). En producción se llamaría a una IA.
const DEMO_REPLIES: Record<string, string> = {
  inflación:
    "La **inflación** es el aumento generalizado y sostenido de los precios de bienes y servicios en una economía durante un período de tiempo, lo que reduce el poder adquisitivo del dinero.",
  pib: "El **PIB nominal** mide la producción a precios actuales, mientras que el **PIB real** la ajusta por inflación, mostrando el crecimiento económico verdadero.",
  interés:
    "Las **tasas de interés** son el precio del dinero. Los bancos centrales las suben para enfriar la economía y bajan para estimularla.",
  bajista:
    "Un **mercado bajista** (bear market) es cuando los precios de los activos caen ≥20% desde sus máximos recientes, reflejando pesimismo generalizado.",
};

const Index = () => {
  // Estado: lista de mensajes mostrados en pantalla
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      role: "bot",
      content:
        "👋 Hola, soy **EconBot**. Pregúntame sobre economía, finanzas, mercados o inversión.",
    },
  ]);
  const [input, setInput] = useState("");      // Texto en el input
  const [typing, setTyping] = useState(false); // Mostrar indicador "escribiendo..."
  const endRef = useRef<HTMLDivElement>(null); // Ancla para autoscroll

  // Autoscroll al último mensaje cada vez que cambian
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  // SEO dinámico
  useEffect(() => {
    document.title = "EconBot — Chatbot de preguntas económicas";
  }, []);

  /** Genera la respuesta del bot buscando palabras clave */
  const generateReply = (q: string): string => {
    const lower = q.toLowerCase();
    for (const key in DEMO_REPLIES) {
      if (lower.includes(key)) return DEMO_REPLIES[key];
    }
    return "Excelente pregunta económica. En una versión completa conectaría con una IA para darte una respuesta detallada con datos actualizados de mercado.";
  };

  /** Envía un mensaje del usuario y simula la respuesta del bot */
  const sendMessage = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    const userMsg: Message = { id: Date.now(), role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setTyping(true);

    // Simulación de latencia de IA
    setTimeout(() => {
      const botMsg: Message = {
        id: Date.now() + 1,
        role: "bot",
        content: generateReply(trimmed),
      };
      setMessages((prev) => [...prev, botMsg]);
      setTyping(false);
    }, 900);
  };

  // Renderiza **negrita** simple en los mensajes
  const renderContent = (text: string) =>
    text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
      part.startsWith("**") && part.endsWith("**") ? (
        <strong key={i} className="text-gradient-gold font-semibold">
          {part.slice(2, -2)}
        </strong>
      ) : (
        <span key={i}>{part}</span>
      )
    );

  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-6 md:py-10">
      {/* ====== CABECERA ====== */}
      <header className="w-full max-w-3xl mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-11 w-11 rounded-2xl bg-gradient-primary flex items-center justify-center shadow-glow">
            <TrendingUp className="h-6 w-6 text-primary-foreground" strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold tracking-tight">
              Econ<span className="text-gradient-primary">Bot</span>
            </h1>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Asistente económico
            </p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-card border border-border">
          <span className="h-2 w-2 rounded-full bg-primary animate-pulse" />
          <span className="text-xs text-muted-foreground">En línea</span>
        </div>
      </header>

      {/* ====== CONTENEDOR DEL CHAT ====== */}
      <section className="w-full max-w-3xl flex-1 flex flex-col bg-card/60 backdrop-blur-xl border border-border rounded-3xl shadow-soft overflow-hidden">
        {/* Lista de mensajes */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 min-h-[55vh] max-h-[65vh]">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex animate-fade-up ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[85%] md:max-w-[75%] px-4 py-3 rounded-2xl leading-relaxed text-sm md:text-base ${
                  m.role === "user"
                    ? "bg-gradient-primary text-primary-foreground rounded-br-md"
                    : "bg-muted text-foreground rounded-bl-md border border-border"
                }`}
              >
                {renderContent(m.content)}
              </div>
            </div>
          ))}

          {/* Indicador "escribiendo" */}
          {typing && (
            <div className="flex justify-start animate-fade-up">
              <div className="bg-muted border border-border rounded-2xl rounded-bl-md px-4 py-3 flex gap-1.5">
                {[0, 1, 2].map((i) => (
                  <span
                    key={i}
                    className="h-2 w-2 rounded-full bg-primary animate-pulse-dot"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Sugerencias rápidas (solo al inicio) */}
        {messages.length === 1 && (
          <div className="px-4 md:px-6 pb-3 flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="text-xs md:text-sm px-3 py-1.5 rounded-full border border-border bg-background/50 hover:bg-muted hover:border-primary/50 transition-colors text-muted-foreground hover:text-foreground"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Formulario de entrada */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage(input);
          }}
          className="p-3 md:p-4 border-t border-border bg-background/40 flex gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Pregunta sobre economía, mercados, inversión..."
            className="flex-1 bg-muted border border-border rounded-2xl px-4 py-3 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-transparent placeholder:text-muted-foreground"
            aria-label="Escribe tu pregunta económica"
          />
          <button
            type="submit"
            disabled={!input.trim() || typing}
            className="bg-gradient-primary text-primary-foreground rounded-2xl px-5 md:px-6 font-semibold flex items-center gap-2 hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity shadow-glow"
            aria-label="Enviar pregunta"
          >
            <Send className="h-4 w-4" />
            <span className="hidden md:inline">Enviar</span>
          </button>
        </form>
      </section>

      <footer className="w-full max-w-3xl mt-4 text-center text-xs text-muted-foreground">
        EconBot · Frontend de demostración · Las respuestas no constituyen asesoramiento financiero.
      </footer>
    </main>
  );
};

export default Index;
