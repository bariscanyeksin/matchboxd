import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
from streamlit.components.v1 import html
import numpy as np

st.set_page_config(page_title="Matchboxd", page_icon="🎬")

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

page_bg_img = """
<style>
.stApp {
    background-image: url("https://i.ibb.co/gPfxJQz/bg-opacity-min.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
.stAppHeader {
    display: none;
}
.stMainBlockContainer {
    padding-top: 0px;
    padding-bottom: 0px;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("Matchboxd.")
st.write("Compare the films watched by two Letterboxd users.")

with st.expander("How to find username?"):
    st.markdown(
        """
        <div style="margin-bottom: 15px;">
            <h4>On PC:</h4>
            <p>Letterboxd username is typically the name that appears in the URL when you visit a user profile. For example:</p>
            <p style="color: #3498db; font-size:15px;">https://letterboxd.com/<strong>username</strong>/</p>
        </div>
        <div style="margin-bottom: 15px;">
            <h4>On Phone:</h4>
            <p>Open the Letterboxd app, go to a profile, tap the <strong>three-dots icon</strong> at the top right.</p>
        </div>
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://i.ibb.co/yqR89kj/user-page.jpg" 
            alt="Example of finding a username on the Letterboxd app"
            class="mobile_img">
        </div>
        <div style="margin-bottom: 15px;">
            <p>And you'll see the username in the marked field.</p>
        </div>
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://i.ibb.co/g9zRnFt/get-username.jpg" 
            alt="Example of finding a username on the Letterboxd app"
            class="mobile_img">
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
        unsafe_allow_html=True,
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


def create_poster_url(film_slug):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "referer": f"https://letterboxd.com/{film_slug}",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    }

    response = requests.get(f"https://letterboxd.com/{film_slug}", headers=headers)

    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    script_tag = soup.find("script", type="application/ld+json")

    if script_tag:
        json_str = script_tag.string.strip()

        if json_str.startswith("/* <![CDATA[ */") and json_str.endswith("/* ]]> */"):
            json_str = json_str[len("/* <![CDATA[ */") : -len("/* ]]> */")].strip()

        try:
            json_data = json.loads(json_str)
            image_url = json_data.get("image", None)

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


def get_all_films(username):
    base_url = f"https://letterboxd.com/{username}/films/by/entry-rating/page/"
    films_with_details = {}
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
        film_list = soup.find(
            "ul", {"class": "poster-list -p70 -grid film-list clear"}
        )

        if not film_list:
            break

        for li in film_list.find_all("li"):
            div = li.find("div", {"data-target-link": True})
            if div:
                title = div.find("img").get("alt")

                film_url = div["data-target-link"]

                rating_span = li.find("span", {"class": "rating"})
                if rating_span:
                    rating_text = rating_span.text.strip()
                    rating = rating_text.count("★") + 0.5 * rating_text.count("½")
                else:
                    rating = 0

                films_with_details[film_url] = {
                    "title": title,
                    "rating": rating
                }

    return films_with_details


def calculate_similarity_with_weighted_ratings(
    films1, ratings1, films2, ratings2, threshold=0.1, weight_common=0.5, weight_ratings=0.5
):
    if not films1 or not films2:
        return 0

    film_rating_map1 = dict(zip(films1, ratings1))
    film_rating_map2 = dict(zip(films2, ratings2))

    common_films = set(film_rating_map1.keys()).intersection(film_rating_map2.keys())
    if not common_films:
        return 0

    common_ratio = len(common_films) / max(len(films1), len(films2))

    total_weight_score = 0
    total_possible_score = 0

    for film in common_films:
        rating1 = film_rating_map1.get(film)
        rating2 = film_rating_map2.get(film)

        if rating1 is None or rating2 is None:
            continue

        difference = abs(rating1 - rating2)
        if difference <= threshold:
            weight = 1 - (difference / threshold)
        else:
            weight = 0

        total_weight_score += weight
        total_possible_score += 1

    rating_similarity = (
        total_weight_score / total_possible_score if total_possible_score > 0 else 0
    )

    similarity = (common_ratio * weight_common) + (rating_similarity * weight_ratings)
    return similarity

