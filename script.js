// get references to links
const topTracks = document.getElementById('top-tracks')
const topArtists = document.getElementById('top-artists')
const recentSongs = document.getElementById('recent-songs')
const recentArtists = document.getElementById('recent-artists')
const recommendMe = document.getElementById('recommend-me')


function sendChoice(choice) {
    // construct url
    const url = `/results?choice=${choice}`

    // make request to flask backend
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tableContainer = document.getElementById('table-container');
            tableContainer.innerHTML = '';

            const table = document.createElement('table');

            // create table header
            if (data.length > 0) {
                const headerRow = table.insertRow();
                Object.keys(data[0]).forEach(key => {
                    const headerCell = headerRow.insertCell();
                    headerCell.textContent = key;
                });
            }

            // insert data into table
            data.forEach(item => {
                const row = table.insertRow();
                Object.values(item).forEach(value => {
                    const cell = row.insertCell();
                    cell.textContent = value;
                });
            });

            tableContainer.appendChild(table);
        });
};


// event listeners
topTracks.addEventListener('click', () => sendChoice('top_tracks'));
topArtists.addEventListener('click', () => sendChoice('top_artists'));
recentSongs.addEventListener('click', () => sendChoice('recent_songs'));
recentArtists.addEventListener('click', () => sendChoice('recent_artists'));
recommendMe.addEventListener('click', () => sendChoice('recommend_me'));