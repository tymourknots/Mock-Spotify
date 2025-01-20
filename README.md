# Mock Spotify

## Overview

This project is a full-stack web application that mimics Spotify's basic features. Initially built with Flask for the backend and vanilla HTML for the frontend, the application has been upgraded to use React for the frontend, providing a more dynamic and modern user experience. This project taught me valuable lessons about database design, full-stack development, and bridging the gap between backend logic and interactive UIs.

## Video Demonstration

<div align="center">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/Nk71oJdapdo" 
          title="Mock Spotify Video Demonstration" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
          allowfullscreen>
  </iframe>
</div>

---

## Lessons Learned

### React Integration
- **Component-Based Design**: I learned how to structure a frontend using React components, allowing for modular, reusable, and maintainable code. 
- **State Management**: Handling state and props in React, especially when dealing with asynchronous data fetching, taught me how to manage and render dynamic data effectively.
- **React Router**: Implementing React Router allowed seamless navigation between different parts of the application, such as user profiles, playlists, and search results.

### Bridging Frontend and Backend
- **RESTful API Design**: Converting the Flask routes into a REST API taught me how to structure and consume APIs effectively. This shift made the application backend-agnostic and opened the door for future scalability.
- **CORS and Security**: Setting up CORS to handle communication between the React frontend and Flask backend helped me understand the intricacies of cross-origin resource sharing and securing API endpoints.

### Enhancing Functionality Beyond Initial Design
- **Dynamic Recommendations**: React's reactivity allowed for a better user experience when displaying song, artist, and playlist recommendations. Integrating these features in React made them more interactive and visually appealing.
- **UI/UX Improvements**: Moving from static HTML to a React-based frontend allowed me to implement a responsive, user-friendly design that better mimics the look and feel of Spotify.

## Skills Acquired

### Frontend Development with React
- Built dynamic components for profiles, playlists, recommendations, and search results.
- Utilized React Router for smooth client-side routing.
- Enhanced user interactivity with stateful components and hooks.

### RESTful API Integration
- Designed a backend API with Flask to serve data to the React frontend.
- Handled asynchronous data fetching with `fetch()` and effectively managed loading and error states.

### Database Design and Optimization
- Designed a normalized database schema to manage users, playlists, songs, artists, and genres.
- Implemented efficient SQL queries to fetch and filter data for recommendations.

### Authentication and Session Management
- Managed user authentication with Flask sessions, ensuring secure access to personalized data.
- Preserved login states across sessions using cookies and integrated user-specific data into the React frontend.

### Query Optimization and Recommendations
- Enhanced recommendations by leveraging user data, such as followed artists and listened-to songs, to suggest playlists, songs, and other artists dynamically.

### Deployment-Ready Features
- Modularized the backend and frontend to simplify future deployment and scaling.
- Used CORS to handle secure communication between the frontend and backend.

## Features

### Core Functionality
- **User Profiles**: Users can log in, view their profile, and see their playlists, followed artists, and songs they’ve listened to.
- **Search**: Users can search for songs, albums, artists, genres, and playlists using keyword-based filtering.
- **Recommendations**: Personalized song, artist, and playlist recommendations are generated based on user activity, such as followed artists and listened-to songs.

### Frontend Enhancements
- **Dynamic UI**: A modern React-based UI with reusable components and responsive design.
- **Navigation**: Smooth navigation using React Router.
- **Improved Search**: Real-time feedback and user-friendly navigation links to related content.

### Backend Enhancements
- **REST API**: A well-structured API for handling user profiles, recommendations, and search functionality.
- **Authentication**: A secure login system with Flask sessions.

## Challenges Solved

### Indirect Relationships
Managing indirect relationships, such as recommending songs by artists followed by a user, required creative SQL queries to handle the lack of direct Song-Artist relationships.

### Schema Expansion with New Features
Expanding the original schema to include features like recommendations and full-text search provided valuable lessons in balancing complexity and performance.

### Many-to-Many Relationships
Properly handling Many-to-Many relationships, such as User-Playlist and Artist-Genre, ensured data integrity and efficient querying.

### Optimized Recommendations
Building a recommendation engine to provide relevant suggestions without overwhelming the user involved solving challenges related to filtering and ranking.

