import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

function SearchArtist() {
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const artistName = searchParams.get('artist_name');
    if (!artistName) {
      setArtists([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    fetch(`http://localhost:8111/api/search_artist?artist_name=${encodeURIComponent(artistName)}`)
      .then((response) => response.json())
      .then((data) => {
        console.log('Fetched artist data:', data);
        setArtists(data.artists || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching artist data:', error);
        setLoading(false);
      });
  }, [searchParams]);

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Artist Search Results</h1>
      {artists.length > 0 ? (
        artists.map((artist) => (
          <div key={artist.id}>
            <p>Name: {artist.name}</p>
            <p>Biography: {artist.biography}</p>
            <p>
              <a href={`/artist/${artist.id}`}>View Artist Profile</a>
            </p>
          </div>
        ))
      ) : (
        <p>No artists found.</p>
      )}
    </div>
  );
}

export default SearchArtist;
