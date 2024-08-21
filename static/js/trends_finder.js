$(document).ready(function() {
$('#finance-form').submit(function(event) {
        event.preventDefault();  // Prevent default form submission

        $.ajax({
            url: '{% url "fetch_finance_data" %}',
            type: 'GET',
            data: $(this).serialize(),
            success: function(data) {
                console.log('Received data:', data);  // Debug: Log the received data

                // Clear previous data
                $('#stock-data').html('<h4>Latest Stock Data</h4>');
                $('#crypto-data').html('<h4>Latest Crypto Data</h4>');

                // Insert stock data
                if (data.latest_stocks && data.latest_stocks.length > 0) {
                    data.latest_stocks.forEach(function(stock) {
                        console.log('Stock:', stock);  // Debug: Log each stock object
                        $('#stock-data').append(`
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">${stock.symbol || 'N/A'}</h5>
                                    <p class="card-text">Price: ${stock.price || 'N/A'}</p>
                                    <p class="card-text">Change: ${stock.change || 'N/A'} (${stock.change_percent || 'N/A'}%)</p>
                                    <a href="https://www.marketwatch.com/investing/stock/${stock.symbol}" class="btn btn-primary" target="_blank">View Details</a>
                                </div>
                            </div>
                        `);
                    });
                } else {
                    $('#stock-data').append('<p>No stock data available.</p>');
                }

                // Insert crypto data
                if (data.latest_cryptos && data.latest_cryptos.length > 0) {
                    data.latest_cryptos.forEach(function(crypto) {
                        console.log('Crypto:', crypto);  // Debug: Log each crypto object
                        $('#crypto-data').append(`
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h5 class="card-title">${crypto.symbol || 'N/A'}</h5>
                                    <p class="card-text">Price: $${crypto.price || 'N/A'}</p>
                                    <p class="card-text">Change: ${crypto.change || 'N/A'} (${crypto.change_percent || 'N/A'}%)</p>
                                    <a href="https://coinmarketcap.com/currencies/${crypto.symbol ? crypto.symbol.toLowerCase() : ''}" class="btn btn-primary" target="_blank">View Details</a>
                                </div>
                            </div>
                        `);
                    });
                } else {
                    $('#crypto-data').append('<p>No crypto data available.</p>');
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error:', status, error);
                console.log('Response:', xhr.responseText);  // Debug: Log the full response
                $('#stock-data').html('<p>Error fetching stock data. Please try again.</p>');
                $('#crypto-data').html('<p>Error fetching crypto data. Please try again.</p>');
            }
        });
    });
});

function performSearch() {
        const query = document.getElementById('searchInput').value;
        const resultsContainer = document.getElementById('resultsContainer');

        // Clear previous results
        resultsContainer.innerHTML = '';

        // Check if query is not empty
        if (query.trim() === '') {
            resultsContainer.innerHTML = '<p>Please enter a search term.</p>';
            return;
        }

        // Perform AJAX request to your Django view
        fetch(`/search/?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                // Display results
                if (data.results && data.results.length > 0) {
                    data.results.forEach(result => {
                        const resultElement = document.createElement('div');
                        resultElement.classList.add('result-item');
                        resultElement.innerHTML = `
                            <h5>${result.title}</h5>
                            <p>${result.description}</p>
                            <a href="${result.url}" target="_blank">Read more</a>
                        `;
                        resultsContainer.appendChild(resultElement);
                    });
                } else {
                    resultsContainer.innerHTML = '<p>No results found.</p>';
                }
            })
            .catch(error => {
                console.error('Error fetching search results:', error);
                resultsContainer.innerHTML = '<p>Error fetching results.</p>';
            });
    }

function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = ''; // Clear previous results

    for (const [source, items] of Object.entries(data)) {
        if (items.length > 0) {
            const section = document.createElement('div');
            section.className = 'results-section';
            section.innerHTML = `<h4>${source}</h4>`;

            items.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'result-item';
                itemDiv.innerHTML = `
                    <h5>${item.title}</h5>
                    <p>${item.description}</p>
                    <a href="${item.url}" target="_blank">Read more</a>
                    ${item.cover_picture_url ? `<img src="${item.cover_picture_url}" alt="${item.title}" />` : ''}
                `;
                section.appendChild(itemDiv);
            });

            resultsContainer.appendChild(section);
        }
    }
}

function setRegion(regionCode) {
        fetch(`/set_region?region=${encodeURIComponent(regionCode)}`)
            .then(response => {
                if (response.ok) {
                    console.log('Region set to:', regionCode);
                    // Optionally refresh the page or update the UI
                    window.location.reload();
                } else {
                    console.error('Failed to set region.');
                }
            })
            .catch(error => {
                console.error('Error setting region:', error);
            });
    }

function bookmarkItem(itemTitle, itemUrl, itemSource) {
    // Optional: Use localStorage for client-side bookmark management
    let bookmarks = JSON.parse(localStorage.getItem('bookmarks')) || [];
    const newBookmark = { title: itemTitle, url: itemUrl, source: itemSource };

    const existingBookmark = bookmarks.find(bookmark => bookmark.url === itemUrl);
    if (!existingBookmark) {
        bookmarks.push(newBookmark);
        localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
        alert("Bookmark added successfully!");
    } else {
        alert("This bookmark already exists!");
    }

    // Send to server-side for persistent storage
    fetch('/bookmark_trend/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: new URLSearchParams({
            'title': itemTitle,
            'url': itemUrl,
            'source': itemSource
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Item bookmarked:', itemTitle);
        } else {
            console.error('Failed to bookmark item.');
        }
    })
    .catch(error => {
        console.error('Error bookmarking item:', error);
    });
}

function shareItem(itemTitle, itemUrl) {
    // Check if the Web Share API is available
    if (navigator.share) {
        navigator.share({
            title: itemTitle,
            url: itemUrl
        })
        .then(() => console.log('Successfully shared via Web Share API'))
        .catch(error => console.error('Error sharing item:', error));
    } else {
        // Fallback to sharing through social media platforms
        console.log('Web Share API not supported. Sharing through social media.');

        // URL encode the title and URL
        const encodedTitle = encodeURIComponent(itemTitle);
        const encodedUrl = encodeURIComponent(itemUrl);

        // Define social media sharing URLs
        const twitterShareUrl = `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}`;
        const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`;
        const linkedinShareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${encodedUrl}&title=${encodedTitle}`;
        const whatsappShareUrl = `https://api.whatsapp.com/send?text=${encodedTitle}%20${encodedUrl}`;

        // Create a custom share dialog
        let shareOptions = `
            <div class="share-options">
                <a href="${twitterShareUrl}" target="_blank" class="btn btn-outline-primary mb-2"><i class="fab fa-twitter"></i> Share on Twitter</a>
                <a href="${facebookShareUrl}" target="_blank" class="btn btn-outline-primary mb-2"><i class="fab fa-facebook"></i> Share on Facebook</a>
                <a href="${linkedinShareUrl}" target="_blank" class="btn btn-outline-primary mb-2"><i class="fab fa-linkedin"></i> Share on LinkedIn</a>
                <a href="${whatsappShareUrl}" target="_blank" class="btn btn-outline-primary mb-2"><i class="fab fa-whatsapp"></i> Share on WhatsApp</a>
                <button onclick="copyToClipboard('${itemUrl}')" class="btn btn-outline-secondary mb-2"><i class="fas fa-copy"></i> Copy Link</button>
            </div>
        `;

        // Insert the share options into a modal or a specific container
        document.getElementById('shareContainer').innerHTML = shareOptions;
        $('#shareModal').modal('show');
    }
}

function copyToClipboard(text) {
    const tempInput = document.createElement('input');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    alert("Link copied to clipboard!");
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



