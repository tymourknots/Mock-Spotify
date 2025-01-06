document.addEventListener("DOMContentLoaded", () => {
    const albumId = window.location.pathname.split("/").pop(); // Extract album ID from URL

    // Fetch album details and songs
    fetch(`/api/album/${albumId}`)
        .then(response => response.json())
        .then(data => {
            const { album, songs } = data;

            // Populate album details
            document.getElementById("album-title").innerText = `Album Details: ${album.title}`;
            document.getElementById("album-info").innerHTML = `
                <p>Title: ${album.title}</p>
                <p>Artist: <a href="/artist/${album.artistId}">${album.artistName}</a></p>
                <p>Release Year: ${album.releaseYear}</p>
                <p>Genre: <a href="/genre/${album.genreId}">${album.genreName}</a></p>
            `;

            // Populate song list
            const songList = document.getElementById("song-list");
            if (songs.length > 0) {
                songs.forEach(song => {
                    const songElement = document.createElement("div");
                    songElement.innerHTML = `
                        <a href="/search_song?song_id=${song.id}">${song.title}</a> - Duration: ${song.duration} seconds
                    `;
                    songList.appendChild(songElement);
                });
            } else {
                songList.innerHTML = "<p>No songs found in this album.</p>";
            }
        })
        .catch(error => console.error("Error fetching album details:", error));
});
