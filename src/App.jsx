import { useState } from 'react'
import './App.css'
import { analyzeCV } from './services/api'

function App() {
  const [file, setFile] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('jobs')

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      if (!validTypes.includes(selectedFile.type)) {
        setError('Format invalide. Veuillez télécharger un fichier PDF ou DOCX.')
        return
      }
      
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('Fichier trop volumineux. Maximum 10MB.')
        return
      }
      
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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
              J
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">JobMatchAI</h1>
              <p className="text-xs text-gray-500">Analyse CV par IA</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {!results && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-3">
                Analysez votre CV avec l'IA
              </h2>
              <p className="text-gray-600">
                Obtenez des recommandations personnalisées de métiers et formations
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-8">
              <label htmlFor="cv-upload" className="block cursor-pointer">
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="hidden"
                  id="cv-upload"
                />
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors">
                  <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="text-lg font-medium text-gray-900 mb-1">
                    {file ? file.name : 'Cliquez pour sélectionner votre CV'}
                  </p>
                  <p className="text-sm text-gray-500">
                    PDF ou DOCX, maximum 10MB
                  </p>
                </div>
              </label>

              {file && (
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="mt-6 w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {analyzing ? 'Analyse en cours...' : 'Analyser mon CV'}
                </button>
              )}

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
                  {error}
                </div>
              )}
            </div>
          </div>
        )}

        {results && (
          <div>
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{results.name}</h3>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                    {results.email && <span>📧 {results.email}</span>}
                    {results.experienceYears !== null && <span>💼 {results.experienceYears} ans d'expérience</span>}
                  </div>
                  
                  {results.skills.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Compétences</p>
                      <div className="flex flex-wrap gap-2">
                        {results.skills.map((skill, idx) => (
                          <span key={idx} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {results.aiInsights && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
                      <p className="text-sm font-medium text-blue-900 mb-2">�� Analyse IA</p>
                      <p className="text-sm text-gray-700 whitespace-pre-line">{results.aiInsights}</p>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => {
                    setResults(null)
                    setFile(null)
                  }}
                  className="ml-4 text-sm text-gray-600 hover:text-gray-900"
                >
                  Nouvelle analyse
                </button>
              </div>
            </div>

            <div className="mb-6">
              <div className="border-b border-gray-200">
                <nav className="flex gap-8">
                  <button
                    onClick={() => setActiveTab('jobs')}
                    className={'pb-4 px-1 border-b-2 font-medium text-sm transition-colors ' + 
                      (activeTab === 'jobs' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700')}
                  >
                    Métiers recommandés ({results.topJobs.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('offers')}
                    className={'pb-4 px-1 border-b-2 font-medium text-sm transition-colors ' +
                      (activeTab === 'offers' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700')}
                  >
                    Offres réelles ({results.realJobOffers.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('trainings')}
                    className={'pb-4 px-1 border-b-2 font-medium text-sm transition-colors ' +
                      (activeTab === 'trainings' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700')}
                  >
                    Formations ({results.trainings.length})
                  </button>
                </nav>
              </div>
            </div>

            <div>
              {activeTab === 'jobs' && (
                <div className="space-y-4">
                  {results.topJobs.map((job, idx) => (
                    <div key={idx} className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                          {job.score}% match
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-4">{job.description}</p>
                      {job.salaryRange && (
                        <p className="text-sm text-gray-500 mb-3">💰 {job.salaryRange}</p>
                      )}
                      {job.missingSkills.length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-2">Compétences à développer:</p>
                          <div className="flex flex-wrap gap-2">
                            {job.missingSkills.map((skill, i) => (
                              <span key={i} className="px-2 py-1 bg-orange-50 text-orange-700 rounded text-xs">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'offers' && (
                <div className="space-y-4">
                  {results.realJobOffers.length > 0 ? (
                    results.realJobOffers.map((job, idx) => (
                      <div key={idx} className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">{job.title}</h3>
                            <p className="text-sm text-gray-600">{job.company} • {job.location}</p>
                          </div>
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                            {job.contractType}
                          </span>
                        </div>
                        <p className="text-gray-600 text-sm mb-3">{job.description}</p>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">{job.experienceRequired}</span>
                          {job.url && (
                            <a
                              href={job.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 font-medium"
                            >
                              Voir l'offre →
                            </a>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
                      <p className="text-gray-500">Aucune offre d'emploi trouvée pour le moment</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'trainings' && (
                <div className="grid md:grid-cols-2 gap-4">
                  {results.trainings.map((training, idx) => (
                    <div key={idx} className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{training.title}</h3>
                      <p className="text-sm text-gray-600 mb-3">{training.provider} • {training.duration}</p>
                      <div className="mb-4">
                        <p className="text-sm font-medium text-gray-700 mb-2">Compétences acquises:</p>
                        <div className="flex flex-wrap gap-2">
                          {training.skills.map((skill, i) => (
                            <span key={i} className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      <a
                        href={training.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                      >
                        En savoir plus →
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <footer className="mt-16 border-t bg-white">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="text-center text-sm text-gray-600">
            <p className="mb-1">JobMatchAI - ESSEC AI Course 2025</p>
            <p className="text-xs text-gray-500">Powered by OpenAI GPT-4o • Hugging Face • France Travail API</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
