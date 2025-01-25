import streamlit as st
import requests
from bs4 import BeautifulSoup
from modules.nav import Navbar
import app

st.set_page_config(page_title="Matchboxd-Scout", page_icon="🎬")

Navbar()

SIMILARITY_COLORS = {
    "orange": "#FF8000",
    "green": "#00E054",
    "blue": "#40BCF4"
}

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="cache"], [class*="st-"], h1, h2, h3  {
        font-family: 'Poppins', sans-serif;
    }
    
    div[data-testid="stSidebarNav"] {
        display: none;
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

st.title("Matchboxd-Scout.")
st.write("Find someone, like you.")

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
                poster_url = app.create_poster_url(film_slug)
                
                # Film adını ve slug'ı ekleyin
                films.append({
                    "name": film_name,  # Film adı
                    "url": film_url,
                    "poster": poster_url,
                    "slug": film_slug.split("/")[-2]  # Slug
                })
            else:
                print("Film divi bulunamadı")

    return films

def find_users_with_same_favorites(username, favourite_films):
    # Film slug'larını al
    film_slugs = [film['slug'] for film in favourite_films]
    users = []
    seen_users = set()  # Aynı kullanıcıyı tekrar eklememek için

    # 4 film kombinasyonu için arama
    search_query_4 = " ".join([f"fan:{slug}" for slug in film_slugs])
    search_url = f"https://letterboxd.com/s/search/{search_query_4}/"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        bs4 = BeautifulSoup(response.text, "html.parser")
        for li in bs4.find_all("li", class_="search-result -person"):
            user_link = li.find("a", class_="name")
            if user_link and username not in user_link['href']:
                user_profile_url = f"https://letterboxd.com{user_link['href']}"
                if user_profile_url not in seen_users:
                    seen_users.add(user_profile_url)
                    users.append({
                        "username": user_link.text.strip(),
                        "profile_url": user_profile_url,
                        "avatar": li.find("img")['src'],
                        "common_films": 4
                    })

    # 3 film kombinasyonları için arama
    for i in range(len(film_slugs)):
        for j in range(i + 1, len(film_slugs)):
            for k in range(j + 1, len(film_slugs)):
                search_query_3 = f"fan:{film_slugs[i]} fan:{film_slugs[j]} fan:{film_slugs[k]}"
                search_url = f"https://letterboxd.com/s/search/{search_query_3}/"
                response = requests.get(search_url)
                
                if response.status_code == 200:
                    bs4 = BeautifulSoup(response.text, "html.parser")
                    for li in bs4.find_all("li", class_="search-result -person"):
                        user_link = li.find("a", class_="name")
                        if user_link and username not in user_link['href']:
                            user_profile_url = f"https://letterboxd.com{user_link['href']}"
                            if user_profile_url not in seen_users:
                                seen_users.add(user_profile_url)
                                users.append({
                                    "username": user_link.text.strip(),
                                    "profile_url": user_profile_url,
                                    "avatar": li.find("img")['src'],
                                    "common_films": 3
                                })

    return users

username = st.text_input("Username", placeholder="Enter the Letterboxd username")

if st.button("Find"):
    if not username:
        st.warning("Please enter a username.")
    else:
        with st.spinner("Fetching favourite films..."):
            user_img_url = app.get_profile_image(username)
            favourite_films = get_favourite_films(username)
            users_with_same_favorites = find_users_with_same_favorites(username, favourite_films)
        
        # Tek sütun oluştur
        st.markdown(
            """
            <style>
            .single-column {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.container():  # Tek sütun için container
            st.markdown('<div class="single-column">', unsafe_allow_html=True)

            if favourite_films:
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
                            transition: all 0.3s ease;
                        }}
                        .user-img:hover {{
                            transform: translateY(-5px);
                            border-color: #FFFFFF !important;
                        }}
                        </style>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <a href="https://letterboxd.com/{username}" target="_blank">
                            <img src="{user_img_url}" alt="{username}" title="{username}" class="user-img" style="border-radius: 50%; width: 100px; height: 100px; margin-bottom: 10px; border: 4px solid rgba(255, 255, 255, 0.1); box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);">
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<h4 style='font-size: 16px; text-align: center; font-family: Poppins, sans-serif;'>{username}'s Favourite Films</h4>",
                    unsafe_allow_html=True,
                )
                film_posters_html = "".join(
                    f"""
                    <a href="{film['url']}" target="_blank"  class="favourite-films-card">
                        <img src="{film['poster']}" alt="{film['name']}" title="{film['name']}" style="width: 60px; height: auto; margin: 5px; border-radius: 5px;">
                    </a>
                    """
                    for film in favourite_films
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
                
                if users_with_same_favorites:
                    st.markdown("<h3 style='text-align: center; margin-top: 50px; margin-bottom: -10px;'>Users with similar taste</h3>", unsafe_allow_html=True)
                    
                    # Stil tanımlamaları
                    st.markdown(
                        f"""
                        <style>
                        .user-card {{
                            background-color: #262730;
                            border-radius: 15px;
                            padding: 20px;
                            margin: 10px 0;
                            transition: all 0.3s ease;
                            display: flex;
                            align-items: center;
                            gap: 15px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        }}
                        
                        .user-card:hover {{
                            transform: translateY(-5px);
                            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                            background-color: #2E3140;
                        }}
                        
                        .user-avatar {{
                            width: 60px;
                            height: 60px;
                            border-radius: 50%;
                            border: 3px solid rgba(255, 255, 255, 0.1);
                            transition: all 0.3s ease;
                            cursor: pointer;
                        }}
                        
                        .user-avatar:hover {{
                            border-color: {SIMILARITY_COLORS['orange']} !important;
                        }}
                        
                        .user-info {{
                            flex-grow: 1;
                        }}
                        
                        .user-name {{
                            color: #ffffff !important;
                            font-size: 18px;
                            font-weight: 600;
                            margin-bottom: 5px;
                            text-decoration: none !important;
                        }}
                        
                        .user-name:hover {{
                            color: {SIMILARITY_COLORS['green']} !important;
                            text-decoration: none !important;
                        }}
                        
                        .user-meta {{
                            color: #888;
                            font-size: 14px;
                        }}
                        
                        .view-profile-btn {{
                            background-color: transparent;
                            border: 0.5px solid #FFFFFF;
                            color: {SIMILARITY_COLORS['blue']} !important;
                            padding: 8px 15px;
                            border-radius: 20px;
                            font-size: 14px;
                            font-weight: 500;
                            text-decoration: none !important;
                            transition: all 0.3s ease;
                        }}
                        
                        .view-profile-btn:hover {{
                            background-color: {SIMILARITY_COLORS['blue']};
                            color: #FFFFFF !important;
                            text-decoration: none !important;
                        }}
                        
                        @media (max-width: 768px) {{
                            .user-card {{
                                flex-direction: column;
                                text-align: center;
                                padding: 15px;
                            }}
                            
                            .user-avatar {{
                                width: 80px;
                                height: 80px;
                            }}
                            
                            .view-profile-btn {{
                                margin-top: 10px;
                            }}
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Kullanıcı kartları
                    for user in users_with_same_favorites:
                        # Yıldız sayısına göre HTML oluştur
                        stars_html = "".join([
                            f'<span style="color: {SIMILARITY_COLORS["orange"]}; margin-right: 2px;">★</span>' 
                            for _ in range(user['common_films'])
                        ])
                        
                        st.markdown(
                            f"""
                            <div class="user-card">
                                <a href="{user['profile_url']}" target="_blank"> 
                                    <img src="{user['avatar']}" alt="{user['username']}" title="{user['username']}" class="user-avatar">
                                </a>
                                <div class="user-info">
                                    <a href="{user['profile_url']}" target="_blank" class="user-name">
                                        {user['username']}
                                    </a>
                                    <div class="user-meta" style="color: #888">
                                        {user['profile_url'].split('/')[-2]}
                                        <div style="font-size: 16px;">
                                            {stars_html}
                                        </div>
                                    </div>
                                </div>
                                <a href="{user['profile_url']}" target="_blank" class="view-profile-btn">
                                    View Profile
                                </a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        """
                        <style>
                        .no-users-heading {
                            padding-top: 0 !important;
                            padding-bottom: 0 !important;
                        }
                        </style>
                        <div style="text-align: center; padding: 40px 20px; background-color: #262730; border-radius: 15px; margin: 20px 0;">
                            <h3 class="no-users-heading" style="color: #888; font-size: 18px">No users found with similar taste :(</h3>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:
                st.error("Could not fetch favourite films for one or both users.")

            st.markdown('</div>', unsafe_allow_html=True)
