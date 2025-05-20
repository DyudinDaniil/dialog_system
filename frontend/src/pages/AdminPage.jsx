import React, { useState, useEffect } from 'react';

function AdminPage() {
  const API_BASE = "http://localhost:8000";
  const [lore, setLore] = useState("");
  const [locations, setLocations] = useState([]);
  const [characters, setCharacters] = useState([]);

  // Новые записи (для форм создания)
  const [newLoc, setNewLoc] = useState({ name: "", description: "", reputation: "", poi: "" });
  const [newChar, setNewChar] = useState({ name: "", age: "", sex: "", traits: "", attitude: "", locationId: "" });

  useEffect(() => {
    // Загружаем начальные данные
    fetch(`${API_BASE}/lore`).then(res => res.json()).then(data => setLore(data.content || "")).catch(console.error);
    fetch(`${API_BASE}/locations`).then(res => res.json()).then(data => setLocations(data)).catch(console.error);
    fetch(`${API_BASE}/characters`).then(res => res.json()).then(data => setCharacters(data)).catch(console.error);
  }, []);

  const saveLore = () => {
    fetch(`${API_BASE}/lore`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: lore })
    }).then(res => res.json())
      .then(data => alert("Лор обновлен!"))
      .catch(err => console.error("Failed to update lore", err));
  };

  const addLocation = () => {
    const repLevels = newLoc.reputation ? newLoc.reputation.split(',').map(s => s.trim()) : [];
    const poiList = newLoc.poi ? newLoc.poi.split(',').map(s => s.trim()) : [];
    const payload = {
      name: newLoc.name,
      description: newLoc.description,
      reputation_levels: repLevels,
      points_of_interest: poiList
    };
    fetch(`${API_BASE}/locations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(res => res.json())
      .then(data => {
        setLocations(prev => [...prev, data]);
        setNewLoc({ name: "", description: "", reputation: "", poi: "" });
      })
      .catch(err => console.error("Failed to add location", err));
  };

  const deleteLocation = (id) => {
    if (!window.confirm("Удалить локацию?")) return;
    fetch(`${API_BASE}/locations/${id}`, { method: "DELETE" })
      .then(res => {
        if (res.ok) {
          setLocations(prev => prev.filter(loc => loc.id !== id));
        }
      })
      .catch(err => console.error("Failed to delete location", err));
  };

  const addCharacter = () => {
    const traitsArr = newChar.traits ? newChar.traits.split(',').map(s => s.trim()) : [];
    const payload = {
      name: newChar.name,
      age: newChar.age ? Number(newChar.age) : null,
      sex: newChar.sex,
      traits: traitsArr,
      attitude: newChar.attitude,
      location_id: Number(newChar.locationId)
    };
    fetch(`${API_BASE}/characters`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(res => res.json())
      .then(data => {
        setCharacters(prev => [...prev, data]);
        setNewChar({ name: "", age: "", sex: "", traits: "", attitude: "", locationId: "" });
      })
      .catch(err => console.error("Failed to add character", err));
  };

  const deleteCharacter = (id) => {
    if (!window.confirm("Удалить персонажа?")) return;
    fetch(`${API_BASE}/characters/${id}`, { method: "DELETE" })
      .then(res => {
        if (res.ok) {
          setCharacters(prev => prev.filter(ch => ch.id !== id));
        }
      })
      .catch(err => console.error("Failed to delete character", err));
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Глобальный Лор</h2>
      <textarea value={lore} onChange={e => setLore(e.target.value)} rows={4} cols={80} />
      <br/>
      <button onClick={saveLore}>Сохранить лор</button>

      <hr/>

      <h2>Локации</h2>
      <ul>
        {locations.map(loc => (
          <li key={loc.id}>
            <strong>{loc.name}</strong> ({loc.description || "без описания"})
            <button onClick={() => deleteLocation(loc.id)} style={{ marginLeft: '10px' }}>Удалить</button>
          </li>
        ))}
      </ul>
      <h3>Добавить новую локацию:</h3>
      <div>
        <input
          type="text" placeholder="Название" value={newLoc.name}
          onChange={e => setNewLoc({ ...newLoc, name: e.target.value })}
        />
        <br/>
        <textarea
          placeholder="Описание" value={newLoc.description} rows={2} cols={60}
          onChange={e => setNewLoc({ ...newLoc, description: e.target.value })}
        />
        <br/>
        <input
          type="text" placeholder="Уровни репутации (через запятую)" value={newLoc.reputation}
          onChange={e => setNewLoc({ ...newLoc, reputation: e.target.value })}
        />
        <br/>
        <input
          type="text" placeholder="Точки интереса (через запятую)" value={newLoc.poi}
          onChange={e => setNewLoc({ ...newLoc, poi: e.target.value })}
        />
        <br/>
        <button onClick={addLocation}>Создать локацию</button>
      </div>

      <hr/>

      <h2>Персонажи (NPC)</h2>
      <ul>
        {characters.map(ch => (
          <li key={ch.id}>
            <strong>{ch.name}</strong> – {ch.age || "N/A"} лет, {ch.sex || "пол не указан"}, локация: {
              locations.find(loc => loc.id === ch.location_id)?.name || ch.location_id
            }, отношение: {ch.attitude || "не указано"}.
            <button onClick={() => deleteCharacter(ch.id)} style={{ marginLeft: '10px' }}>Удалить</button>
          </li>
        ))}
      </ul>
      <h3>Создать нового персонажа:</h3>
      <div>
        <input
          type="text" placeholder="Имя" value={newChar.name}
          onChange={e => setNewChar({ ...newChar, name: e.target.value })}
        />
        <input
          type="number" placeholder="Возраст" value={newChar.age}
          onChange={e => setNewChar({ ...newChar, age: e.target.value })}
          style={{ width: '80px', marginLeft: '5px' }}
        />
        <input
          type="text" placeholder="Пол" value={newChar.sex}
          onChange={e => setNewChar({ ...newChar, sex: e.target.value })}
          style={{ width: '80px', marginLeft: '5px' }}
        />
        <br/>
        <input
          type="text" placeholder="Черты характера (через запятую)" value={newChar.traits}
          onChange={e => setNewChar({ ...newChar, traits: e.target.value })}
          style={{ width: '300px' }}
        />
        <br/>
        <input
          type="text" placeholder="Отношение к игроку" value={newChar.attitude}
          onChange={e => setNewChar({ ...newChar, attitude: e.target.value })}
        />
        <br/>
        <select value={newChar.locationId} onChange={e => setNewChar({ ...newChar, locationId: e.target.value })}>
          <option value="">-- Локация --</option>
          {locations.map(loc => (
            <option key={loc.id} value={loc.id}>{loc.name}</option>
          ))}
        </select>
        <br/>
        <button onClick={addCharacter}>Добавить персонажа</button>
      </div>
    </div>
  );
}

export default AdminPage;
