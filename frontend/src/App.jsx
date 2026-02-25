import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import DashboardPage from './pages/DashboardPage'
import ChatPage from './pages/ChatPage'
import TriggersPage from './pages/TriggersPage'
import BookingsPage from './pages/BookingsPage'
import GeneratorPage from './pages/GeneratorPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="triggers" element={<TriggersPage />} />
          <Route path="bookings" element={<BookingsPage />} />
          <Route path="generate" element={<GeneratorPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}