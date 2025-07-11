import React from 'react';
import './DogCard.css';

const DogCard = ({ dog, onImageClick }) => {
  return (
    <div className="dog-card">
      <img 
        src={dog.thumbnail_url} 
        alt={dog.name}
        className="dog-thumbnail"
        onClick={() => onImageClick(dog.original_url)}
      />
      <div className="dog-info">
        <h3>{dog.name}</h3>
        {dog.breed && <p><strong>Breed:</strong> {dog.breed}</p>}
        <p>{dog.description}</p>
      </div>
    </div>
  );
};

export default DogCard;