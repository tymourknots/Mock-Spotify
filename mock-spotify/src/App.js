import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import SearchSong from './SearchSong';
import SearchAlbum from './SearchAlbum';
import SearchArtist from './SearchArtist';
import SearchGenre from './SearchGenre';
import SearchPlaylist from './SearchPlaylist';
import AlbumDetails from './AlbumDetails';
import ArtistDetails from './ArtistDetails';
import GenreDetails from './GenreDetails'; 
import PlaylistDetails from './PlaylistDetails';

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
        <Route path="/album/:albumId" element={<AlbumDetails />} />
        <Route path="/artist/:artistId" element={<ArtistDetails />} />
        <Route path="/genre/:genreId" element={<GenreDetails />} />
        <Route path="/playlist/:playlistId" element={<PlaylistDetails />} />
      </Routes>
    </Router>
  );
}

export default App;

