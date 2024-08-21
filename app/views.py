import logging
import requests
import spotipy
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from googleapiclient.discovery import build
from newsapi import NewsApiClient
from pytrends.request import TrendReq
from spotipy.oauth2 import SpotifyClientCredentials
from .forms import UserProfileForm, UserRegistrationForm
from .models import UserProfile, Bookmark
from .search import unified_search

logger = logging.getLogger(__name__)


def set_region(request):
    region = request.GET.get('region', 'US')
    request.session['region'] = region
    logger.info(f"Region set to: {region}")
    return redirect('index')


def fetch_reddit_trends(query=None):
    url = "https://www.reddit.com/r/all/hot.json"
    headers = {'User-agent': 'Trend Finder Bot'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get('data', {}).get('children', [])
        trends = [{
            'title': trend['data']['title'],
            'description': trend['data'].get('selftext', ''),
            'url': f"https://www.reddit.com{trend['data']['permalink']}",
            'source': 'Reddit',
            'cover_picture_url': ''
        } for trend in data]
        if query:
            trends = [t for t in trends if query.lower() in t['title'].lower()]
        return trends
    except requests.RequestException as e:
        logger.error(f"Error fetching Reddit trends: {e}")
        return []


def fetch_youtube_trends(region='set_region', worldwide=False):
    youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)

    try:
        request_params = {
            'part': 'snippet,contentDetails,statistics',
            'chart': 'mostPopular',
            'regionCode': region if not worldwide else '',
            'maxResults': 50,
        }

        request = youtube.videos().list(**request_params)
        response = request.execute()
        videos = response.get('items', [])

        formatted_videos = [{
            'title': video['snippet']['title'],
            'description': video['snippet'].get('description', ''),
            'url': f"https://www.youtube.com/watch?v={video['id']}",
            'source': 'YouTube',
            'video_url': f"https://www.youtube.com/watch?v={video['id']}",
            'cover_picture_url': video['snippet']['thumbnails']['high']['url'],
        } for video in videos]

        return formatted_videos
    except Exception as e:
        logger.error(f"Error fetching YouTube trends: {e}")
        return []


def fetch_google_trends(query=None):
    pytrends = TrendReq(hl='en-US', tz=360)

    try:
        if query:
            # Build payload with the query
            pytrends.build_payload([query], cat=0, timeframe='now 1-d', gprop='')
            data = pytrends.interest_over_time()
            # Format data
            if not data.empty:
                formatted_trends = [{
                    'title': query,
                    'description': f"Interest over time: {data[query].max()}",
                    'url': f"https://trends.google.com/trends/explore?q={query}",
                    'source': 'Google Trends',
                    'cover_picture_url': ''
                }]
            else:
                formatted_trends = [{
                    'title': query,
                    'description': 'No data available',
                    'url': f"https://trends.google.com/trends/explore?q={query}",
                    'source': 'Google Trends',
                    'cover_picture_url': ''
                }]
        else:
            # Fetch trending searches
            trending_searches_df = pytrends.trending_searches(pn='united_states')
            formatted_trends = [{
                'title': row[0],
                'description': 'Trending search',
                'url': f"https://trends.google.com/trends/explore?q={row[0]}",
                'source': 'Google Trends',
                'cover_picture_url': ''
            } for row in trending_searches_df.values]

        return formatted_trends
    except Exception as e:
        logger.error(f"Error fetching Google Trends: {e}")
        return []


def fetch_spotify_trends(market="US"):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    try:
        results = sp.new_releases(limit=50, country=market)
        # Debugging: Log the markets in which the first few albums are available
        for album in results['albums']['items'][:5]:  # Check the first 5 albums
            logger.debug(f"Album '{album['name']}' available markets: {album.get('available_markets', [])}")

        formatted_trends = [{
            'title': album['name'],
            'description': f"Artist: {', '.join([artist['name'] for artist in album['artists']])}",
            'url': album['external_urls']['spotify'],
            'source': 'Spotify',
            'cover_picture_url': album['images'][0]['url'] if album['images'] else ''
        } for album in results['albums']['items'] if market in album.get('available_markets', [])]
        return formatted_trends
    except Exception as e:
        logger.error(f"Error fetching Spotify new releases: {e}")
        return []


