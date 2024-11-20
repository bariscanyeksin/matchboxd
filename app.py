import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
from streamlit.components.v1 import html

st.set_page_config(
    page_title="Matchboxd",
    page_icon="🎬"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="cache"], [class*="st-"], h1, h2, h3  {
        font-family: 'Poppins', sans-serif;
    }

    .stHeading {
        margin-bottom: 5px;
        padding-bottom: 0px;
    }

    .stButton {
        text-align: center;
    }
    
    
    h1 span[data-testid="stHeaderActionElements"], h2 span[data-testid="stHeaderActionElements"], h3 span[data-testid="stHeaderActionElements"], h4 span[data-testid="stHeaderActionElements"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Matchboxd.")
st.write("Compare the movies watched by two Letterboxd users.")

with st.expander("How to find your username?"):
    st.markdown(
        """
        <div style="margin-bottom: 15px;">
            <h4>On PC:</h4>
            <p>Your Letterboxd username is typically the name that appears in the URL when you visit your profile. For example:</p>
            <p style="color: #3498db; font-size:15px;">https://letterboxd.com/username/</p>
        </div>
        <div style="margin-bottom: 15px;">
            <h4>On Phone:</h4>
            <p>Open the Letterboxd app, go to your profile, tap the <strong>cogwheel icon</strong> (settings) at the top of your profile page, and you'll see your username at the top of this page.</p>
        </div>
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://i.ibb.co/xSdJ557/50ce062c-70c3-4c62-ad9d-0fc901f94ee0.jpg" 
            alt="Example of finding your username on the Letterboxd app"
            class="mobile_img">
            <p style="font-size: 11px; margin-top: 10px; color: #7b7b7b;">
                Example of finding your username on the Letterboxd app
            </p>
        </div>
        <style>
            .mobile_img {
                width: 50%;
                height: auto;
            }
            @media (max-width: 768px) {
                .mobile_img {
                    width: 80%;
                    height: auto;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

user1 = st.text_input("User 1", placeholder="Enter the first Letterboxd username")
user2 = st.text_input("User 2", placeholder="Enter the second Letterboxd username")

def get_profile_image(user):
    image_url = f"https://letterboxd.com/{user}/"
    page = requests.get(image_url)
    bs4 = BeautifulSoup(page.text, "html.parser")
    prof_img_ = bs4.find("span", {"class": "avatar -a110 -large"})
    if prof_img_:
        return prof_img_.find("img").attrs["src"]
    else:
        return None

def create_poster_url(movie_slug):
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': f'https://letterboxd.com/{movie_slug}',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }

    response = requests.get(f'https://letterboxd.com/{movie_slug}', headers=headers)

    if response.status_code != 200:
            return ""

    soup = BeautifulSoup(response.text, "html.parser")

    script_tag = soup.find('script', type='application/ld+json')

    if script_tag:
        json_str = script_tag.string.strip()
        
        if json_str.startswith("/* <![CDATA[ */") and json_str.endswith("/* ]]> */"):
            json_str = json_str[len("/* <![CDATA[ */"): -len("/* ]]> */")].strip()
        
        try:
            json_data = json.loads(json_str)
            image_url = json_data.get('image', None)

            if image_url:
                return image_url
            else:
                print("Image URL not found.")
                return ""
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return ""
    else:
        print("JSON-LD script tag not found.")
        return ""

def get_all_movies(username):
    """
    Fetches all movies watched by a Letterboxd user, including movie name, rating, URL, and poster URL.
    """
    base_url = f"https://letterboxd.com/{username}/films/by/entry-rating/page/"
    movies_with_details = {}
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=0, i",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    }

    url = f"{base_url}1/"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    pagination = soup.find("div", {"class": "paginate-pages"})
    if pagination:
        total_pages = max(
            [int(a.text) for a in pagination.find_all("a") if a.text.isdigit()] + [1]
        )
    else:
        total_pages = 1

    for page in range(1, total_pages + 1):
        url = f"{base_url}{page}/"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        movie_list = soup.find(
            "ul", {"class": "poster-list -p70 -grid film-list clear"}
        )

        if not movie_list:
            break

        for li in movie_list.find_all("li"):
            div = li.find("div", {"data-target-link": True})
            if div:
                movie_title = div.find("img").get("alt")

                movie_url = div["data-target-link"]

                rating_span = li.find("span", {"class": "rating"})
                if rating_span:
                    rating_text = rating_span.text.strip()
                    rating = rating_text.count("★") + 0.5 * rating_text.count("½")
                else:
                    rating = 0

                movies_with_details[movie_title] = {
                    "rating": rating,
                    "movie_url": movie_url,
                }

    return movies_with_details

def calculate_similarity_with_weighted_ratings(movies1, ratings1, movies2, ratings2, threshold=0.5):
    """
    Calculate similarity between two users based on:
    1. The ratio of common movies to total movies rated by both users.
    2. The weighted similarity of ratings for common movies.
    
    Parameters:
    - movies1: List of movies rated by user 1.
    - ratings1: List of ratings given by user 1.
    - movies2: List of movies rated by user 2.
    - ratings2: List of ratings given by user 2.
    - threshold: Rating difference threshold for assigning weight points.
    
    Returns:
    - similarity: Final similarity score between 0 and 1.
    - common_movies: List of common movies.
    """
    
    common_movies = set(movies1).intersection(set(movies2))
    
    if not common_movies:
        return 0, []
    
    common_ratio = len(common_movies) / max(len(movies1), len(movies2))
    
    total_weight_score = 0
    total_possible_score = 0
    
    for movie in common_movies:
        try:
            rating1 = ratings1[movies1.index(movie)]
            rating2 = ratings2[movies2.index(movie)]
            
            if rating1 is None or rating2 is None:
                continue
            
            if abs(rating1 - rating2) <= threshold:
                weight = 1 - (abs(rating1 - rating2) / threshold)
            else:
                weight = 0
            
            total_weight_score += weight
            total_possible_score += 1
        
        except ValueError:
            continue
    
    if total_possible_score > 0:
        rating_similarity = total_weight_score / total_possible_score
    else:
        rating_similarity = 0
    
    similarity = (common_ratio * 0.5) + (rating_similarity * 0.5)
    
    return similarity, list(common_movies)

def get_favourite_films(user):
    url = f"https://letterboxd.com/{user}/"
    page = requests.get(url)
    bs4 = BeautifulSoup(page.text, "html.parser")
    films = []
    film_list = bs4.find("ul", class_="poster-list -p150 -horizontal")
    if film_list:
        for film in film_list.find_all("li", class_="poster-container favourite-film-poster-container"):
            div = film.find("div")
            if div:
                img_tag = div.find("img")
                film_name = img_tag["alt"] if img_tag else "Bilinmiyor"
                film_url = (
                    f"https://letterboxd.com{div['data-poster-url'].replace('image-150/', '')}"
                    if "data-poster-url" in div.attrs
                    else None
                )
                movie_slug = div['data-poster-url'].replace('image-150/', '')
                poster_url = create_poster_url(movie_slug)
                films.append(
                    {"name": film_name, "url": film_url, "poster": poster_url}
                )
            else:
                print("Film divi bulunamadı")

    return films

def find_high_rated_common_movies(movies_with_ratings1, movies_with_ratings2):
    """
    Finds movies that both users rated 4.5 or 5 stars.

    Args:
        movies_with_ratings1 (dict): A dictionary of movies and their details for user 1.
        movies_with_ratings2 (dict): A dictionary of movies and their details for user 2.

    Returns:
        list: A list of dictionaries with common movies rated 4.5 or higher by both users.
    """
    common_high_rated_movies = []

    for movie in movies_with_ratings1:
        if movie in movies_with_ratings2:
            rating1 = movies_with_ratings1[movie]['rating']
            rating2 = movies_with_ratings2[movie]['rating']

            if rating1 is not None and rating2 is not None and rating1 >= 4.5 and rating2 >= 4.5:
                common_high_rated_movies.append({
                    "title": movie,
                    "rating_user1": rating1,
                    "rating_user2": rating2,
                    "movie_url": "https://letterboxd.com" + movies_with_ratings1[movie]['movie_url'],
                    "poster_url": create_poster_url(movies_with_ratings1[movie]['movie_url'])
                })

    return common_high_rated_movies

if st.button("Compare"):
    if not user1 or not user2:
        st.warning("Please enter both usernames.")
    else:
        # start_time = time.time()
        
        with st.spinner(f"Fetching movies for {user1}..."):
            img_url1 = get_profile_image(user1)
            movies_with_ratings1 = get_all_movies(user1)
            movies1 = list(movies_with_ratings1.keys())
            ratings1 = [details['rating'] for details in movies_with_ratings1.values()]
        
        with st.spinner(f"Fetching movies for {user2}..."):
            img_url2 = get_profile_image(user2)
            movies_with_ratings2 = get_all_movies(user2)
            movies2 = list(movies_with_ratings2.keys())
            ratings2 = [details['rating'] for details in movies_with_ratings2.values()]
        
        with st.spinner("Fetching favourite films..."):
            favourite_films1 = get_favourite_films(user1)
            favourite_films2 = get_favourite_films(user2)
        
        with st.spinner("Finding movies loved the most by both users..."):
            movies_loved_the_most = find_high_rated_common_movies(movies_with_ratings1, movies_with_ratings2)
                        
        # end_time = time.time()
        # elapsed_time = end_time - start_time
        
        # st.write(f"Time taken: {elapsed_time:.2f} seconds")
        
        if movies1 and movies2:
            # Calculate similarity
            #similarity, common_movies = calculate_similarity(movies1, movies2)
            #similarity_percentage = round(similarity * 100, 2)
            
            similarity, common_movies = calculate_similarity_with_weighted_ratings(movies1, ratings1, movies2, ratings2)
            similarity_percentage = round(similarity * 100, 2)

            col1, col2 = st.columns(2)
            
            st.markdown(
                """
                <style>
                @media only screen and (max-width: 768px) {
                    .stHorizontalBlock {
                        gap: 50px;
                    }
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            if favourite_films1 and favourite_films2:
                st.markdown(
                    f"""
                        <style>
                        .favourite-films-card {{
                            transition: transform 0.3s ease, background-color 0.3s ease;
                        }}
                        .favourite-films-card:hover {{
                            transform: translateY(-5px);
                        }}
                        .user-img {{
                            transition: transform 0.3s ease, background-color 0.3s ease;
                        }}
                        .user-img:hover {{
                            transform: translateY(-5px);
                        }}
                        </style>
                    """,
                        unsafe_allow_html=True,
                )
                with col1:
                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <a href="https://letterboxd.com/{user1}" target="_blank">
                                <img src="{img_url1}" alt="{user1}" id="user_img" class="user-img" style="border-radius: 50%; width: 100px; height: 100px; margin-bottom: 10px;">
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<h4 style='font-size: 16px; text-align: center; font-family: Poppins, sans-serif;'>{user1}'s Favourite Films</h4>",
                        unsafe_allow_html=True,
                    )
                    if favourite_films1:
                        film_posters_html = "".join(
                            f"""
                            <a href="{film['url']}" target="_blank"  class="favourite-films-card">
                                <img src="{film['poster']}" alt="{film['name']}" style="width: 60px; height: auto; margin: 5px; border-radius: 5px;">
                            </a>
                            """
                            for film in favourite_films1 if film["poster"]
                        )
                        st.markdown(
                            f"""
                            <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center;">
                                {film_posters_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                with col2:
                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <a href="https://letterboxd.com/{user2}" target="_blank">
                                <img src="{img_url2}" alt="{user2}" class="user-img" style="border-radius: 50%; width: 100px; height: 100px; margin-bottom: 10px;">
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<h4 style='font-size: 16px; text-align: center; font-family: Poppins, sans-serif;'>{user2}'s Favourite Films</h4>",
                        unsafe_allow_html=True,
                    )
                    if favourite_films2:
                        film_posters_html = "".join(
                            f"""
                            <a href="{film['url']}" target="_blank" class="favourite-films-card">
                                <img src="{film['poster']}" alt="{film['name']}" style="width: 60px; height: auto; margin: 5px; border-radius: 8px;">
                            </a>
                            """
                            for film in favourite_films2 if film["poster"]
                        )
                        st.markdown(
                            f"""
                            <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center;">
                                {film_posters_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            else:
                st.error("Could not fetch favourite films for one or both users.")


            st.markdown(
                "<div style='text-align: center;'><h3>Similarity Score</h3></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="text-align: center; margin-bottom:20px;">
                    The similarity between 
                    <span style="color:#4e82cf; font-weight:bold;">{user1}</span> 
                    and 
                    <span style="color:#913636; font-weight:bold;">{user2}</span> 
                    is <span style="color:#27732a; font-size:18px; font-weight:bold;">{similarity_percentage}%</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            if movies_loved_the_most:
                with st.expander("Movies You Both Loved the Most"):
                    movies_loved_the_most_cards_html = "".join(
                        f"""
                        <a href="{movie['movie_url']}" target="_blank" style="text-decoration: none; color: inherit; display: block; height: 100%; width: 100%; border-radius: 10px;">
                            <div class="movie-card">
                                <img src="{movie['poster_url']}" alt="{movie['title']}" style="width: 70%; height: 150px; object-fit: cover; border-radius: 12px; margin-bottom: 10px;">
                                <div style="font-size: 14px; font-weight: bold; margin-bottom: 5px;">{movie['title']}</div>
                                <div style="font-size: 12px; color: #aaa;">{user1}: {movie['rating_user1']} ★</div>
                                <div style="font-size: 12px; color: #aaa;">{user2}: {movie['rating_user2']} ★</div>
                            </div>
                        </a>
                        """
                        for movie in movies_loved_the_most
                    )

                    st.markdown(
                        f"""
                        <style>
                            .movie-card {{
                                padding: 5px; 
                                background-color: #2b2b2b; 
                                border: 1px solid #444; 
                                border-radius: 10px; 
                                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
                                text-align: center; 
                                font-family: Poppins, sans-serif; 
                                color: #ddd; 
                                width: 100%;
                                height: 100%;
                                box-sizing: border-box;
                                transition: transform 0.3s ease, background-color 0.3s ease;
                            }}
                            
                            .movie-card:hover {{
                                background-color: #272727;
                                transform: translateY(-5px);
                            }}

                            .movie-grid {{
                                display: grid;
                                gap: 10px;
                                justify-items: center;
                                align-items: center;
                                max-width: 100%;
                                padding: 10px;
                                box-sizing: border-box;
                                justify-content: end;
                                height: 100%;
                                min-height: 300px;
                            }}

                            @media (min-width: 768px) {{
                                .movie-grid {{
                                    grid-template-columns: repeat(4, 1fr);
                                }}
                            }}

                            @media (max-width: 767px) {{
                                .movie-grid {{
                                    grid-template-columns: repeat(2, 1fr);
                                }}
                            }}
                        </style>
                        <div class="movie-grid">
                            {movies_loved_the_most_cards_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No movies you both loved the most found.")

            if common_movies:
                with st.expander("Movies You Both Have Watched"):
                    movie_cards_html = "".join(
                        f"""
                        <div class="common-movie-card">
                            {movie}
                        </div>
                        """
                        for movie in common_movies
                    )

                    st.markdown(
                        f"""
                        <style>
                            .common-movie-card {{
                                padding: 5px;
                                background-color: rgba(0, 0, 0, 0.1);
                                border: 1px solid #ddd;
                                border-radius: 8px;
                                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                text-align: center;
                                font-size: 14px;
                                font-weight: bold;
                                color: #ddd;
                                width: 130px;
                                height: 100%;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                box-sizing: border-box;
                            }}

                            .common-movie-grid {{
                                display: grid;
                                gap: 10px;
                                justify-items: center;
                                align-items: center;
                                max-width: 100%;
                                padding: 10px;
                                box-sizing: border-box;
                                justify-content: center;
                                min-height: 75px;
                            }}

                            @media (min-width: 768px) {{
                                .common-movie-grid {{
                                    grid-template-columns: repeat(4, 1fr);
                                }}
                            }}

                            @media (max-width: 767px) {{
                                .common-movie-grid {{
                                    grid-template-columns: repeat(2, 1fr);
                                }}
                            }}
                        </style>

                        <div class="common-movie-grid">
                            {movie_cards_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No movies you both have watched found.")
        else:
            st.error("Could not fetch movies for one or both users.")
            
html('''
  <script>
      // Time of creation of this script = {now}.
      // The time changes everytime and hence would force streamlit to execute JS function
      function scrollToMySection() {{
          var element = window.parent.document.getElementById("{tab_id}");
          if (element) {{
              element.scrollIntoView({{ behavior: "smooth" }});
          }} else {{
              setTimeout(scrollToMySection, 100);
          }}
      }}
      scrollToMySection();
  </script>
  '''.format(now=time.time(), tab_id="user_img")
)
