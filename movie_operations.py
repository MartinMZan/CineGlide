from ncoreparser import Client, SearchParamWhere, SearchParamType, ParamSort, ParamSeq
from ncoreparser.torrent import Torrent
import requests
import auth

NCORE_USERNAME = auth.NCORE_USERNAME
NCORE_PASSWORD = auth.NCORE_PASSWORD

URL = "https://api.themoviedb.org/3/search/movie"
header = {
    "accept": "application/json",
    "Authorization": auth.TMDB_API_KEY,
}


def _parse_movie_title(torrent):
    title_split = torrent["title"].split(".")
    if title_split[0] == torrent["title"]:  # If not movie.name.release_year.etc format.
        return None

    for idx, word in enumerate(title_split):
        if idx == 0:  # The title of a movie can be a number.
            continue
        try:
            release_year = int(word)

            return " ".join(title_split[:idx]), release_year
        except ValueError:
            continue

    return None, None


def _get_tmdb_details(title, release_year):
    body = {
        "query": title,
        "year": release_year,
    }
    response = requests.get(URL, headers=header, params=body)
    response.raise_for_status()
    data = response.json()["results"][0]
    overview = data["overview"]
    poster_path = "https://image.tmdb.org/t/p/original" + data["poster_path"]
    return overview, poster_path


def get_movie_toplist(length: int = 10,
                      t_type: SearchParamType = SearchParamType.HD_HUN):
    # If there is a lot of movies which cannot be parsed, then we may have less items in the toplist than lenght.
    client = Client()
    client.login(NCORE_USERNAME, NCORE_PASSWORD)
    torrents = client.search(pattern="", type=t_type, number=int(length * 1.5),
                             sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)
    client.logout()

    movies = []
    for torrent in torrents:
        title, release_year = _parse_movie_title(torrent)
        if title in movies:  # Same movie appears multiple times.
            continue
        if title is None:  # Cannot be parsed.
            continue
        overview, poster_path = _get_tmdb_details(title, release_year)
        movies.append({"title": title, "release_year": release_year, "overview": overview,
                       "poster_path": poster_path})

    return movies[:length]


def download_movie(title: str,
                   release_year: int,
                   resolution: str = "1080p",
                   t_type: SearchParamType = SearchParamType.HD_HUN):
    client = Client()
    client.login(NCORE_USERNAME, NCORE_PASSWORD)
    torrent = client.search(pattern=f"{title} {release_year} {resolution}", type=t_type, number=1,
                            sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]
    client.download(torrent, "tmp")
    client.logout()


# TODO: Decide what to do with this class.
class Movie:
    def __init__(self,
                 title: str,
                 release_year: int,
                 overview: str,
                 poster_path: str,
                 torrent: Torrent):
        self.title = title
        self.release_year = release_year
        self.overview = overview
        self.poster_path = poster_path
