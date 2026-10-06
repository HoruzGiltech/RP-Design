import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { SiteProvider } from './context/SiteContext'
import HomePage from './pages/HomePage'

export default function App() {
  return (
    <SiteProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </BrowserRouter>
    </SiteProvider>
  )
}
