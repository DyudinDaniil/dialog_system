import React, { useState, useEffect } from 'react';

function ChatPage() {
  const API_BASE = "http://localhost:8000";
  const [locations, setLocations] = useState([]);
  const [characters, setCharacters] = useState([]);
  const [filteredNPCs, setFilteredNPCs] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [selectedNPC, setSelectedNPC] = useState(null);
  const [messages, setMessages] = useState([]);     // история диалога (сообщения)
  const [input, setInput] = useState("");           // текст текущего ввода пользователя

  // Загрузка локаций и персонажей при первом рендере
  useEffect(() => {
    fetch(`${API_BASE}/locations`)
      .then(res => res.json())
      .then(data => setLocations(data))
      .catch(err => console.error("Failed to fetch locations", err));
    fetch(`${API_BASE}/characters`)
      .then(res => res.json())
      .then(data => setCharacters(data))
      .catch(err => console.error("Failed to fetch characters", err));
  }, []);

  // Обновление списка NPC при изменении выбранной локации
  useEffect(() => {
    if (selectedLocation) {
      const npcs = characters.filter(c => c.location_id === selectedLocation);
      setFilteredNPCs(npcs);
    } else {
      setFilteredNPCs([]);
    }
    // Сбросить выбранного NPC и сообщения, если сменили локацию
    setSelectedNPC(null);
    setMessages([]);
  }, [selectedLocation]);

  // Если выбрали NPC, можно загрузить предыдущую историю (опционально)
  useEffect(() => {
    if (selectedNPC) {
      fetch(`${API_BASE}/dialogue/${selectedNPC}`)
        .then(res => res.json())
        .then(data => {
          // Преобразуем историю в наш формат state (role/text)
          const historyMsgs = data.map(item => ({
            role: item.role === "user" ? "Игрок" : "NPC",
            text: item.message
          }));
          setMessages(historyMsgs);
        })
        .catch(err => console.error("Failed to load dialogue history", err));
    }
  }, [selectedNPC]);

  const handleSend = async () => {
    const msg = input.trim();
    if (!msg) return;
    if (msg.toLowerCase() === "exit") {
      // Выход из диалога
      setSelectedNPC(null);
      setMessages([]);
      setInput("");
      return;
    }
    // Добавляем сообщение пользователя в локальный state сразу
    setMessages(prev => [...prev, { role: "Игрок", text: msg }]);
    setInput("");
    try {
      const resp = await fetch(`${API_BASE}/dialogue?character_id=${selectedNPC}&location_id=${selectedLocation}&message=${encodeURIComponent(msg)}`, {
        method: "POST"
      });
      const data = await resp.json();
      if (resp.ok && data.reply) {
        // Добавляем ответ NPC в state
        setMessages(prev => [...prev, { role: "NPC", text: data.reply }]);
      } else {
        console.error("Error from dialogue API", data);
      }
    } catch (err) {
      console.error("Failed to send message", err);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      {/* Шаг 1: Выбор локации */}
      {!selectedNPC && (
        <div>
          <h2>Выберите локацию:</h2>
          <select onChange={e => setSelectedLocation(Number(e.target.value))} defaultValue="">
            <option value="" disabled>-- Локация --</option>
            {locations.map(loc => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </select>
        </div>
      )}
      {/* Шаг 2: Выбор NPC (появляется после выбора локации) */}
      {selectedLocation && !selectedNPC && (
        <div style={{ marginTop: '20px' }}>
          <h3>Локация: {locations.find(l => l.id === selectedLocation)?.name}</h3>
          <p>Выберите персонажа для диалога:</p>
          <ul>
            {filteredNPCs.map(npc => (
              <li key={npc.id}>
                <button onClick={() => setSelectedNPC(npc.id)}>
                  {npc.name} ({npc.attitude || "отношение неизвестно"})
                </button>
              </li>
            ))}
            {filteredNPCs.length === 0 && <li><em>Нет NPC в этой локации.</em></li>}
          </ul>
        </div>
      )}
      {/* Шаг 3: Диалог с выбранным NPC */}
      {selectedLocation && selectedNPC && (
        <div style={{ marginTop: '20px' }}>
          <h3>Диалог с: {
            characters.find(c => c.id === selectedNPC)?.name
          }</h3>
          <div style={{ border: '1px solid #ccc', padding: '10px', height: '300px', overflowY: 'auto', marginBottom: '10px' }}>
            {messages.map((msg, idx) => (
              <p key={idx}><strong>{msg.role}:</strong> {msg.text}</p>
            ))}
          </div>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
            placeholder="Введите сообщение (или 'exit' для выхода)"
            style={{ width: '80%' }}
          />
          <button onClick={handleSend} style={{ marginLeft: '10px' }}>Отправить</button>
        </div>
      )}
    </div>
  );
}

export default ChatPage;
