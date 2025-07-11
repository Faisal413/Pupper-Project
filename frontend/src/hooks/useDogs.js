import { useState, useEffect } from 'react';
import ApiService from '../services/api';

export const useDogs = () => {
  const [dogs, setDogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDogs = async () => {
      try {
        setLoading(true);
        const data = await ApiService.fetchDogs();
        setDogs(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDogs();
  }, []);

  return { dogs, loading, error };
};