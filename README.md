# Mock Spotify

**Currently, I'm building a Docker container to run the PostgreSQL database so others can easily download and run my code. Initially, the database was hosted using Google Cloud Platform as part of a class project, and I'm now transitioning to Docker to make it easier for others to run the project locally. Additionally, I'm reintegrating JavaScript and CSS.

## Overview

In this project, I built a database application that mimics Spotify's basic features. This experience taught me a lot about database design, SQL, and building web applications with Flask, pushing me beyond what I expected at the start. Here's what I learned, the skills I gained, and the challenges I solved:

## Lessons Learned

### Database Schema Design: 

I learned the ins and outs of designing a robust database schema that can represent real-world relationships between multiple entities. Figuring out the optimal relationships between users, playlists, songs, artists, and albums was more challenging than I anticipated. I now understand the importance of planning these relationships early to avoid issues with querying and functionality later on.

### Complexity of Relationships: 

One of the big takeaways was realizing how crucial it is to correctly handle Many-to-Many relationships, like Users and Playlists or Artists and Genres. The way I structured these relationships had a direct impact on how easy (or difficult) it was to work with the data during development.

### Enhancing Functionality Beyond Initial Design: 

I also learned the importance of adapting a project as it progresses. While my initial design was solid, I had to introduce new features like user authentication and recommendation algorithms to enhance the user experience. This process taught me a lot about iterating and expanding a project based on both user needs and technical feasibility.

### SQL Full-Text Search: 

Adding full-text search to artist biographies showed me how to enhance database functionality to improve user experience. This feature was valuable for filtering artists by keywords, and I learned how to implement it to make data more searchable.

### Web Application Integration: 

I learned how to bridge the gap between the backend (database) and the frontend (Flask application). Handling database connections, executing SQL queries, and displaying data dynamically in the web interface gave me insight into building full-stack applications.

## Skills Acquired

### Database Design and Normalization: 

I got comfortable designing a normalized database schema, organizing entities, and setting up appropriate relationships while maintaining data integrity.

### Complex SQL Queries: 

I gained experience writing complex SQL queries that join multiple tables, handle indirect relationships, and filter data as needed. Implementing features like song recommendations and genre navigation pushed me to think through the best query logic to make the data work for me.

### Web Application Development with Flask: 

This project was a crash course in building a web application from scratch using Flask. I set up routes, implemented a user login system, and integrated SQL queries to create a cohesive user experience.

### SQLAlchemy and ORM: 

Working with SQLAlchemy taught me how to integrate SQL with Python, handle database connections, and commit changes effectively, which is essential for building dynamic applications.

### Session Management and Authentication: 

I implemented user authentication with Flask sessions, giving users the ability to log in and view personalized profiles. This was new to me, and I now understand how crucial session management is for secure and interactive web applications.

### Query Optimization and Recommendations: 

I built a recommendation engine that suggested songs, artists, and playlists based on the artists that users followed. Implementing this taught me the basics of recommendation logic, even if the final solution was more straightforward than initially planned.

## Problems Solved

### Indirect Relationships: 

One of the trickiest parts was creating indirect relationships where no direct link existed. For example, recommending songs by artists followed by a user, despite the schema lacking a direct Song-Artist relationship, required a workaround using multiple joins.

### Schema Expansion with New Features: 

I expanded the original schema by adding features like full-text search, array attributes, and composite types. These changes helped make the application more flexible and realistic.

### Handling Many-to-Many Relationships: 

Managing Many-to-Many relationships (like User-Playlist and Artist-Genre) required creating intermediary tables and maintaining data integrity through SQL constraints. This was a key problem that I solved by understanding how to properly link tables.

### User-Specific Data Presentation: 

I figured out how to effectively display personalized information to logged-in users, including the artists they follow, songs they listened to, and recommendations. This added complexity to the user experience, but also made it much more engaging.

### Recommendation Algorithm: 

Implementing the recommendation engine involved solving the problem of providing useful suggestions without overwhelming the user. Though simplified, it used artists that users followed to suggest relevant songs, artists, and playlists, which involved some creative SQL query design.

### Improving Search Functionality: 

To enhance search capabilities, I implemented full-text search on artist biographies, which helped me understand how to make data more accessible and user-friendly.
