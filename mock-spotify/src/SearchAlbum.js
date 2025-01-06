import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

function SearchAlbum() {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const albumTitle = searchParams.get('album_title');
    if (!albumTitle) {
      setAlbums([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    fetch(`http://localhost:8111/api/search_album?album_title=${encodeURIComponent(albumTitle)}`)
      .then((response) => response.json())
      .then((data) => {
        console.log('Fetched album data:', data);
        setAlbums(data.albums || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching album data:', error);
        setLoading(false);
      });
  }, [searchParams]);

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Album Search Results</h1>
      {albums.length > 0 ? (
        albums.map((album) => (
          <div key={album.id}>
            <p>Title: {album.title}</p>
            <p>Artist: {album.artist}</p>
            <p>Release Year: {album.releaseYear}</p>
            <p>Genre: {album.genre}</p>
            <p>
              <a href={`/album/${album.id}`}>View Album Details</a>
            </p>
          </div>
        ))
      ) : (
        <p>No albums found.</p>
      )}
    </div>
  );
}

export default SearchAlbum;
