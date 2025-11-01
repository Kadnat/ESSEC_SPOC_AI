import { useState } from 'react'
import './App.css'
import { analyzeCV } from './services/api'

function App() {
  const [file, setFile] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResults(null)
      setError(null)
    }
  }

  const handleAnalyze = async () => {
    if (!file) return
    
    setAnalyzing(true)
    setError(null)
    
    try {
      // Call the backend API
      const data = await analyzeCV(file)
      setResults({
        name: data.cv_analysis.name,
        email: data.cv_analysis.email,
        skills: data.cv_analysis.skills,
        experienceYears: data.cv_analysis.experience_years,
        education: data.cv_analysis.education,
        languages: data.cv_analysis.languages,
        summary: data.cv_analysis.summary,
        topJobs: data.job_recommendations.map(job => ({
          id: job.job_id,
          title: job.title,
          description: job.description,
          score: Math.round(job.match_score * 100),
          requiredSkills: job.required_skills,
          missingSkills: job.missing_skills,
          salaryRange: job.salary_range,
          educationLevel: job.education_level,
        })),
        realJobOffers: data.real_job_offers.map(job => ({
          id: job.id,
          title: job.title,
          company: job.company,
          location: job.location,
          contractType: job.contract_type,
          description: job.description,
          requiredSkills: job.required_skills,
          experienceRequired: job.experience_required,
          salary: job.salary,
          publicationDate: job.publication_date,
          url: job.url,
          romeCode: job.rome_code,
          source: job.source,
        })),
        trainings: data.training_recommendations.map(training => ({
          id: training.training_id,
          title: training.title,
          provider: training.provider,
          url: training.url,
          duration: training.duration,
          skills: training.skills_acquired,
          score: Math.round(training.relevance_score * 100),
        })),
        aiInsights: data.ai_insights,
      })
    } catch (err) {
      console.error('Error analyzing CV:', err)
      setError(err.response?.data?.detail || 'Erreur lors de l\'analyse du CV. Vérifiez que le backend est lancé sur le port 8001.')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            🚀 JobMatch<span className="text-blue-600">AI</span>
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Analysez votre CV et découvrez les métiers qui vous correspondent
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            📄 Téléchargez votre CV
          </h2>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              className="hidden"
              id="cv-upload"
            />
            <label 
              htmlFor="cv-upload"
              className="cursor-pointer"
            >
              <div className="text-6xl mb-4">📎</div>
              <p className="text-lg text-gray-700 mb-2">
                {file ? file.name : "Cliquez pour sélectionner un fichier"}
              </p>
              <p className="text-sm text-gray-500">
                Formats acceptés: PDF, DOCX (Max 10MB)
              </p>
            </label>
          </div>

          {file && (
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="mt-6 w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {analyzing ? "🔄 Analyse en cours..." : "🧠 Analyser mon CV"}
            </button>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">
                <strong>❌ Erreur:</strong> {error}
              </p>
            </div>
          )}
        </div>

        {/* Results Section */}
        {results && (
          <div className="space-y-6">
            {/* Profile Summary */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                👤 Profil analysé
              </h2>
              <div className="space-y-3">
                <p className="text-lg"><strong>Nom:</strong> {results.name}</p>
                {results.email && (
                  <p className="text-lg"><strong>Email:</strong> {results.email}</p>
                )}
                {results.experienceYears && (
                  <p className="text-lg"><strong>Expérience:</strong> {results.experienceYears} ans</p>
                )}
                <div>
                  <strong className="text-lg">Compétences détectées:</strong>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {results.skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                {results.summary && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <p className="text-gray-700 italic">{results.summary}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Job Recommendations */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                💼 Métiers recommandés
              </h2>
              <div className="space-y-4">
                {results.topJobs.map((job, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {job.title}
                        </h3>
                        {job.salaryRange && (
                          <p className="text-sm text-gray-600 mt-1">💰 {job.salaryRange}</p>
                        )}
                      </div>
                      <div className="flex items-center">
                        <span className="text-2xl font-bold text-green-600">
                          {job.score}%
                        </span>
                        <span className="ml-2 text-sm text-gray-500">match</span>
                      </div>
                    </div>
                    <p className="text-gray-700 text-sm mb-3">{job.description}</p>
                    {job.missingSkills.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-orange-600">
                          ⚠️ Compétences à développer:
                        </p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {job.missingSkills.map((skill, i) => (
                            <span key={i} className="text-xs px-2 py-1 bg-orange-50 text-orange-700 rounded">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* AI Insights */}
            {results.aiInsights && (
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow-lg p-8 border-2 border-purple-200">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                  🤖 Conseils IA personnalisés
                </h2>
                <p className="text-gray-800 leading-relaxed">
                  {results.aiInsights}
                </p>
              </div>
            )}

            {/* Real Job Offers from France Travail */}
            {results.realJobOffers && results.realJobOffers.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  💼 Offres d'emploi réelles
                </h2>
                <p className="text-sm text-gray-500 mb-6">
                  Powered by France Travail API - Offres mises à jour quotidiennement
                </p>
                <div className="space-y-4">
                  {results.realJobOffers.map((job, idx) => (
                    <div
                      key={idx}
                      className="border-l-4 border-green-500 bg-green-50 rounded-lg p-5 hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {job.title}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            🏢 {job.company} • 📍 {job.location}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            📝 {job.contractType} • {job.experienceRequired}
                            {job.salary && ` • 💰 ${job.salary}`}
                          </p>
                        </div>
                        <span className="text-xs px-2 py-1 bg-green-600 text-white rounded">
                          {job.source}
                        </span>
                      </div>
                      
                      {job.description && (
                        <p className="text-sm text-gray-700 mt-3 line-clamp-3">
                          {job.description.substring(0, 200)}...
                        </p>
                      )}
                      
                      {job.requiredSkills && job.requiredSkills.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {job.requiredSkills.slice(0, 5).map((skill, i) => (
                            <span key={i} className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                              {skill}
                            </span>
                          ))}
                        </div>
                      )}
                      
                      <div className="flex gap-3 mt-4">
                        {job.url && (
                          <a
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-green-600 hover:text-green-700 font-medium"
                          >
                            Voir l'offre →
                          </a>
                        )}
                        <span className="text-xs text-gray-400">
                          Publié le {new Date(job.publicationDate).toLocaleDateString('fr-FR')}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Training Recommendations */}
            {results.trainings && results.trainings.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                  🎓 Formations recommandées
                </h2>
                <div className="space-y-4">
                  {results.trainings.map((training, idx) => (
                    <div
                      key={idx}
                      className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {training.title}
                        </h3>
                        <span className="text-sm font-medium text-purple-600">
                          {training.score}% pertinent
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        📚 {training.provider} • ⏱️ {training.duration}
                      </p>
                      <div className="flex flex-wrap gap-2 mt-3">
                        {training.skills.map((skill, i) => (
                          <span key={i} className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                            {skill}
                          </span>
                        ))}
                      </div>
                      <a
                        href={training.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium"
                      >
                        🔗 Voir la formation →
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* CTA */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-lg p-8 text-white text-center">
              <h3 className="text-2xl font-bold mb-2">
                🎯 Prêt à booster votre carrière ?
              </h3>
              <p className="mb-4">
                Téléchargez un rapport complet de votre analyse
              </p>
              <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                📥 Télécharger le rapport PDF
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-600 text-sm">
          <p>JobMatchAI - Projet ESSEC AI Course 2025</p>
          <p className="mt-1">Powered by Hugging Face 🤗 & FastAPI ⚡</p>
        </div>
      </footer>
    </div>
  )
}

export default App
