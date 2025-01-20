from collections.abc import Mapping
from typing import Literal

API_BASE = 'https://api.themoviedb.org/3'
CDN_BASE = 'https://image.tmdb.org/t/p/original'
TMDB_ICON = 'https://i.imgur.com/sSE7Usn.png'


MV_IDS = Literal[28, 12, 16, 35, 80, 99, 18, 10751, 14, 36, 27, 10402, 9648, 10749, 878, 10770, 53, 10752, 37]
TV_IDS = Literal[10759, 16, 35, 80, 99, 18, 10751, 10762, 9648, 10763, 10764, 10765, 10766, 10767, 10768, 37]


MOVIE_GENRES: Mapping[int, str] = {
    12: 'Adventure',
    14: 'Fantasy',
    18: 'Drama',
    16: 'Animation',
    27: 'Horror',
    28: 'Action',
    35: 'Comedy',
    36: 'History',
    37: 'Western',
    53: 'Thriller',
    80: 'Crime',
    99: 'Documentary',
    878: 'Sci-fi',
    9648: 'Mystery',
    10402: 'Music',
    10749: 'Romance',
    10751: 'Family',
    10752: 'War',
    10770: 'TV Movie',
}


TV_GENRES: Mapping[int, str] = {
    16: 'Animation',
    18: 'Drama',
    35: 'Comedy',
    37: 'Western',
    80: 'Crime',
    99: 'Documentary',
    9648: 'Mystery',
    10751: 'Family',
    10759: 'Action/Adventure',
    10762: 'Kids',
    10763: 'News',
    10764: 'Reality',
    10765: 'Sci-fi/Fantasy',
    10766: 'Soap',
    10767: 'Talk',
    10768: 'War/Politics',
}


# https://imdbapi.dev/playground
IMDBAPI_GQL_QUERY = """
query($IMDB_ID: ID!) {
  title(id: $IMDB_ID) {
    id
    type
    primary_title
    start_year
    plot
    genres
    rating{
      aggregate_rating
      votes_count
    }
  }
}
"""
