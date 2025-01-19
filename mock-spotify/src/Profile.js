import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

function Profile() {
  const { username } = useParams();
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`http://localhost:8111/api/profile/${username}`)
      .then((response) => {
        if (!response.ok) throw new Error('Failed to fetch profile data');
        return response.json();
      })
      .then((data) => {
        console.log('Profile data:', data); // Debugging log
        setProfileData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching profile:', err.message);
        setError(err.message);
        setLoading(false);
      });
  }, [username]);

  const handleLogout = () => {
    fetch('http://localhost:8111/api/logout', { method: 'POST' })
      .then(() => {
        navigate('/');
      })
      .catch((err) => console.error('Error logging out:', err));
  };

  if (loading) {
    return <p>Loading profile...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  // Use default values for destructuring to handle missing or undefined fields
  const {
    user = {},
    songs = [],
    artists = [],
    createdPlaylists = [],
    followedPlaylists = [],
  } = profileData || {};

  return (
    <div>
      <h1>Profile: {user.username || 'Unknown User'}</h1>
      <p>Email: {user.email || 'No email provided'}</p>

      <h2>Songs Listened To</h2>
      <div>
        {songs.length > 0 ? (
          songs.map((song) => (
            <div key={song.id}>
              <Link to={`/api/search_song?song_title=${encodeURIComponent(song.title)}`}>
                {song.title}
              </Link>{' '}
              - Genre: {song.genre}
            </div>
          ))
        ) : (
          <p>No songs found.</p>
        )}
      </div>

      <h2>Followed Artists</h2>
      <div>
        {artists.length > 0 ? (
          artists.map((artist) => (
            <div key={artist.id}>
              <Link to={`/api/artist/${artist.id}`}>{artist.name}</Link> - Followed Since:{' '}
              {artist.followDate}
            </div>
          ))
        ) : (
          <p>No artists followed.</p>
        )}
      </div>

      <h2>Created Playlists</h2>
      <div>
        {createdPlaylists.length > 0 ? (
          createdPlaylists.map((playlist) => (
            <div key={playlist.id}>
              <Link to={`/api/playlist/${playlist.id}`}>{playlist.title}</Link>
            </div>
          ))
        ) : (
          <p>You have not created any playlists.</p>
        )}
      </div>

      <h2>Followed Playlists</h2>
      <div>
        {followedPlaylists.length > 0 ? (
          followedPlaylists.map((playlist) => (
            <div key={playlist.id}>
              <Link to={`/api/playlist/${playlist.id}`}>{playlist.title}</Link>
            </div>
          ))
        ) : (
          <p>You are not following any playlists.</p>
        )}
      </div>

      <button onClick={handleLogout}>Logout</button>
      <button onClick={() => navigate('/')}>Go Back Home</button> {/* Go back home button */}
    </div>
  );
}

export default Profile;
