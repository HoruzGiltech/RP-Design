import { useSite } from '../../context/SiteContext'
import Marquee from '../ui/Marquee'
import './SpecialtiesStrip.css'

/** Franja de especialidades, entre la Portada y Servicios. */
export default function SpecialtiesStrip() {
  const { data: site } = useSite()
  const { specialties } = site

  // Sin especialidades visibles no se dibuja ni la franja ni sus líneas
  if (specialties.length === 0) return null

  return (
    <div className="specialties-strip">
      <div className="container specialties-strip__inner">
        <Marquee items={specialties} label="Especialidades" />
      </div>
    </div>
  )
}
