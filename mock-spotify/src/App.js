import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import SearchSong from './SearchSong';
import SearchAlbum from './SearchAlbum';
import SearchArtist from './SearchArtist';
import SearchGenre from './SearchGenre';
import SearchPlaylist from './SearchPlaylist';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search_song" element={<SearchSong />} />
        <Route path="/search_album" element={<SearchAlbum />} />
        <Route path="/search_artist" element={<SearchArtist />} />
        <Route path="/search_genre" element={<SearchGenre />} />
        <Route path="/search_playlist" element={<SearchPlaylist />} />
      </Routes>
    </Router>
  );
}

export default App;
