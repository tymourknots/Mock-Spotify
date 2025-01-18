import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function PlaylistDetails() {
  const { playlistId } = useParams();
  const [playlist, setPlaylist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`http://localhost:8111/api/playlist/${playlistId}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Playlist not found');
        }
        return response.json();
      })
      .then((data) => {
        setPlaylist(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [playlistId]);

  if (loading) return <p>Loading playlist details...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Playlist Details: {playlist.title}</h1>
      <div>
        <p>Title: {playlist.title}</p>
        <p>Description: {playlist.description}</p>
        <p>Creation Year: {playlist.creationYear}</p>
      </div>

      <h2>Created by</h2>
      <div>
        {playlist.creator ? (
          <p>{playlist.creator.name}</p>
        ) : (
          <p>Creator not found.</p>
        )}
      </div>

      <h2>Followers</h2>
      <div>
        {playlist.followers.length > 0 ? (
          playlist.followers.map((follower) => <p key={follower.id}>{follower.name}</p>)
        ) : (
          <p>No followers for this playlist.</p>
        )}
      </div>

      <h2>Songs in this Playlist</h2>
      <div>
        {playlist.songs.length > 0 ? (
          playlist.songs.map((song) => (
            <div key={song.id}>
              <Link to={`/search_song?song_id=${song.id}`}>{song.title}</Link> - Duration: {song.duration} seconds
            </div>
          ))
        ) : (
          <p>No songs found in this playlist.</p>
        )}
      </div>

      <p>
        <Link to="/">Go back to the home page</Link>
      </p>
    </div>
  );
}

export default PlaylistDetails;
