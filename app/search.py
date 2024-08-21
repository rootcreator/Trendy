import logging
from typing import Dict, List, Union
import requests
import spotipy
from django.conf import settings
from googleapiclient.discovery import build
from newsapi import NewsApiClient
from pytrends.request import TrendReq
from spotipy import SpotifyClientCredentials


logger = logging.getLogger(__name__)


def query_google_trends(query):
    pytrends = TrendReq(hl='en-US', tz=360)

    try:
        pytrends.build_payload([query], cat=0, timeframe='now 1-d')
        data = pytrends.interest_over_time()

        if not data.empty:
            trend_data = {
                'title': query,
                'interest_max': data[query].max(),
                'interest_mean': data[query].mean(),
                'interest_min': data[query].min(),
                'url': f"https://trends.google.com/trends/explore?q={query}",
                'source': 'Google Trends',
                'cover_picture_url': ''
            }
        else:
            trend_data = {
                'title': query,
                'description': 'No data available',
                'url': f"https://trends.google.com/trends/explore?q={query}",
                'source': 'Google Trends',
                'cover_picture_url': ''
            }

        return trend_data
    except Exception as e:
        logger.error(f"Error querying Google Trends: {e}")
        return {}


def search_reddit(query, sort='relevance', limit=10):
    url = "https://www.reddit.com/r/all/search.json"
    headers = {'User-agent': 'Trend Finder Bot'}
    params = {
        'q': query,
        'sort': sort,
        'limit': limit
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get('data', {}).get('children', [])
        results = [{
            'title': item['data']['title'],
            'description': item['data'].get('selftext', ''),
            'url': f"https://www.reddit.com{item['data']['permalink']}",
            'source': 'Reddit',
            'cover_picture_url': item['data'].get('thumbnail', '')
        } for item in data]
        return results
    except requests.RequestException as e:
        logger.error(f"Error searching Reddit: {e}")
        return []


def search_youtube(query, max_results=10, region='US', order='relevance'):
    youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)

    try:
        request = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            regionCode=region,
            maxResults=max_results,
            order=order
        )
        response = request.execute()
        items = response.get('items', [])

        results = [{
            'title': item['snippet']['title'],
            'description': item['snippet'].get('description', ''),
            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            'source': 'YouTube',
            'cover_picture_url': item['snippet']['thumbnails']['high']['url'],
        } for item in items]

        return results
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}")
        return []


def search_spotify(query, search_type='track', limit=10):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    try:
        results = sp.search(q=query, type=search_type, limit=limit)

        def format_item(item):
            if search_type == 'track':
                return {
                    'title': item['name'],
                    'description': f"Artist: {', '.join([artist['name'] for artist in item['artists']])}",
                    'url': item['external_urls']['spotify'],
                    'source': 'Spotify',
                    'cover_picture_url': item['album']['images'][0]['url'] if item['album']['images'] else ''
                }
            elif search_type == 'album':
                return {
                    'title': item['name'],
                    'description': f"Artist: {', '.join([artist['name'] for artist in item['artists']])}",
                    'url': item['external_urls']['spotify'],
                    'source': 'Spotify',
                    'cover_picture_url': item['images'][0]['url'] if item['images'] else ''
                }
            elif search_type == 'artist':
                return {
                    'title': item['name'],
                    'description': 'Artist',
                    'url': item['external_urls']['spotify'],
                    'source': 'Spotify',
                    'cover_picture_url': item['images'][0]['url'] if item['images'] else ''
                }
            elif search_type == 'playlist':
                return {
                    'title': item['name'],
                    'description': f"Owner: {item['owner']['display_name']}",
                    'url': item['external_urls']['spotify'],
                    'source': 'Spotify',
                    'cover_picture_url': item['images'][0]['url'] if item['images'] else ''
                }

        formatted_results = [
            format_item(item) for item in results[f'{search_type}s']['items']
        ]
        return formatted_results

    except Exception as e:
        logger.error(f"Error searching Spotify: {e}")
        return []


def search_news(query, language='en'):
    newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)

    try:
        search_results = newsapi.get_everything(
            q=query,
            language=language,
            sort_by='relevancy'
        )
        articles = search_results.get('articles', [])
        formatted_news = [{
            'title': article['title'],
            'description': article.get('description', ''),
            'url': article['url'],
            'source': article['source']['name'],
            'cover_picture_url': article.get('urlToImage', '')
        } for article in articles]
        return formatted_news
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        return []


def unified_search(query: str, limit=10) -> Dict[str, List[Dict[str, Union[str, List[str]]]]]:
    results = {
        'Google Trends': [],
        'Reddit': [],
        'YouTube': [],
        'Spotify': [],
        'News': []
    }

    # Query Google Trends
    google_trends_data = query_google_trends(query)
    if google_trends_data:
        results['Google Trends'].append(google_trends_data)

    # Search Reddit
    reddit_results = search_reddit(query, limit=limit)
    if reddit_results:
        results['Reddit'] = reddit_results

    # Search YouTube
    youtube_results = search_youtube(query, max_results=limit)
    if youtube_results:
        results['YouTube'] = youtube_results

    # Search Spotify
    spotify_results = search_spotify(query, limit=limit)
    if spotify_results:
        results['Spotify'] = spotify_results

    # Search News
    news_results = search_news(query)
    if news_results:
        results['News'] = news_results

    return results
