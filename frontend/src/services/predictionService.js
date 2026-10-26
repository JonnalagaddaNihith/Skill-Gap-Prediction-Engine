import api from './api';

export const predictionService = {
  getRecommendations: async () => {
    const response = await api.get('/api/prediction/recommendations');
    return response.data;
  },
};