def calculate_enhanced_similarity(films1, ratings1, films2, ratings2):
    if not films1 or not films2:
        return 0

    film_rating_map1 = dict(zip(films1, ratings1))
    film_rating_map2 = dict(zip(films2, ratings2))
    
    common_films = set(film_rating_map1.keys()).intersection(film_rating_map2.keys())
    if not common_films:
        return 0
        
    # Ortak film oranı (Jaccard similarity)
    jaccard_similarity = len(common_films) / len(set(films1).union(films2))
    
    # Pearson korelasyon katsayısı
    common_ratings1 = [film_rating_map1[f] for f in common_films]
    common_ratings2 = [film_rating_map2[f] for f in common_films]
    
    if len(common_ratings1) < 2:  # Pearson korelasyonu için en az 2 veri noktası gerekli
        return jaccard_similarity
        
    correlation = np.corrcoef(common_ratings1, common_ratings2)[0, 1]
    
    # Genre-based similarity eklenebilir
    # Temporal similarity eklenebilir (kullanıcıların filmleri izleme zamanları)
    
    # Ağırlıklı ortalama
    weights = {
        'jaccard': 0.3,
        'correlation': 0.7
    }
    
    final_similarity = (
        weights['jaccard'] * jaccard_similarity +
        weights['correlation'] * (correlation if not np.isnan(correlation) else 0)
    )
    
    return max(0, min(1, final_similarity))
    
def calculate_similarity_basic(films1, films2):
    common_films = set(films1).intersection(set(films2))

    if not common_films:
        return 0, 0, 0

    common_ratio_user1 = len(common_films) / len(films1)
    common_ratio_user2 = len(common_films) / len(films2)

    return common_ratio_user1, common_ratio_user2

def get_favourite_films(user):
    url = f"https://letterboxd.com/{user}/"
    page = requests.get(url)
    bs4 = BeautifulSoup(page.text, "html.parser")
    films = []
    film_list = bs4.find("ul", class_="poster-list -p150 -horizontal")
    if film_list:
        for film in film_list.find_all(
            "li", class_="poster-container favourite-film-poster-container"
        ):
            div = film.find("div")
            if div:
                img_tag = div.find("img")
                film_name = img_tag["alt"] if img_tag else "Bilinmiyor"
                film_url = (
                    f"https://letterboxd.com{div['data-poster-url'].replace('image-150/', '')}"
                    if "data-poster-url" in div.attrs
                    else None
                )
                film_slug = div["data-poster-url"].replace("image-150/", "")
                poster_url = create_poster_url(film_slug)
                films.append({"name": film_name, "url": film_url, "poster": poster_url})
            else:
                print("Film divi bulunamadı")

    return films


def get_watchlist(username):
    base_url = f"https://letterboxd.com/{username}/watchlist/by/date-newest/page/"
    watchlist = {}
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
        film_list = soup.find(
            "ul", {"class": "poster-list -p125 -grid -scaled128"}
        )

        if not film_list:
            break

        for li in film_list.find_all("li"):
            div = li.find("div", {"data-target-link": True})
            if div:
                title = div.find("img").get("alt")

                film_url = div["data-target-link"]

                rating_span = li.find("span", {"class": "rating"})
                if rating_span:
                    rating_text = rating_span.text.strip()
                    rating = rating_text.count("★") + 0.5 * rating_text.count("½")
                else:
                    rating = 0

                watchlist[film_url] = {
                    "title": title,
                    "rating": rating
                }
    return watchlist


