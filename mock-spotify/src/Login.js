import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
  
    console.log("Submitting login request:", { username, password }); // Debugging log
  
    fetch('http://localhost:8111/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // Important for session handling
      body: JSON.stringify({ username, password }),
    })
      .then((response) => {
        console.log("Response status:", response.status); // Debugging log
        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.message || "Login failed");
          });
        }
        return response.json();
      })
      .then((data) => {
        console.log("Login successful:", data); // Debugging log
        sessionStorage.setItem('username', data.username); // Store username
        setError('');
        navigate(`/`);
      })
      .catch((err) => {
        console.error("Login failed:", err.message); // Debugging log
        setError(err.message);
      });
  };
  
  
  

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        /><br />

        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        /><br />

        <input type="submit" value="Login" />
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <p><a href="/">Go back to the home page</a></p>
    </div>
  );
}

export default Login;
