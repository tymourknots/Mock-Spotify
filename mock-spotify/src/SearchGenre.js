import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

function SearchGenre() {
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const genreName = searchParams.get('genre_name');
    if (!genreName) {
      setGenres([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    fetch(`http://localhost:8111/api/search_genre?genre_name=${encodeURIComponent(genreName)}`)
      .then((response) => response.json())
      .then((data) => {
        console.log('Fetched genre data:', data);
        setGenres(data.genres || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching genre data:', error);
        setLoading(false);
      });
  }, [searchParams]);

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Genre Search Results</h1>
      {genres.length > 0 ? (
        genres.map((genre) => (
          <div key={genre.id}>
            <p>Name: {genre.name}</p>
            <p>Description: {genre.description}</p>
            <p>
              <a href={`/genre/${genre.id}`}>View Genre Details</a>
            </p>
          </div>
        ))
      ) : (
        <p>No genres found.</p>
      )}
    </div>
  );
}

export default SearchGenre;