def find_high_rated_common_films(films_with_ratings1, films_with_ratings2):
    common_high_rated_films = []

    for film in films_with_ratings1:
        if film in films_with_ratings2:
            rating1 = films_with_ratings1[film]["rating"]
            rating2 = films_with_ratings2[film]["rating"]

            if (
                rating1 is not None
                and rating2 is not None
                and rating1 >= 4
                and rating2 >= 4
            ):
                common_high_rated_films.append(
                    {
                        "title": films_with_ratings1[film]["title"],
                        "rating_user1": rating1,
                        "rating_user2": rating2,
                        "film_url": "https://letterboxd.com" + film,
                        "poster_url": create_poster_url(film),
                    }
                )

    return common_high_rated_films


def find_low_rated_common_films(films_with_ratings1, films_with_ratings2):
    common_low_rated_films = []

    for film in films_with_ratings1:
        if film in films_with_ratings2:
            rating1 = films_with_ratings1[film]["rating"]
            rating2 = films_with_ratings2[film]["rating"]

            if (
                rating1 is not None
                and rating2 is not None
                and 0.5 <= rating1 <= 2
                and 0.5 <= rating2 <= 2
            ):
                common_low_rated_films.append(
                    {
                        "title": films_with_ratings1[film]["title"],
                        "rating_user1": rating1,
                        "rating_user2": rating2,
                        "film_url": "https://letterboxd.com" + film,
                        "poster_url": create_poster_url(film),
                    }
                )

    return common_low_rated_films


def find_common_films_from_watchlist(watchlist_films1, watchlist_films2):
    common_films_from_watchlist = []
    watchlist_films2_set = set(watchlist_films2.keys())

    for film, details in watchlist_films1.items():
        if film in watchlist_films2_set:
            rating1 = details.get("rating")
            rating2 = watchlist_films2[film].get("rating")

            if rating1 is not None and rating2 is not None:
                common_films_from_watchlist.append(
                    {
                        "title": details["title"],
                        "rating_user1": rating1,
                        "rating_user2": rating2,
                        "film_url": "https://letterboxd.com" + film,
                        "poster_url": create_poster_url(film),
                    }
                )

    return common_films_from_watchlist

