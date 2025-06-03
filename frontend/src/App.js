import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [currentTab, setCurrentTab] = useState('upload');
  const [cvData, setCvData] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useState({
    keywords: '',
    location: 'Remote',
    experience_level: 'mid-level',
    max_results: 20
  });

  useEffect(() => {
    fetchJobs();
    fetchApplications();
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/upload-cv`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCvData response.data.analysis);
      alert('CV uploaded and analyzed successfully!');
    } catch (error) {
      alert('Error uploading CV: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const searchJobs = async () => {
    if (!cvData) {
      alert('Please upload your CV first');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/search-jobs`, searchParams);
      setJobs(response.data.jobs);
      alert(`Found ${response.data.jobs.length} jobs!`);
      setCurrentTab('jobs');
    } catch (error) {
      alert('Error searching jobs: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const applyToJob = async (jobId) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/apply-job/${jobId}`);
      alert('Application submitted successfully!');
      fetchJobs();
      fetchApplications();
    } catch (error) {
      alert('Error applying to job: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const autoApplyJobs = async () => {
    if (!cvData) {
      alert('Please upload your CV first');
      return;
    }

    if (!window.confirm('This will automatically apply to multiple jobs. Continue?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/auto-apply?min_match_score=70&max_applications=5`);
      alert(response.data.message);
      fetchJobs();
      fetchApplications();
    } catch (error) {
      alert('Error in auto-apply: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/jobs`);
      setJobs(response.data.jobs);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchApplications = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/applications`);
      setApplications(response.data.applications);
    } catch (error) {
      console.error('Error fetching applications:', error);
    }
  };

  const getMatchScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">🚀</span>
              </div>
              <h1 className="ml-3 text-2xl font-bold text-gray-900">LinkedIn Dream Job Bot</h1>
            </div>
            <div className="text-sm text-gray-500">
              {cvData ? '✅ CV Loaded' : '⚠️ Upload CV to start'}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['upload', 'search', 'jobs', 'applications'].map((tab) => (
              <button
                key={tab}
                onClick={() => setCurrentTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  currentTab === tab
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab === 'upload' && '📄 '}
                {tab === 'search' && '🔍 '}
                {tab === 'jobs' && '💼 '}
                {tab === 'applications' && '📊 '}
                {tab.replace('-', ' ')}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* CV Upload Tab */}
          {currentTab === 'upload' && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Your CV</h2>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="cv-upload"
                />
                <label htmlFor="cv-upload" className="cursor-pointer">
                  <div className="text-gray-400 text-6xl mb-4">📄</div>
                  <p className="text-xl text-gray-600 mb-2">Click to upload your CV (PDF only)</p>
                  <p className="text-sm text-gray-500">AI will analyze your skills and experience</p>
                </label>
              </div>

              {loading && (
                <div className="mt-4 text-center">
                  <div className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-indigo-500">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing CV...
                  </div>
                </div>
              )}

              {cvData && (
                <div className="mt-6 bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">CV Analysis Results</h3>
                  
                  <div className="grid md:grid-cols-3 gap-4">
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Skills ({cvData.skills?.length || 0})</h4>
                      <div className="flex flex-wrap gap-1">
                        {cvData.skills?.slice(0, 8).map((skill, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Experience ({cvData.experience?.length || 0})</h4>
                      <div className="text-sm text-gray-600 space-y-1">
                        {cvData.experience?.slice(0, 3).map((exp, index) => (
                          <div key={index} className="truncate">{exp}</div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Education ({cvData.education?.length || 0})</h4>
                      <div className="text-sm text-gray-600 space-y-1">
                        {cvData.education?.slice(0, 3).map((edu, index) => (
                          <div key={index} className="truncate">{edu}</div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {cvData.summary && (
                    <div className="mt-4">
                      <h4 className="font-medium text-gray-700 mb-2">Professional Summary</h4>
                      <p className="text-sm text-gray-600">{cvData.summary}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Job Search Tab */}
          {currentTab === 'search' && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Search Dream Jobs</h2>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Keywords</label>
                  <input
                    type="text"
                    value={searchParams.keywords}
                    onChange={(e) => setSearchParams({...searchParams, keywords: e.target.value})}
                    placeholder="e.g., Python, React, Data Science"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                  <input
                    type="text"
                    value={searchParams.location}
                    onChange={(e) => setSearchParams({...searchParams, location: e.target.value})}
                    placeholder="e.g., Remote, San Francisco, New York"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Experience Level</label>
                  <select
                    value={searchParams.experience_level}
                    onChange={(e) => setSearchParams({...searchParams, experience_level: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="entry-level">Entry Level</option>
                    <option value="mid-level">Mid Level</option>
                    <option value="senior-level">Senior Level</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max Results</label>
                  <select
                    value={searchParams.max_results}
                    onChange={(e) => setSearchParams({...searchParams, max_results: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value={10}>10 jobs</option>
                    <option value={20}>20 jobs</option>
                    <option value={50}>50 jobs</option>
                  </select>
                </div>
              </div>

              <div className="mt-6 flex space-x-4">
                <button
                  onClick={searchJobs}
                  disabled={loading || !cvData}
                  className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {loading ? 'Searching...' : '🔍 Search Jobs'}
                </button>
                
                <button
                  onClick={autoApplyJobs}
                  disabled={loading || !cvData}
                  className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {loading ? 'Applying...' : '🚀 Auto Apply (Top 5)'}
                </button>
              </div>

              {!cvData && (
                <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                  <p className="text-yellow-800 text-sm">
                    ⚠️ Please upload your CV first to enable job search and auto-apply features.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Jobs Tab */}
          {currentTab === 'jobs' && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Job Opportunities ({jobs.length})</h2>
                <button
                  onClick={fetchJobs}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                >
                  🔄 Refresh
                </button>
              </div>

              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                        <p className="text-gray-600">{job.company} • {job.location}</p>
                        <p className="text-sm text-gray-500">{job.posted_date}</p>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMatchScoreColor(job.match_score)}`}>
                          {Math.round(job.match_score)}% match
                        </span>
                        
                        {job.applied ? (
                          <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                            ✅ Applied
                          </span>
                        ) : (
                          <button
                            onClick={() => applyToJob(job.id)}
                            disabled={loading}
                            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
                          >
                            Apply Now
                          </button>
                        )}
                      </div>
                    </div>
                    
                    <p className="text-gray-700 text-sm mb-2 line-clamp-2">{job.description}</p>
                    <p className="text-gray-600 text-xs"><strong>Requirements:</strong> {job.requirements}</p>
                    
                    <div className="mt-3 flex justify-between items-center">
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:text-indigo-800 text-sm"
                      >
                        View on LinkedIn →
                      </a>
                    </div>
                  </div>
                ))}
                
                {jobs.length === 0 && (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">🔍</div>
                    <p className="text-gray-600">No jobs found. Try searching for opportunities first!</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Applications Tab */}
          {currentTab === 'applications' && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">My Applications ({applications.length})</h2>
                <button
                  onClick={fetchApplications}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                >
                  🔄 Refresh
                </button>
              </div>

              <div className="space-y-4">
                {applications.map((app) => (
                  <div key={app.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{app.job_title}</h3>
                        <p className="text-gray-600">{app.company}</p>
                        <p className="text-sm text-gray-500">
                          Applied: {new Date(app.application_date).toLocaleDateString()}
                        </p>
                      </div>
                      
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        app.status === 'applied' ? 'bg-blue-100 text-blue-800' :
                        app.status === 'interview' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                      </span>
                    </div>
                    
                    <details className="mt-3">
                      <summary className="cursor-pointer text-indigo-600 hover:text-indigo-800 text-sm">
                        View Cover Letter
                      </summary>
                      <div className="mt-2 p-3 bg-gray-50 rounded-md text-sm text-gray-700 whitespace-pre-line">
                        {app.cover_letter}
                      </div>
                    </details>
                  </div>
                ))}
                
                {applications.length === 0 && (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">📊</div>
                    <p className="text-gray-600">No applications yet. Start applying to jobs to see them here!</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            🚀 LinkedIn Dream Job Bot - Your AI-powered job hunting assistant
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
