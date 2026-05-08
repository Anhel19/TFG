import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-20 text-center">
      <h1 className="text-5xl font-bold text-slate-800 mb-4">
        Bienvenido a True Table 🍽️
      </h1>
      <p className="text-lg text-slate-600 mb-8">
        Reserva tu mesa en los mejores restaurantes en segundos.
      </p>
      <Link
        to="/reservar"
        className="inline-block px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition-colors"
      >
        Reservar ahora
      </Link>
    </div>
  )
}