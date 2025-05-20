import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import AdminPage from './pages/AdminPage';

function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: '10px' }}>
        <Link to="/chat" style={{ marginRight: '15px' }}>Диалог с персонажем</Link>
        <Link to="/admin">Управление лором/персонажами</Link>
      </nav>
      <Routes>
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="*" element={<ChatPage />} />  {/* по умолчанию открываем чат */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
