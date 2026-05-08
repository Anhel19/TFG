import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="max-w-md mx-auto px-4 py-20 text-center">
      <h1 className="text-6xl font-bold text-slate-800 mb-2">404</h1>
      <p className="text-lg text-slate-600 mb-6">
        Esta página no existe.
      </p>
      <Link
        to="/"
        className="inline-block px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors"
      >
        Volver al inicio
      </Link>
    </div>
  )
}