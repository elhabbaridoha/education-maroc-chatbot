import { useState, useRef, useEffect } from "react"
import axios from "axios"
import "./App.css"

const API_URL = "https://dohael-education-maroc-api.hf.space/ask"

const EXAMPLES = [
  "Qu'est-ce que le baccalauréat marocain ?",
  "Comment s'inscrire à l'université au Maroc ?",
  "ما هي المواد الدراسية في الثانوي ؟",
  "Quelles sont les filières disponibles après le bac ?",
  "كيف يعمل نظام Massar ؟",
]

const HISTORY = [
  "Bac marocain 2024",
  "Inscription université",
  "Système Massar",
  "Filières après bac",
  "Orientation scolaire",
]

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "مرحبا بكم! Bienvenue ! Je suis votre assistant IA spécialisé dans le système éducatif marocain. Posez-moi vos questions en français, arabe ! 🇲🇦",
    },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [darkMode, setDarkMode] = useState(true)
  const [lang, setLang] = useState("fr")
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async (text) => {
    const question = text || input
    if (!question.trim() || loading) return
    setMessages((prev) => [...prev, { role: "user", content: question }])
    setInput("")
    setLoading(true)
    try {
      const res = await axios.post(API_URL, { question })
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.reponse }])
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "❌ Erreur de connexion. Veuillez réessayer." }])
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([{ role: "assistant", content: "مرحبا بكم! Bienvenue ! Nouvelle conversation démarrée. 🇲🇦" }])
  }

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`} dir={lang === "ar" ? "rtl" : "ltr"}>

      {/* ── SIDEBAR ── */}
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-header">
          <span className="brand-logo">🇲🇦</span>
          {sidebarOpen && <span className="brand-name">EduMaroc AI</span>}
        </div>

        {sidebarOpen && (
          <>
            <button className="new-chat-btn" onClick={clearChat}>
              <span className="plus-icon">＋</span> Nouvelle conversation
            </button>

            <div className="history-section">
              <p className="history-label">Récent</p>
              {HISTORY.map((h, i) => (
                <button key={i} className="history-item" onClick={() => setInput(h)}>
                  <span className="history-icon">💬</span>
                  <span>{h}</span>
                </button>
              ))}
            </div>

            <div className="sidebar-footer">
              <div className="lang-toggle">
                <button className={lang === "fr" ? "active" : ""} onClick={() => setLang("fr")}>FR</button>
                <button className={lang === "ar" ? "active" : ""} onClick={() => setLang("ar")}>عر</button>
              </div>
            </div>
          </>
        )}
      </aside>

      {/* ── MAIN ── */}
      <main className="main">

        {/* Header */}
        <header className="chat-header">
          <div className="header-left">
            <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
              ☰
            </button>
            <div className="header-info">
              <span className="header-title">Assistant Éducation Marocaine</span>
              <span className="header-sub">Français • العربية • Darija</span>
            </div>
          </div>&
          <div className="header-right">
            <div className="status-badge">
              <span className="status-dot" />
              En ligne
            </div>
            <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? "☀️" : "🌙"}
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="messages-area">
          {messages.map((msg, i) => (
            <div key={i} className={`msg-row ${msg.role}`}>
              <div className="msg-avatar">
                {msg.role === "assistant" ? "🇲🇦" : "👤"}
              </div>
              <div className="msg-bubble">
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="msg-row assistant">
              <div className="msg-avatar">🇲🇦</div>
              <div className="msg-bubble typing">
                <span /><span /><span />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Example chips */}
        <div className="chips-row">
          {EXAMPLES.slice(0, 3).map((ex, i) => (
            <button key={i} className="chip" onClick={() => sendMessage(ex)}>
              {ex}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="input-bar">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder={lang === "ar" ? "اكتب سؤالك هنا..." : "Posez votre question..."}
            rows={1}
            disabled={loading}
          />
          <button
            className="send-btn"
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
          >
            {loading ? "⏳" : "➤"}
          </button>
        </div>

        <p className="footer-note">
          Assistant IA spécialisé dans l'éducation marocaine · Powered by Mistral-7B LoRA
        </p>
      </main>
    </div>
  )
}