def fetch_latest_content(language='en-US', max_results=50):
    # Define the endpoints and parameters
    movie_url = "https://api.themoviedb.org/3/movie/popular"
    tv_url = "https://api.themoviedb.org/3/tv/popular"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': language,
        'page': 1
    }

    movies = []
    tv_shows = []

    def fetch_paginated_results(url, params, target_list, max_results):
        page = 1
        while len(target_list) < max_results:
            params['page'] = page
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Response Data for {url} (Page {page}): {data}")

                results = data.get('results', [])
                if isinstance(results, list):
                    for item in results:
                        if len(target_list) >= max_results:
                            return
                        target_list.append({
                            'title': item.get('title') or item.get('name'),
                            'description': item.get('overview', ''),
                            'release_date': item.get('release_date') or item.get('first_air_date'),
                            'url': f"https://www.themoviedb.org/movie/{item.get('id')}" if 'title' in item else f"https://www.themoviedb.org/tv/{item.get('id')}",
                            'source': 'TMDb',
                            'cover_picture_url': f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}" if item.get(
                                'poster_path') else None
                        })
                else:
                    logger.warning(f"No valid 'results' list found in response data for {url} (Page {page})")

                page += 1
                if not results:
                    logger.info(f"No more pages available for {url}.")
                    break

            except requests.RequestException as e:
                logger.error(f"Error fetching data from {url} (Page {page}): {e}")
                break

    # Fetch movies
    fetch_paginated_results(movie_url, params, movies, max_results)

    # Fetch TV shows
    fetch_paginated_results(tv_url, params, tv_shows, max_results)

    logger.debug(f"Movies fetched: {movies}")
    logger.debug(f"TV Shows fetched: {tv_shows}")
    return {'movies': movies, 'tv_shows': tv_shows}


def fetch_latest_news(query=None, sources='cnn,bbc-news,Variety,Entertainment-Weekly,The-Hollywood-Reporter,espn,'
                                                'Bleacher-Report,CBS-Sports,Bloomberg,Financial-Times,TechCrunch ,Wired,'
                                                'The-Verge'):
    newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)

    try:
        top_headlines = newsapi.get_top_headlines(
            q=query if query else '',
            sources=sources,
            language='en'
        )
        articles = top_headlines.get('articles', [])
        formatted_news = [{
            'title': article['title'],
            'description': article.get('description', ''),
            'url': article['url'],
            'source': article['source']['name'],
            'cover_picture_url': article.get('urlToImage', '')
        } for article in articles[:50]]
        return formatted_news
    except Exception as e:
        logger.error(f"Error fetching latest news: {e}")
        return []


def fetch_twitter_trends():
    # Retrieve the API key from Django settings
    api_key = settings.TWITTER_API_KEY

    if not api_key:
        raise ValueError("Twitter API key is not set in Django settings")

    url = "https://twitter-api45.p.rapidapi.com/trends.php"
    querystring = {"country": "Worldwide"}  # Specify Worldwide trends

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "twitter-api45.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        trends_data = response.json()

        # Format data
        formatted_trends = [{
            'title': trend['name'],
            'description': f"Tweet volume: {trend.get('tweet_volume', 'N/A')}",
            'url': trend.get('url', '#'),
            'source': 'Twitter Trends',
            'cover_picture_url': ''
        } for trend in trends_data.get('trends', [])]

        return formatted_trends
    else:
        return []


def fetch_stock_data(symbol):
    """Fetch the latest stock data from Alpha Vantage."""
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'apikey': settings.ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Example of processing the data
    latest = data.get('Time Series (1min)', {})
    if latest:
        latest_time, latest_info = list(latest.items())[0]
        return {
            'symbol': symbol,
            'price': latest_info.get('1. open'),
            'change': float(latest_info.get('1. open')) - float(latest_info.get('4. close')),
            'change_percent': ((float(latest_info.get('1. open')) - float(latest_info.get('4. close'))) / float(
                latest_info.get('4. close'))) * 100
        }
    return {}


