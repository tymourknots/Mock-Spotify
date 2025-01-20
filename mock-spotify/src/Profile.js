import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

function Profile() {
  const { username } = useParams();
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState(null);
  const [songRecommendations, setSongRecommendations] = useState([]);
  const [artistRecommendations, setArtistRecommendations] = useState([]);
  const [playlistRecommendations, setPlaylistRecommendations] = useState([]); // State for playlist recommendations
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch profile data
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

  // Fetch song recommendations
  useEffect(() => {
    fetch(`http://localhost:8111/api/recommendations/${username}`)
      .then((response) => {
        if (!response.ok) throw new Error('Failed to fetch recommendations');
        return response.json();
      })
      .then((data) => {
        console.log('Song Recommendations:', data); // Debugging log
        setSongRecommendations(data.songs || []); // Update state with song recommendations
      })
      .catch((err) => console.error('Error fetching song recommendations:', err.message));
  }, [username]);

  // Fetch artist recommendations
  useEffect(() => {
    fetch(`http://localhost:8111/recommend_artists/${username}`)
      .then((response) => {
        if (!response.ok) throw new Error('Failed to fetch artist recommendations');
        return response.json();
      })
      .then((data) => {
        console.log('Artist Recommendations:', data); // Debugging log
        setArtistRecommendations(data.artists || []); // Update state with artist recommendations
      })
      .catch((err) => console.error('Error fetching artist recommendations:', err.message));
  }, [username]);

  // Fetch playlist recommendations
  useEffect(() => {
    fetch(`http://localhost:8111/recommend_playlists/${username}`)
      .then((response) => {
        if (!response.ok) throw new Error('Failed to fetch playlist recommendations');
        return response.json();
      })
      .then((data) => {
        console.log('Playlist Recommendations:', data); // Debugging log
        setPlaylistRecommendations(data.playlists || []); // Update state with playlist recommendations
      })
      .catch((err) => console.error('Error fetching playlist recommendations:', err.message));
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

      {/* Songs Listened To */}
      <h2>Songs Listened To</h2>
      <div>
        {songs.length > 0 ? (
          songs.map((song) => (
            <div key={song.id}>
              <Link to={`/search_song?song_title=${encodeURIComponent(song.title)}`}>
                {song.title}
              </Link>{' '}
              - Genre: {song.genre}
            </div>
          ))
        ) : (
          <p>No songs found.</p>
        )}
      </div>

      {/* Followed Artists */}
      <h2>Followed Artists</h2>
      <div>
        {artists.length > 0 ? (
          artists.map((artist) => (
            <div key={artist.id}>
              <Link to={`/artist/${artist.id}`}>{artist.name}</Link> - Followed Since:{' '}
              {artist.followDate}
            </div>
          ))
        ) : (
          <p>No artists followed.</p>
        )}
      </div>

      {/* Created Playlists */}
      <h2>Created Playlists</h2>
      <div>
        {createdPlaylists.length > 0 ? (
          createdPlaylists.map((playlist) => (
            <div key={playlist.id}>
              <Link to={`/playlist/${playlist.id}`}>{playlist.title}</Link>
            </div>
          ))
        ) : (
          <p>You have not created any playlists.</p>
        )}
      </div>

      {/* Followed Playlists */}
      <h2>Followed Playlists</h2>
      <div>
        {followedPlaylists.length > 0 ? (
          followedPlaylists.map((playlist) => (
            <div key={playlist.id}>
              <Link to={`/playlist/${playlist.id}`}>{playlist.title}</Link>
            </div>
          ))
        ) : (
          <p>You are not following any playlists.</p>
        )}
      </div>

      {/* Song Recommendations */}
      <h2>Recommended Songs</h2>
      <div>
        {songRecommendations.length > 0 ? (
          songRecommendations.map((song) => (
            <div key={song.id}>
              <p>
                <strong>Title:</strong>{' '}
                <Link to={`/search_song?song_title=${encodeURIComponent(song.title)}`}>
                  {song.title}
                </Link>
              </p>
              <p>
                <strong>Artist:</strong> {song.artist} - <strong>Genre:</strong> {song.genre}
              </p>
            </div>
          ))
        ) : (
          <p>No song recommendations available.</p>
        )}
      </div>

      {/* Artist Recommendations */}
      <h2>Recommended Artists</h2>
      <div>
        {artistRecommendations.length > 0 ? (
          artistRecommendations.map((artist) => (
            <div key={artist.id}>
              <p>
                <strong>Name:</strong>{' '}
                <Link to={`/artist/${artist.id}`}>{artist.name}</Link>
              </p>
              <p>
                <strong>Biography:</strong> {artist.biography || 'No biography available.'}
              </p>
            </div>
          ))
        ) : (
          <p>No artist recommendations available.</p>
        )}
      </div>

      {/* Playlist Recommendations */}
      <h2>Recommended Playlists</h2>
      <div>
        {playlistRecommendations.length > 0 ? (
          playlistRecommendations.map((playlist) => (
            <div key={playlist.id}>
              <p>
                <strong>Playlist:</strong>{' '}
                <Link to={`/playlist/${playlist.id}`}>{playlist.title}</Link>
              </p>
            </div>
          ))
        ) : (
          <p>No playlist recommendations available.</p>
        )}
      </div>

      {/* Logout and Go Home Buttons */}
      <button onClick={handleLogout}>Logout</button>
      <button onClick={() => navigate('/')}>Go Back Home</button>
    </div>
  );
}

export default Profile;
