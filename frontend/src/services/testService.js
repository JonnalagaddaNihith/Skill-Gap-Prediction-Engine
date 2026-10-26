import api from './api';

export const testService = {
  getQuestions: async (params = {}) => {
    const { skillId, difficulty, numQuestions = 10 } = params;
    const queryParams = new URLSearchParams();
    if (skillId) queryParams.append('skill_id', skillId);
    if (difficulty) queryParams.append('difficulty', difficulty);
    queryParams.append('num_questions', numQuestions);

    const response = await api.get(`/api/test/questions?${queryParams}`);
    return response.data;
  },

  submitTest: async (testData) => {
    const response = await api.post('/api/test/submit', testData);
    return response.data;
  },

  getTestHistory: async () => {
    const response = await api.get('/api/test/history');
    return response.data;
  },

  getTestAttemptDetails: async (attemptId) => {
    const response = await api.get(`/api/test/history/${attemptId}`);
    return response.data;
  },
};
