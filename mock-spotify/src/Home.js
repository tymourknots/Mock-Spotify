import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css'; // Importing the CSS file

function Home() {
  const [songTitle, setSongTitle] = useState('');
  const [albumTitle, setAlbumTitle] = useState('');
  const [artistName, setArtistName] = useState('');
  const [genreName, setGenreName] = useState('');
  const [playlistTitle, setPlaylistTitle] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const navigate = useNavigate();

  // Check login status when the component mounts
  useEffect(() => {
    fetch('http://localhost:8111/api/session', {
      method: 'GET',
      credentials: 'include', // Include cookies for session validation
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.username) {
          setIsLoggedIn(true);
          setUsername(data.username);
        } else {
          setIsLoggedIn(false);
          setUsername('');
        }
      })
      .catch((error) => console.error('Error checking session:', error));
  }, []);

  // Handle logout
  const handleLogout = () => {
    fetch('http://localhost:8111/api/logout', {
      method: 'POST',
      credentials: 'include', // Include session cookies
    })
      .then(() => {
        setIsLoggedIn(false);
        setUsername('');
      })
      .catch((error) => console.error('Error logging out:', error));
  };

  return (
    <div className="home-container">
      <h1 className="home-title">Mock Spotify</h1>
      <div className="auth-section">
        {isLoggedIn ? (
          <div className="auth-logged-in">
            <p>Welcome, {username}!</p>
            <button className="button" onClick={() => navigate(`/profile/${username}`)}>Profile</button>
            <button className="button" onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <button className="button login-button" onClick={() => navigate('/login')}>Login</button>
        )}
      </div>
      <div className="search-forms">
        <form className="search-form" onSubmit={(e) => { e.preventDefault(); navigate(`/search_song?song_title=${encodeURIComponent(songTitle.trim())}`); }}>
          <input className="input-field" type="text" value={songTitle} onChange={(e) => setSongTitle(e.target.value)} placeholder="Search for a song" />
          <button className="button" type="submit">Search</button>
        </form>
        <form className="search-form" onSubmit={(e) => { e.preventDefault(); navigate(`/search_album?album_title=${encodeURIComponent(albumTitle.trim())}`); }}>
          <input className="input-field" type="text" value={albumTitle} onChange={(e) => setAlbumTitle(e.target.value)} placeholder="Search for an album" />
          <button className="button" type="submit">Search</button>
        </form>
        <form className="search-form" onSubmit={(e) => { e.preventDefault(); navigate(`/search_artist?artist_name=${encodeURIComponent(artistName.trim())}`); }}>
          <input className="input-field" type="text" value={artistName} onChange={(e) => setArtistName(e.target.value)} placeholder="Search for an artist" />
          <button className="button" type="submit">Search</button>
        </form>
        <form className="search-form" onSubmit={(e) => { e.preventDefault(); navigate(`/search_genre?genre_name=${encodeURIComponent(genreName.trim())}`); }}>
          <input className="input-field" type="text" value={genreName} onChange={(e) => setGenreName(e.target.value)} placeholder="Search for a genre" />
          <button className="button" type="submit">Search</button>
        </form>
        <form className="search-form" onSubmit={(e) => { e.preventDefault(); navigate(`/search_playlist?playlist_title=${encodeURIComponent(playlistTitle.trim())}`); }}>
          <input className="input-field" type="text" value={playlistTitle} onChange={(e) => setPlaylistTitle(e.target.value)} placeholder="Search for a playlist" />
          <button className="button" type="submit">Search</button>
        </form>
      </div>
    </div>
  );
}

export default Home;
