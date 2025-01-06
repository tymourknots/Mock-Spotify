import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import SearchSong from './SearchSong';
import SearchAlbum from './SearchAlbum';

function App() {
  const [searchQuery, setSearchQuery] = useState(''); // General query for the home page (optional)

  return (
    <Router>
      <Routes>
        {/* Home page where users can search */}
        <Route path="/" element={<Home setSearchQuery={setSearchQuery} />} />

        {/* Song search results page */}
        <Route path="/search_song" element={<SearchSong />} />

        {/* Album search results page */}
        <Route path="/search_album" element={<SearchAlbum />} />
      </Routes>
    </Router>
  );
}

export default App;
