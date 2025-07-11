import { config } from '../utils/config';

const API_BASE_URL = config.API_BASE_URL;

class ApiService {
  async fetchDogs() {
    try {
      const response = await fetch(`${API_BASE_URL}/dogs`);
      if (!response.ok) throw new Error('Failed to fetch dogs');
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      // Mock data for development
      return [
        {
          id: 1,
          name: 'Buddy',
          breed: 'Labrador Retriever',
          description: 'Friendly and energetic dog looking for a loving home',
          thumbnail_url: '/placeholder-dog.jpg',
          original_url: '/placeholder-dog-large.jpg'
        }
      ];
    }
  }
}

export default new ApiService();