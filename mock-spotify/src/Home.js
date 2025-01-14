import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [songTitle, setSongTitle] = useState('');
  const [albumTitle, setAlbumTitle] = useState('');
  const [artistName, setArtistName] = useState('');
  const [genreName, setGenreName] = useState('');
  const [playlistTitle, setPlaylistTitle] = useState('');
  const navigate = useNavigate();

  const handleSongSearch = (e) => {
    e.preventDefault();
    if (!songTitle.trim()) return;
    navigate(`/search_song?song_title=${encodeURIComponent(songTitle.trim())}`);
  };

  const handleAlbumSearch = (e) => {
    e.preventDefault();
    if (!albumTitle.trim()) return;
    navigate(`/search_album?album_title=${encodeURIComponent(albumTitle.trim())}`);
  };

  const handleArtistSearch = (e) => {
    e.preventDefault();
    if (!artistName.trim()) return;
    navigate(`/search_artist?artist_name=${encodeURIComponent(artistName.trim())}`);
  };

  const handleGenreSearch = (e) => {
    e.preventDefault();
    if (!genreName.trim()) return;
    navigate(`/search_genre?genre_name=${encodeURIComponent(genreName.trim())}`);
  };

  const handlePlaylistSearch = (e) => {
    e.preventDefault();
    if (!playlistTitle.trim()) return;
    navigate(`/search_playlist?playlist_title=${encodeURIComponent(playlistTitle.trim())}`);
  };

  return (
    <div>
      <h1>Mock Spotify</h1>
      <form onSubmit={handleSongSearch}>
        <p>
          Search for a song:
          <input
            type="text"
            value={songTitle}
            onChange={(e) => setSongTitle(e.target.value)}
            placeholder="Search for a song"
          />
          <button type="submit">Search</button>
        </p>
      </form>
      <form onSubmit={handleAlbumSearch}>
        <p>
          Search for an album:
          <input
            type="text"
            value={albumTitle}
            onChange={(e) => setAlbumTitle(e.target.value)}
            placeholder="Search for an album"
          />
          <button type="submit">Search</button>
        </p>
      </form>
      <form onSubmit={handleArtistSearch}>
        <p>
          Search for an artist:
          <input
            type="text"
            value={artistName}
            onChange={(e) => setArtistName(e.target.value)}
            placeholder="Search for an artist"
          />
          <button type="submit">Search</button>
        </p>
      </form>
      <form onSubmit={handleGenreSearch}>
        <p>
          Search for a genre:
          <input
            type="text"
            value={genreName}
            onChange={(e) => setGenreName(e.target.value)}
            placeholder="Search for a genre"
          />
          <button type="submit">Search</button>
        </p>
      </form>
      <form onSubmit={handlePlaylistSearch}>
        <p>
          Search for a playlist:
          <input
            type="text"
            value={playlistTitle}
            onChange={(e) => setPlaylistTitle(e.target.value)}
            placeholder="Search for a playlist"
          />
          <button type="submit">Search</button>
        </p>
      </form>
    </div>
  );
}

export default Home;
