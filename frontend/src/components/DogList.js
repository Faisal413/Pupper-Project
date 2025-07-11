import React from 'react';
import DogCard from './DogCard';
import './DogList.css';

const DogList = ({ dogs, loading, error }) => {
  const handleImageClick = (originalUrl) => {
    window.open(originalUrl, '_blank');
  };

  if (loading) return <div className="loading">Loading dogs...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="dogs-grid">
      {dogs.map(dog => (
        <DogCard 
          key={dog.id} 
          dog={dog} 
          onImageClick={handleImageClick}
        />
      ))}
    </div>
  );
};

export default DogList;