import { BrowserRouter, Route, Routes } from 'react-router-dom'

import Layout from './components/layout/Layout'
import { SiteProvider } from './context/SiteContext'
import HomePage from './pages/HomePage'
import NotFoundPage from './pages/NotFoundPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import ProjectsPage from './pages/ProjectsPage'

export default function App() {
  return (
    <SiteProvider>
      <BrowserRouter>
        <Routes>
          {/* Todas las páginas comparten el encabezado y el pie de Layout */}
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/proyectos" element={<ProjectsPage />} />
            <Route path="/proyectos/:slug" element={<ProjectDetailPage />} />
            {/* Cualquier otra dirección */}
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </SiteProvider>
  )
}