def fetch_crypto_data(symbol):
    """Fetch the latest crypto data from CoinMarketCap."""
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': settings.COINMARKETCAP_API_KEY
    }
    params = {
        'symbol': symbol
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Example of processing the data
    crypto = data.get('data', {}).get(symbol, {}).get('quote', {}).get('USD', {})
    return {
        'symbol': symbol,
        'price': crypto.get('price'),
        'change': crypto.get('percent_change_24h'),
        'change_percent': crypto.get('percent_change_24h')
    }


def fetch_finance_data(request):
    """Fetch and return stock and crypto data based on AJAX request."""
    if request.method == 'GET':
        stock_symbols = request.GET.get('stock_symbols', '').split(',')
        crypto_symbols = request.GET.get('crypto_symbols', '').split(',')

        latest_stocks = [fetch_stock_data(symbol.strip()) for symbol in stock_symbols if symbol.strip()]
        latest_cryptos = [fetch_crypto_data(symbol.strip()) for symbol in crypto_symbols if symbol.strip()]

        return JsonResponse({
            'latest_stocks': latest_stocks,
            'latest_cryptos': latest_cryptos
        })


def index(request):
    region = request.session.get('region', 'US')
    logger.info(f"Region retrieved from session: {region}")
    user = request.user if request.user.is_authenticated else None

    youtube_trends = fetch_youtube_trends(region=region)
    reddit_trends = fetch_reddit_trends()
    google_trends = fetch_google_trends()
    latest_content = fetch_latest_content()
    spotify_trends = fetch_spotify_trends(market=region)
    latest_news = fetch_latest_news()
    twitter_trends = fetch_twitter_trends()

    # Fetch symbols from user input if available
    stock_symbols = request.GET.get('stock_symbols', 'AAPL,GOOGL,MSFT').split(',')
    crypto_symbols = request.GET.get('crypto_symbols', 'BTC,ETH,ADA').split(',')

    # Fetch stock and crypto data
    latest_stocks = [fetch_stock_data(symbol) for symbol in stock_symbols]
    latest_cryptos = [fetch_crypto_data(symbol) for symbol in crypto_symbols]

    # Preprocess data for template
    processed_stocks = [
        {
            'symbol': stock.get('symbol'),
            'price': stock.get('price'),
            'change': stock.get('change'),
            'change_percent': stock.get('change_percent')
        }
        for stock in latest_stocks if stock
    ]

    processed_cryptos = [
        {
            'symbol': crypto.get('symbol'),
            'price': crypto.get('price'),
            'change': crypto.get('change'),
            'change_percent': crypto.get('change_percent'),
            'symbol_lower': crypto.get('symbol', '').lower()
        }
        for crypto in latest_cryptos if crypto
    ]

    logger.debug(f"Latest content: {latest_content}")

    # Combine all trends into a single list
    all_trends = []

    for trend in youtube_trends:
        trend['source'] = 'YouTube'
        all_trends.append(trend)

    for trend in reddit_trends:
        trend['source'] = 'Reddit'
        all_trends.append(trend)

    for trend in google_trends:
        trend['source'] = 'Google'
        all_trends.append(trend)

    for trend in spotify_trends:
        trend['source'] = 'Spotify'
        all_trends.append(trend)

    for trend in twitter_trends:
        trend['source'] = 'Twitter'
        all_trends.append(trend)

    return render(request, 'index.html', {
        'all_trends': all_trends,
        'youtube_trends': youtube_trends,
        'reddit_trends': reddit_trends,
        'google_trends': google_trends,
        'spotify_trends': spotify_trends,
        'latest_news': latest_news,
        'selected_region': region,
        'latest_content': latest_content,
        'twitter_trends': twitter_trends,
        'latest_stocks': processed_stocks,
        'latest_cryptos': processed_cryptos,
    })


def search_view(request):
    query = request.GET.get('query', '')

    # Perform the search
    search_results = unified_search(query)

    # Check if the request is an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'results': search_results})

    return render(request, 'search_results.html', {'results': search_results})


@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'user_profile': user_profile,
        'profile_picture': user_profile.profile_picture.url if user_profile.profile_picture else None,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'edit_profile.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('profile')  # Redirect to profile page after successful registration
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
@require_POST
def bookmark_trend(request):
    trend_title = request.POST.get('title')
    trend_url = request.POST.get('url')
    trend_source = request.POST.get('source')

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        trend_url=trend_url,
        defaults={'trend_title': trend_title, 'trend_source': trend_source}
    )

    return JsonResponse({'status': 'success', 'created': created})


@login_required
def get_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')
    data = [{'title': b.trend_title, 'url': b.trend_url, 'source': b.trend_source} for b in bookmarks]
    return JsonResponse({'bookmarks': data})
