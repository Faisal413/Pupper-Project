import React from 'react';
import DogList from '../components/DogList';
import { useDogs } from '../hooks/useDogs';
import './Home.css';

const Home = () => {
  const { dogs, loading, error } = useDogs();

  return (
    <div className="home">
      <header className="home-header">
        <h1>Pupper - Dogs Available for Adoption</h1>
      </header>
      <main>
        <DogList dogs={dogs} loading={loading} error={error} />
      </main>
    </div>
  );
};

export default Home;