if st.button("Compare"):
    if not user1 or not user2:
        st.warning("Please enter both usernames.")
    else:
        if user1 == user2:
            st.warning("You cannot compare a user with themselves.")
        else:
            # start_time = time.time()

            with st.spinner(f"Fetching films for {user1}..."):
                img_url1 = get_profile_image(user1)
                films_with_ratings1 = get_all_films(user1)
                films_from_watchlist1 = get_watchlist(user1)
                films1 = list(films_with_ratings1.keys())
                ratings1 = [details["rating"] for details in films_with_ratings1.values()]

            with st.spinner(f"Fetching films for {user2}..."):
                img_url2 = get_profile_image(user2)
                films_with_ratings2 = get_all_films(user2)
                films_from_watchlist2 = get_watchlist(user2)
                films2 = list(films_with_ratings2.keys())
                ratings2 = [details["rating"] for details in films_with_ratings2.values()]

            with st.spinner("Fetching favourite films..."):
                favourite_films1 = get_favourite_films(user1)
                favourite_films2 = get_favourite_films(user2)

            with st.spinner("Finding films loved the most by both users..."):
                films_loved_the_most = find_high_rated_common_films(
                    films_with_ratings1, films_with_ratings2
                )

            with st.spinner("Finding films hated the most by both users..."):
                films_hated_the_most = find_low_rated_common_films(
                    films_with_ratings1, films_with_ratings2
                )

            with st.spinner("Fetching watchlists..."):
                films_watch_together = find_common_films_from_watchlist(
                    films_from_watchlist1, films_from_watchlist2
                )

            # end_time = time.time()
            # elapsed_time = end_time - start_time

            # st.write(f"Time taken: {elapsed_time:.2f} seconds")

            if films1 and films2:
                # Calculate similarity
                detailed_similarity = calculate_enhanced_similarity(films1, ratings1, films2, ratings2)
                similarity_percentage = int(round(detailed_similarity * 100, 2))

                common_ratio_user1, common_ratio_user2 = calculate_similarity_basic(
                    films1, films2
                )
                
                user1_percentage = int(round(common_ratio_user1 * 100))
                user2_percentage = int(round(common_ratio_user2 * 100))

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
                            <div id="user_img"></div>
                            <div style="text-align: center;">
                                <a href="https://letterboxd.com/{user1}" target="_blank">
                                    <img src="{img_url1}" alt="{user1}" title="{user1}" class="user-img" style="border-radius: 50%; width: 100px; height: 100px; margin-bottom: 10px; border: 4px solid rgba(255, 255, 255, 0.8); box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);">
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
                                    <img src="{film['poster']}" alt="{film['name']}" title="{film['name']}" style="width: 60px; height: auto; margin: 5px; border-radius: 5px;">
                                </a>
                                """
                                for film in favourite_films1
                                if film["poster"]
                            )
                            st.markdown(
                                f"""
                                <div style="display: flex; overflow-x: auto; white-space: nowrap; justify-content: center; align-items: center; gap: 10px; padding: 10px;">
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
                                    <img src="{img_url2}" alt="{user2}" title="{user2}" class="user-img" style="border-radius: 50%; width: 100px; height: 100px; margin-bottom: 10px; border: 4px solid rgba(255, 255, 255, 0.8); box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);">
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
                                    <img src="{film['poster']}" alt="{film['name']}" title="{film['name']}" style="width: 60px; height: auto; margin: 5px; border-radius: 8px;">
                                </a>
                                """
                                for film in favourite_films2
                                if film["poster"]
                            )
                            st.markdown(
                                f"""
                                <div style="display: flex; overflow-x: auto; white-space: nowrap; justify-content: center; align-items: center; gap: 10px; padding: 10px;">
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
                    <div style="text-align: center; margin-bottom: 10px;">
                        <span style="font-size: 48px; font-weight: bold; color: #40BCF4;">{similarity_percentage}%</span>
                    </div>
                    <div style="text-align: center; color: #999; font-size: 14px; margin-bottom: 30px;">
                        also...
                        <ul style="list-style: none; padding: 0; margin: 10px 0;">
                            <li style="margin: 5px 0;">• {user1} has seen <span style="font-weight: bold;">{user2_percentage}%</span> of {user2}'s watched films</li>
                            <li style="margin: 5px 0;">• {user2} has seen <span style="font-weight: bold;">{user1_percentage}%</span> of {user1}'s watched films</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if films_loved_the_most:
                    with st.expander("Films You Both Loved the Most ❤️"):
                        films_loved_the_most_cards_html = "".join(
                            f"""
                            <a href="{film['film_url']}" title="{film['title']}" target="_blank" style="text-decoration: none; color: inherit; display: block; height: 100%; width: 100%; border-radius: 10px;">
                                <div class="films-loved-the-most-card">
                                    <img src="{film['poster_url']}" alt="{film['title']}" class="films-loved-the-most-image">
                                    <div style="font-size: 14px; font-weight: bold; margin-bottom: 5px;">{film['title']}</div>
                                    <div style="font-size: 12px; color: #aaa;">{user1}: {film['rating_user1']} ★</div>
                                    <div style="font-size: 12px; color: #aaa;">{user2}: {film['rating_user2']} ★</div>
                                </div>
                            </a>
                            """
                            for film in films_loved_the_most
                        )

                        st.markdown(
                            f"""
                            <style>
                                .films-loved-the-most-card {{
                                    padding: 5px; 
                                    background-color: #262730; 
                                    border: 0px solid #444; 
                                    border-radius: 10px; 
                                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
                                    text-align: center; 
                                    font-family: Poppins, sans-serif; 
                                    color: #ddd; 
                                    max-width: 100%;
                                    height: 100%;
                                    box-sizing: border-box;
                                    transition: transform 0.3s ease, background-color 0.3s ease;
                                }}

                                .films-loved-the-most-grid {{
                                    display: grid;
                                    gap: 10px;
                                    justify-items: center;
                                    align-items: center;
                                    max-width: 100%;
                                    height: 100%;
                                    padding: 10px;
                                    box-sizing: border-box;
                                    justify-content: center;
                                }}
                                
                                .films-loved-the-most-image {{
                                    object-fit: cover;
                                    border-radius: 12px;
                                    margin-bottom: 10px;
                                }}
                                
                                @media (max-width: 480px) {{
                                    .films-loved-the-most-grid {{
                                        grid-template-columns: repeat(1, 1fr);
                                    }}
                                    
                                    .films-loved-the-most-image {{
                                        width: 50%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}
                                
                                @media (max-width: 767px) and (min-width: 481px) {{
                                    .films-loved-the-most-grid {{
                                        grid-template-columns: repeat(2, 1fr);
                                    }}
                                    
                                    .films-loved-the-most-image {{
                                        width: 40%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}

                                @media (min-width: 768px) {{
                                    .films-loved-the-most-grid {{
                                        grid-template-columns: repeat(4, 1fr);
                                    }}
                                    
                                    .films-loved-the-most-card:hover {{
                                        background-color: #484A5B;
                                        transform: translateY(-5px);
                                    }}
                                    
                                    .films-loved-the-most-image {{
                                        width: 70%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}
                                    
                            </style>
                            <div class="films-loved-the-most-grid">
                                {films_loved_the_most_cards_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    with st.expander("Films You Both Loved the Most ❤️"):
                        st.write("No films you both loved the most found.")

                if films_hated_the_most:
                    with st.expander("Films You Both Hated the Most 😤"):
                        films_hated_the_most_cards_html = "".join(
                            f"""
                            <a href="{film['film_url']}" title="{film['title']}" target="_blank" style="text-decoration: none; color: inherit; display: block; height: 100%; width: 100%; border-radius: 10px;">
                                <div class="films-hated-the-most-card" title="{film['title']}">
                                    <img src="{film['poster_url']}" alt="{film['title']}" class="films-hated-the-most-image">
                                    <div style="font-size: 14px; font-weight: bold; margin-bottom: 5px;">{film['title']}</div>
                                    <div style="font-size: 12px; color: #aaa;">{user1}: {film['rating_user1']} ★</div>
                                    <div style="font-size: 12px; color: #aaa;">{user2}: {film['rating_user2']} ★</div>
                                </div>
                            </a>
                            """
                            for film in films_hated_the_most
                        )

                        st.markdown(
                            f"""
                            <style>
                                .films-hated-the-most-card {{
                                    padding: 5px; 
                                    background-color: #262730; 
                                    border: 0px solid #444; 
                                    border-radius: 10px; 
                                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
                                    text-align: center; 
                                    font-family: Poppins, sans-serif; 
                                    color: #ddd; 
                                    max-width: 100%;
                                    height: 100%;
                                    box-sizing: border-box;
                                    transition: transform 0.3s ease, background-color 0.3s ease;
                                }}

                                .films-hated-the-most-grid {{
                                    display: grid;
                                    gap: 10px;
                                    justify-items: center;
                                    align-items: center;
                                    max-width: 100%;
                                    height: 100%;
                                    padding: 10px;
                                    box-sizing: border-box;
                                    justify-content: center;
                                }}
                                
                                .films-hated-the-most-image {{
                                    object-fit: cover;
                                    border-radius: 12px;
                                    margin-bottom: 10px;
                                }}
                                
                                @media (max-width: 480px) {{
                                    .films-hated-the-most-grid {{
                                        grid-template-columns: repeat(1, 1fr);
                                    }}
                                    
                                    .films-hated-the-most-image {{
                                        width: 50%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}
                                
                                @media (max-width: 767px) and (min-width: 481px) {{
                                    .films-hated-the-most-grid {{
                                        grid-template-columns: repeat(2, 1fr);
                                    }}
                                    
                                    .films-hated-the-most-image {{
                                        width: 40%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}

                                @media (min-width: 768px) {{
                                    .films-hated-the-most-grid {{
                                        grid-template-columns: repeat(4, 1fr);
                                    }}
                                    
                                    .films-hated-the-most-card:hover {{
                                        background-color: #484A5B;
                                        transform: translateY(-5px);
                                    }}
                                    
                                    .films-hated-the-most-image {{
                                        width: 70%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}
                                    
                            </style>
                            <div class="films-hated-the-most-grid">
                                {films_hated_the_most_cards_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    with st.expander("Films You Both Hated the Most 😤"):
                        st.write("No films you both hated the most found.")

                if films_watch_together:
                    with st.expander("Films You Both May Want to Watch Together 🫂"):
                        films_watch_together_cards_html = "".join(
                            f"""
                            <a href="{film['film_url']}" title="{film['title']}" target="_blank" style="text-decoration: none; color: inherit; display: block; height: 100%; width: 100%; border-radius: 10px;">
                                <div class="films_watch_together-card">
                                    <img src="{film['poster_url']}" alt="{film['title']}" class="films_watch_together-image">
                                    <div style="font-size: 14px; font-weight: bold; margin-bottom: 5px;">{film['title']}</div>
                                </div>
                            </a>
                            """
                            for film in films_watch_together
                        )

                        st.markdown(
                            f"""
                            <style>
                                .films_watch_together-card {{
                                    padding: 5px; 
                                    background-color: #262730; 
                                    border: 0px solid #444; 
                                    border-radius: 10px; 
                                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
                                    text-align: center; 
                                    font-family: Poppins, sans-serif; 
                                    color: #ddd; 
                                    max-width: 100%;
                                    height: 100%;
                                    box-sizing: border-box;
                                    transition: transform 0.3s ease, background-color 0.3s ease;
                                }}

                                .films_watch_together-grid {{
                                    display: grid;
                                    gap: 10px;
                                    justify-items: center;
                                    align-items: center;
                                    max-width: 100%;
                                    height: 100%;
                                    padding: 10px;
                                    box-sizing: border-box;
                                    justify-content: center;
                                }}
                                
                                .films_watch_together-image {{
                                    object-fit: cover;
                                    border-radius: 12px;
                                    margin-bottom: 10px;
                                }}
                                
                                @media (max-width: 480px) {{
                                    .films_watch_together-grid {{
                                        grid-template-columns: repeat(1, 1fr);
                                    }}
                                    
                                    .films_watch_together-image {{
                                        width: 50%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}
                                
                                @media (max-width: 767px) and (min-width: 481px) {{
                                    .films_watch_together-grid {{
                                        grid-template-columns: repeat(2, 1fr);
                                    }}
                                    
                                    .films_watch_together-image {{
                                        width: 40%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}

                                @media (min-width: 768px) {{
                                    .films_watch_together-grid {{
                                        grid-template-columns: repeat(4, 1fr);
                                    }}
                                    
                                    .films_watch_together-card:hover {{
                                        background-color: #484A5B;
                                        transform: translateY(-5px);
                                    }}
                                    
                                    .films_watch_together-image {{
                                        width: 70%;
                                        aspect-ratio: 2 / 3;
                                    }}
                                }}
                                    
                            </style>
                            <div class="films_watch_together-grid">
                                {films_watch_together_cards_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    with st.expander("Films You Both May Want to Watch Together 🫂"):
                        st.write("No films you both may want to watch together found.")

            else:
                st.error("Could not fetch films for one or both users.")

html(
    """
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
  """.format(
        now=time.time(), tab_id="user_img"
    )
)
