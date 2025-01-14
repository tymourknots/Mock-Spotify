import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

function SearchPlaylist() {
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const playlistTitle = searchParams.get('playlist_title');
    if (!playlistTitle) {
      setPlaylists([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    fetch(`http://localhost:8111/api/search_playlist?playlist_title=${encodeURIComponent(playlistTitle)}`)
      .then((response) => response.json())
      .then((data) => {
        console.log('Fetched playlist data:', data);
        setPlaylists(data.playlists || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching playlist data:', error);
        setLoading(false);
      });
  }, [searchParams]);

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Playlist Search Results</h1>
      {playlists.length > 0 ? (
        playlists.map((playlist) => (
          <div key={playlist.id}>
            <p>Title: {playlist.title}</p>
            <p>Description: {playlist.description}</p>
            <p>Creation Year: {playlist.creationYear}</p>
            <p>
              <a href={`/playlist/${playlist.id}`}>View Playlist Details</a>
            </p>
          </div>
        ))
      ) : (
        <p>No playlists found.</p>
      )}
    </div>
  );
}

export default SearchPlaylist;
