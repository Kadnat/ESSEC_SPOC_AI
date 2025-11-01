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
    <div className="min-h-screen" style={{ backgroundColor: '#f5f5f5' }}>
      {/* Header France Travail style */}
      <header style={{ backgroundColor: '#003b80' }} className="shadow-md">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl" style={{ backgroundColor: '#ff6f00' }}>
                JM
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">JobMatch AI</h1>
                <p className="text-sm text-blue-100">Votre assistant carrière intelligent</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded" style={{ backgroundColor: 'rgba(255,255,255,0.1)' }}>
              <span className="text-sm text-white">🤖 Propulsé par IA</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Upload Section */}
        {!results && (
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-4xl font-bold mb-3" style={{ color: '#003b80' }}>
                Analysez votre CV gratuitement
              </h2>
              <p className="text-lg" style={{ color: '#666' }}>
                Découvrez les métiers qui vous correspondent et les formations adaptées à votre profil
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-lg border-2 p-8" style={{ borderColor: '#e0e0e0' }}>
              <label htmlFor="cv-upload" className="block cursor-pointer">
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="hidden"
                  id="cv-upload"
                />
                <div className="border-3 border-dashed rounded-xl p-16 text-center transition-all hover:scale-[1.02]" style={{ 
                  borderColor: file ? '#ff6f00' : '#003b80',
                  backgroundColor: file ? '#fff3e0' : '#f0f7ff'
                }}>
                  <svg className="mx-auto h-20 w-20 mb-4" style={{ color: '#003b80' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="text-2xl font-bold mb-2" style={{ color: '#003b80' }}>
                    {file ? '✓ ' + file.name : 'Déposez votre CV ici'}
                  </p>
                  <p className="text-base" style={{ color: '#666' }}>
                    ou cliquez pour sélectionner • PDF ou DOCX • Max 10 Mo
                  </p>
                </div>
              </label>

              {file && (
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="mt-8 w-full text-white py-4 px-8 rounded-lg font-bold text-lg shadow-lg transition-all disabled:opacity-50"
                  style={{ 
                    backgroundColor: analyzing ? '#999' : '#ff6f00',
                    cursor: analyzing ? 'not-allowed' : 'pointer'
                  }}
                  onMouseEnter={(e) => !analyzing && (e.target.style.backgroundColor = '#e56300')}
                  onMouseLeave={(e) => !analyzing && (e.target.style.backgroundColor = '#ff6f00')}
                >
                  {analyzing ? '⏳ Analyse en cours...' : '🚀 Analyser mon CV'}
                </button>
              )}

              {error && (
                <div className="mt-6 p-4 rounded-lg border-2" style={{ backgroundColor: '#ffebee', borderColor: '#ef5350' }}>
                  <p className="text-sm font-medium" style={{ color: '#c62828' }}>⚠️ {error}</p>
                </div>
              )}
            </div>

            {/* Info cards */}
            <div className="grid md:grid-cols-3 gap-6 mt-12">
              <div className="bg-white rounded-lg p-6 shadow-md border-t-4" style={{ borderTopColor: '#003b80' }}>
                <div className="text-4xl mb-3">🎯</div>
                <h3 className="font-bold text-lg mb-2" style={{ color: '#003b80' }}>Matching IA</h3>
                <p className="text-sm" style={{ color: '#666' }}>
                  Trouvez les métiers qui correspondent à vos compétences
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 shadow-md border-t-4" style={{ borderTopColor: '#ff6f00' }}>
                <div className="text-4xl mb-3">💼</div>
                <h3 className="font-bold text-lg mb-2" style={{ color: '#003b80' }}>Offres réelles</h3>
                <p className="text-sm" style={{ color: '#666' }}>
                  Accédez aux offres d'emploi France Travail
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 shadow-md border-t-4" style={{ borderTopColor: '#003b80' }}>
                <div className="text-4xl mb-3">📚</div>
                <h3 className="font-bold text-lg mb-2" style={{ color: '#003b80' }}>Formations</h3>
                <p className="text-sm" style={{ color: '#666' }}>
                  Développez vos compétences manquantes
                </p>
              </div>
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
                <div className="space-y-5">
                  {results.topJobs.map((job, idx) => (
                    <div key={idx} className="bg-white rounded-xl shadow-lg border-l-4 p-7 transition-all hover:shadow-2xl" style={{ borderLeftColor: '#003b80' }}>
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-bold" style={{ color: '#003b80' }}>{job.title}</h3>
                        <span className="px-4 py-2 rounded-full text-sm font-bold" style={{
                          backgroundColor: '#e8f5e9',
                          color: '#2e7d32'
                        }}>
                          ✓ {job.score}% match
                        </span>
                      </div>
                      <p className="text-base mb-4 leading-relaxed" style={{ color: '#555' }}>{job.description}</p>
                      {job.salaryRange && (
                        <p className="text-sm font-medium mb-4" style={{ color: '#666' }}>💰 {job.salaryRange}</p>
                      )}
                      {job.missingSkills.length > 0 && (
                        <div className="mt-5 p-4 rounded-lg" style={{ backgroundColor: '#fff3e0' }}>
                          <p className="text-sm font-bold mb-3" style={{ color: '#e65100' }}>📈 Compétences à développer:</p>
                          <div className="flex flex-wrap gap-2">
                            {job.missingSkills.map((skill, i) => (
                              <span key={i} className="px-3 py-1 rounded text-xs font-medium" style={{
                                backgroundColor: '#ffffff',
                                color: '#e65100',
                                border: '1px solid #ffcc80'
                              }}>
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
                <div className="space-y-5">
                  {results.realJobOffers.length > 0 ? (
                    results.realJobOffers.map((job, idx) => (
                      <div key={idx} className="bg-white rounded-xl shadow-lg border-l-4 p-7 transition-all hover:shadow-2xl" style={{ borderLeftColor: '#ff6f00' }}>
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="text-xl font-bold mb-2" style={{ color: '#003b80' }}>{job.title}</h3>
                            <p className="text-base" style={{ color: '#666' }}>
                              <span className="font-semibold">{job.company}</span> • 📍 {job.location}
                            </p>
                          </div>
                          <span className="px-4 py-2 rounded-lg text-xs font-bold" style={{
                            backgroundColor: '#e3f2fd',
                            color: '#003b80'
                          }}>
                            {job.contractType}
                          </span>
                        </div>
                        <p className="text-base mb-4 leading-relaxed" style={{ color: '#555' }}>{job.description}</p>
                        <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: '#e0e0e0' }}>
                          <span className="text-sm font-medium" style={{ color: '#666' }}>👤 {job.experienceRequired}</span>
                          {job.url && (
                            <a
                              href={job.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-5 py-2 rounded-lg font-bold text-sm transition-all"
                              style={{
                                backgroundColor: '#ff6f00',
                                color: '#ffffff'
                              }}
                              onMouseEnter={(e) => e.target.style.backgroundColor = '#e56300'}
                              onMouseLeave={(e) => e.target.style.backgroundColor = '#ff6f00'}
                            >
                              Voir l'offre →
                            </a>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="bg-white rounded-xl shadow-lg p-16 text-center">
                      <div className="text-6xl mb-4">🔍</div>
                      <p className="text-lg font-medium" style={{ color: '#666' }}>Aucune offre d'emploi trouvée pour le moment</p>
                      <p className="text-sm mt-2" style={{ color: '#999' }}>Réessayez avec un autre profil</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'trainings' && (
                <div className="grid md:grid-cols-2 gap-6">
                  {results.trainings.map((training, idx) => (
                    <div key={idx} className="bg-white rounded-xl shadow-lg border-t-4 p-7 transition-all hover:shadow-2xl" style={{ borderTopColor: '#003b80' }}>
                      <h3 className="text-xl font-bold mb-3" style={{ color: '#003b80' }}>{training.title}</h3>
                      <p className="text-sm mb-5" style={{ color: '#666' }}>
                        <span className="font-semibold">{training.provider}</span> • ⏱️ {training.duration}
                      </p>
                      <div className="mb-5">
                        <p className="text-sm font-bold mb-3" style={{ color: '#003b80' }}>✅ Compétences acquises:</p>
                        <div className="flex flex-wrap gap-2">
                          {training.skills.map((skill, i) => (
                            <span key={i} className="px-3 py-1 rounded text-xs font-medium" style={{
                              backgroundColor: '#e8f5e9',
                              color: '#2e7d32'
                            }}>
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      <a
                        href={training.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block px-5 py-2 rounded-lg font-bold text-sm transition-all"
                        style={{
                          backgroundColor: '#f5f5f5',
                          color: '#003b80'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.backgroundColor = '#003b80'
                          e.target.style.color = '#ffffff'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.backgroundColor = '#f5f5f5'
                          e.target.style.color = '#003b80'
                        }}
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

      <footer className="mt-20" style={{ backgroundColor: '#003b80' }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid md:grid-cols-3 gap-8 text-white mb-8">
            <div>
              <h4 className="font-bold text-lg mb-3">JobMatch AI</h4>
              <p className="text-sm text-blue-100">
                Votre assistant carrière intelligent propulsé par l'IA
              </p>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-3">Technologies</h4>
              <ul className="text-sm text-blue-100 space-y-1">
                <li>• OpenAI GPT-4o-mini</li>
                <li>• Hugging Face Transformers</li>
                <li>• France Travail API</li>
                <li>• React + FastAPI</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-3">Projet</h4>
              <p className="text-sm text-blue-100">
                ESSEC Business School<br />
                Intelligence Artificielle 2025
              </p>
            </div>
          </div>
          <div className="pt-6 border-t text-center text-sm" style={{ borderColor: 'rgba(255,255,255,0.2)', color: '#b3d9ff' }}>
            <p>© 2025 JobMatch AI • Fait avec ❤️ pour l'ESSEC</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
