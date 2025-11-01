/**
 * API Service for JobMatchAI
 * Handles all HTTP requests to the FastAPI backend
 */

import axios from 'axios';

// Base URL for the API (backend)
const API_BASE_URL = 'http://localhost:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload CV file
 * @param {File} file - CV file (PDF or DOCX)
 * @returns {Promise} Response with file metadata
 */
export const uploadCV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload-cv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Analyze CV and get recommendations
 * @param {File} file - CV file (PDF or DOCX)
 * @returns {Promise} Analysis results with job and training recommendations
 */
export const analyzeCV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/analyze-cv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Get all available jobs
 * @returns {Promise} List of jobs
 */
export const getJobs = async () => {
  const response = await api.get('/api/jobs');
  return response.data;
};

/**
 * Get all available trainings
 * @returns {Promise} List of trainings
 */
export const getTrainings = async () => {
  const response = await api.get('/api/trainings');
  return response.data;
};

/**
 * Health check
 * @returns {Promise} API health status
 */
export const healthCheck = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

export default api;
