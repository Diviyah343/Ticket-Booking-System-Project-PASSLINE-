import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Login from './pages/Login'
import Events from './pages/Events'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/events" element={<Events />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
