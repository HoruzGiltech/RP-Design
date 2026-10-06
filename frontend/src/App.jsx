import { BrowserRouter, Route, Routes } from 'react-router-dom'

import Layout from './components/layout/Layout'
import { SiteProvider } from './context/SiteContext'
import HomePage from './pages/HomePage'

export default function App() {
  return (
    <SiteProvider>
      <BrowserRouter>
        <Routes>
          {/* Todas las páginas comparten el encabezado y el pie de Layout */}
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </SiteProvider>
  )
}
