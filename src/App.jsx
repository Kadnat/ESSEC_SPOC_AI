import { useState } from 'react'
import './App.css'
import { analyzeCV } from './services/api'

function App() {
  const [file, setFile] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      if (!validTypes.includes(selectedFile.type)) {
        setError('Format invalide. Veuillez télécharger un fichier PDF ou DOCX.')
        return
      }
      
      // Validate file size (10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('Fichier trop volumineux. Maximum 10MB.')
        return
      }
      
      setFile(selectedFile)
      setResults(null)
      setError(null)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      handleFileChange({ target: { files: [droppedFile] } })
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-32 left-1/2 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="relative bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                🚀 JobMatchAI
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Intelligence Artificielle au service de votre carrière
              </p>
            </div>
            <div className="hidden md:flex items-center gap-4">
              <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                ✨ Powered by GPT-4o & HuggingFace
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Hero Section - Upload */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 mb-8 border border-gray-200">
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Analysez votre CV en quelques secondes
            </h2>
            <p className="text-gray-600">
              Notre IA analyse vos compétences et vous recommande les meilleurs métiers et formations
            </p>
          </div>
          
          <div 
            className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
              dragActive 
                ? 'border-blue-500 bg-blue-50 scale-105' 
                : 'border-gray-300 hover:border-blue-400 bg-gray-50/50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
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
              <div className="text-6xl mb-4 animate-bounce">
                {file ? '✅' : '📎'}
              </div>
              <p className="text-xl font-semibold text-gray-700 mb-2">
                {file ? (
                  <span className="text-green-600">✓ {file.name}</span>
                ) : (
                  "Glissez-déposez votre CV ici"
                )}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                ou cliquez pour sélectionner un fichier
              </p>
              <div className="flex items-center justify-center gap-4 text-xs text-gray-400">
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                  </svg>
                  PDF
                </span>
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                  </svg>
                  DOCX
                </span>
                <span>• Max 10MB</span>
              </div>
            </label>
          </div>

          {file && (
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="mt-6 w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              {analyzing ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyse en cours... Notre IA travaille pour vous
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  🧠 Analyser mon CV avec l'IA
                </span>
              )}
            </button>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg animate-shake">
              <div className="flex items-center">
                <span className="text-2xl mr-3">❌</span>
                <div>
                  <p className="font-semibold text-red-800">Erreur</p>
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Section */}
        {results && (
          <div className="space-y-8 animate-fade-in">
            {/* Profile Summary Card */}
            <div className="bg-gradient-to-br from-white to-blue-50/50 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-blue-100">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white text-2xl shadow-lg">
                  👤
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Profil Candidat
                  </h2>
                  <p className="text-sm text-gray-600">Analyse complète de votre CV</p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
                    <span className="text-2xl">👤</span>
                    <div>
                      <p className="text-xs text-gray-500">Nom</p>
                      <p className="font-semibold text-gray-900">{results.name}</p>
                    </div>
                  </div>
                  {results.email && (
                    <div className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
                      <span className="text-2xl">📧</span>
                      <div>
                        <p className="text-xs text-gray-500">Email</p>
                        <p className="font-semibold text-gray-900">{results.email}</p>
                      </div>
                    </div>
                  )}
                  {results.experienceYears !== null && (
                    <div className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm">
                      <span className="text-2xl">💼</span>
                      <div>
                        <p className="text-xs text-gray-500">Expérience</p>
                        <p className="font-semibold text-gray-900">{results.experienceYears} ans</p>
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <p className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <span className="text-lg">⚡</span>
                    Compétences Détectées
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {results.skills.slice(0, 12).map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg text-sm font-medium shadow-sm hover:shadow-md transition-shadow"
                      >
                        {skill}
                      </span>
                    ))}
                    {results.skills.length > 12 && (
                      <span className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg text-sm">
                        +{results.skills.length - 12} plus
                      </span>
                    )}
                  </div>

                  {results.languages && results.languages.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                        <span className="text-lg">🌍</span>
                        Langues
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {results.languages.map((lang, idx) => (
                          <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                            {lang}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {results.summary && (
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                  <p className="text-gray-700 leading-relaxed italic">
                    💡 "{results.summary}"
                  </p>
                </div>
              )}
            </div>

            {/* AI Insights - Move to top */}
            {results.aiInsights && (
              <div className="bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 rounded-2xl shadow-xl p-8 border-2 border-purple-200">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center text-white text-2xl shadow-lg animate-pulse">
                    🤖
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      Conseils IA Personnalisés
                    </h2>
                    <p className="text-sm text-gray-600">Recommandations par GPT-4o-mini</p>
                  </div>
                </div>
                <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6">
                  <p className="text-gray-800 leading-relaxed whitespace-pre-line">
                    {results.aiInsights}
                  </p>
                </div>
              </div>
            )}

            {/* Job Recommendations */}
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-gray-200">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center text-white text-2xl shadow-lg">
                  💼
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Métiers Recommandés
                  </h2>
                  <p className="text-sm text-gray-600">Top {results.topJobs.length} métiers qui matchent avec votre profil</p>
                </div>
              </div>

              <div className="grid gap-4">
                {results.topJobs.map((job, idx) => (
                  <div
                    key={idx}
                    className="group relative bg-gradient-to-br from-white to-gray-50 border-2 border-gray-200 rounded-xl p-6 hover:shadow-2xl hover:border-green-300 transition-all duration-300 hover:-translate-y-1"
                  >
                    {/* Match Score Badge */}
                    <div className="absolute -top-3 -right-3">
                      <div className="relative">
                        <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                          <div className="text-center">
                            <div className="text-xl font-bold text-white">{job.score}%</div>
                            <div className="text-xs text-white/90 -mt-1">match</div>
                          </div>
                        </div>
                        <div className="absolute inset-0 bg-green-400 rounded-full animate-ping opacity-20"></div>
                      </div>
                    </div>

                    <div className="pr-16">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-gray-900 group-hover:text-green-600 transition-colors">
                            {idx + 1}. {job.title}
                          </h3>
                          <div className="flex items-center gap-3 mt-2 text-sm text-gray-600">
                            {job.salaryRange && (
                              <span className="flex items-center gap-1 bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
                                💰 {job.salaryRange}
                              </span>
                            )}
                            {job.educationLevel && (
                              <span className="flex items-center gap-1 bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
                                🎓 {job.educationLevel}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <p className="text-gray-700 leading-relaxed mb-4">{job.description}</p>

                      {/* Required Skills */}
                      {job.requiredSkills && job.requiredSkills.length > 0 && (
                        <div className="mb-3">
                          <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1">
                            <span>✅</span> Compétences requises
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {job.requiredSkills.map((skill, i) => (
                              <span key={i} className="text-xs px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Missing Skills */}
                      {job.missingSkills && job.missingSkills.length > 0 && (
                        <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                          <p className="text-sm font-semibold text-orange-700 mb-2 flex items-center gap-1">
                            <span>⚠️</span> Compétences à développer
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {job.missingSkills.map((skill, i) => (
                              <span key={i} className="text-xs px-3 py-1 bg-orange-100 text-orange-800 rounded-full font-medium">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Real Job Offers from France Travail */}
            {results.realJobOffers && results.realJobOffers.length > 0 && (
              <div className="bg-gradient-to-br from-white to-green-50/50 backdrop-blur-sm rounded-2xl shadow-xl p-8 border-2 border-green-200">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center text-white text-2xl shadow-lg">
                      🎯
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        Offres d'Emploi Réelles
                      </h2>
                      <p className="text-sm text-gray-600">Mises à jour quotidiennes via France Travail API</p>
                    </div>
                  </div>
                  <span className="px-4 py-2 bg-green-600 text-white rounded-full text-sm font-semibold shadow-lg">
                    {results.realJobOffers.length} offres trouvées
                  </span>
                </div>

                <div className="grid gap-4">
                  {results.realJobOffers.map((job, idx) => (
                    <div
                      key={idx}
                      className="group relative bg-white border-l-4 border-green-500 rounded-xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1"
                    >
                      {/* Header */}
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1 pr-4">
                          <h3 className="text-lg font-bold text-gray-900 group-hover:text-green-600 transition-colors mb-2">
                            {job.title}
                          </h3>
                          <div className="flex flex-wrap items-center gap-3 text-sm">
                            <span className="flex items-center gap-1 text-gray-600">
                              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
                              </svg>
                              {job.company}
                            </span>
                            <span className="flex items-center gap-1 text-gray-600">
                              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                              </svg>
                              {job.location}
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">
                            {job.contractType}
                          </span>
                          <span className="text-xs text-gray-500">
                            Code ROME: {job.romeCode}
                          </span>
                        </div>
                      </div>

                      {/* Details */}
                      <div className="grid md:grid-cols-2 gap-3 mb-4 text-sm">
                        <div className="flex items-center gap-2 text-gray-600">
                          <span>💼</span>
                          <span>{job.experienceRequired}</span>
                        </div>
                        {job.salary && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <span>💰</span>
                            <span>{job.salary}</span>
                          </div>
                        )}
                      </div>

                      {/* Description */}
                      {job.description && (
                        <p className="text-sm text-gray-700 leading-relaxed mb-4 line-clamp-3">
                          {job.description}
                        </p>
                      )}

                      {/* Skills */}
                      {job.requiredSkills && job.requiredSkills.length > 0 && (
                        <div className="mb-4">
                          <p className="text-xs font-semibold text-gray-600 mb-2">Compétences requises:</p>
                          <div className="flex flex-wrap gap-2">
                            {job.requiredSkills.slice(0, 5).map((skill, i) => (
                              <span key={i} className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                                {skill}
                              </span>
                            ))}
                            {job.requiredSkills.length > 5 && (
                              <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                                +{job.requiredSkills.length - 5}
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Footer */}
                      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                        <span className="text-xs text-gray-500 flex items-center gap-1">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                          </svg>
                          Publié le {new Date(job.publicationDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
                        </span>
                        {job.url && (
                          <a
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg text-sm font-semibold hover:from-green-600 hover:to-emerald-700 transition-all shadow-md hover:shadow-lg"
                          >
                            Voir l'offre
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {results.realJobOffers.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">🔍</div>
                    <p className="text-gray-600">Aucune offre trouvée pour le moment.</p>
                    <p className="text-sm text-gray-500 mt-2">Essayez de modifier vos critères de recherche.</p>
                  </div>
                )}
              </div>
            )}

            {/* Training Recommendations */}
            {results.trainings && results.trainings.length > 0 && (
              <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-gray-200">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center text-white text-2xl shadow-lg">
                    🎓
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      Formations Recommandées
                    </h2>
                    <p className="text-sm text-gray-600">Pour booster vos compétences manquantes</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  {results.trainings.map((training, idx) => (
                    <div
                      key={idx}
                      className="group bg-gradient-to-br from-white to-purple-50 border-2 border-purple-200 rounded-xl p-6 hover:shadow-2xl hover:border-purple-400 transition-all duration-300 hover:-translate-y-1"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="text-lg font-bold text-gray-900 group-hover:text-purple-600 transition-colors leading-tight">
                          {training.title}
                        </h3>
                        <div className="ml-2 px-2 py-1 bg-purple-600 text-white text-xs font-bold rounded-full">
                          {training.score}%
                        </div>
                      </div>

                      <div className="space-y-2 text-sm text-gray-600 mb-4">
                        <p className="flex items-center gap-2">
                          <span>📚</span>
                          <span className="font-medium">{training.provider}</span>
                        </p>
                        <p className="flex items-center gap-2">
                          <span>⏱️</span>
                          <span>{training.duration}</span>
                        </p>
                      </div>

                      <div className="mb-4">
                        <p className="text-xs font-semibold text-gray-600 mb-2">Compétences acquises:</p>
                        <div className="flex flex-wrap gap-1">
                          {training.skills.slice(0, 4).map((skill, i) => (
                            <span key={i} className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                              {skill}
                            </span>
                          ))}
                          {training.skills.length > 4 && (
                            <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                              +{training.skills.length - 4}
                            </span>
                          )}
                        </div>
                      </div>

                      <a
                        href={training.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full text-center px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg text-sm font-semibold hover:from-purple-600 hover:to-pink-700 transition-all shadow-md hover:shadow-lg"
                      >
                        Voir la formation →
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* CTA */}
            <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-2xl shadow-2xl p-8 text-white text-center relative overflow-hidden">
              <div className="absolute inset-0 bg-black/10"></div>
              <div className="relative z-10">
                <h3 className="text-3xl font-bold mb-3">
                  🎯 Prêt à transformer votre carrière ?
                </h3>
                <p className="text-lg mb-6 text-white/90">
                  Téléchargez votre rapport complet et passez à l'action
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                  <button className="px-8 py-4 bg-white text-indigo-600 rounded-xl font-bold text-lg hover:bg-gray-100 transition-all shadow-xl hover:shadow-2xl transform hover:-translate-y-1">
                    📥 Télécharger le rapport PDF
                  </button>
                  <button 
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                    className="px-8 py-4 bg-white/10 backdrop-blur-sm border-2 border-white/30 text-white rounded-xl font-bold text-lg hover:bg-white/20 transition-all"
                  >
                    🔄 Analyser un autre CV
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative bg-gradient-to-r from-gray-900 to-gray-800 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8 text-center md:text-left">
            <div>
              <h3 className="text-2xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                🚀 JobMatchAI
              </h3>
              <p className="text-gray-400 text-sm">
                L'IA au service de votre orientation professionnelle
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Technologies</h4>
              <div className="space-y-1 text-sm text-gray-400">
                <p>🤖 OpenAI GPT-4o-mini</p>
                <p>🤗 Hugging Face Transformers</p>
                <p>⚡ FastAPI + React</p>
                <p>🇫🇷 France Travail API</p>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Projet</h4>
              <p className="text-sm text-gray-400">
                ESSEC AI Course 2025
              </p>
              <p className="text-sm text-gray-400 mt-2">
                Made with ❤️ by AI enthusiasts
              </p>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-700 text-center text-sm text-gray-400">
            <p>© 2025 JobMatchAI - Tous droits réservés</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
