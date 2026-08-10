import streamlit as st
import pandas as pd 
import requests
import os
from dotenv import load_dotenv
import sqlite3
import altair as alt
load_dotenv()
GOOGLE_BOOKS_API_KEY = st.secrets.get(
    "GOOGLE_BOOKS_API_KEY",
    os.getenv("GOOGLE_BOOKS_API_KEY")
)
# -------------------------
# DATABASE
# -------------------------

conn = sqlite3.connect("books.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    genre TEXT,
    status TEXT,
    rating INTEGER,
    total_pages INTEGER,
    current_page INTEGER,
    notes TEXT,
    favourite INTEGER,
    google_id TEXT
)
""")

conn.commit()
st.set_page_config(
    page_title="BookNest",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #F7F0E6;
}

/* Main headings */
h1, h2, h3 {
    color: #3F7FAA !important;
    font-family: "Georgia", serif;
}

/* Normal text */
p, label, div {
    color: #5C463D;
}

/* Buttons */
.stButton > button {
    background-color: #F6C51C;
    color: #4A4745;
    border: none;
    border-radius: 16px;
    padding: 0.55rem 1rem;
    font-weight: 700;
    transition: all 0.2s ease-in-out;
}

.stButton > button:hover {
    background-color: #E5B617;
    color: #4A4745;
    transform: translateY(-1px);
}

/* Text inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #FFFCFB;
    border: 1px solid #AFC9D8;
    border-radius: 14px;
}

/* Select boxes */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #FFFCFB;
    border: 1px solid #AFC9D8
    border-radius: 14px;
}

/* Progress bars */
.stProgress > div > div > div > div {
    background-color: #B7C9B2;
}

/* Divider */
hr {
    border-color: #D9D0C4;
}

/* Success messages */
div[data-testid="stAlert"] {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)


st.title("📚 BookNest")
st.subheader("Your personal reading tracker")

st.write(
    "Track what you're reading, what you've finished, "
    "and what you want to read next."
)

st.divider()

# -------------------------
# SESSION STORAGE
# -------------------------

if "books" not in st.session_state:
    cursor.execute("""
        SELECT
            id,
            title,
            author,
            genre,
            status,
            rating,
            total_pages,
            current_page,
            notes,
            favourite,
            google_id
        FROM books
    """)

    rows = cursor.fetchall()

    st.session_state.books = []

    for row in rows:
        st.session_state.books.append(
            {
                "id": row[0],
                "title": row[1],
                "author": row[2],
                "genre": row[3],
                "status": row[4],
                "rating": row[5],
                "total_pages": row[6],
                "current_page": row[7],
                "notes": row[8],
                "favourite": bool(row[9]),
                "google_id": row[10]
            }
        )

if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

if "reading_goal" not in st.session_state:
    st.session_state.reading_goal = 20 

# -------------------------
# SEARCH AND FILTERS
# -------------------------

st.header("🔎 Search & Filter")

search_col, genre_col, favourite_col = st.columns(3)

with search_col:
    search_term = st.text_input(
        "Search by title or author"
    )

with genre_col:
    filter_genre = st.selectbox(
        "Filter by genre",
        ["All"] + [
            "Fiction",
            "Fantasy",
            "Romance",
            "Mystery",
            "Thriller",
            "Science Fiction",
            "Historical Fiction",
            "Biography",
            "Memoir",
            "History",
            "Self Development",
            "Philosophy",
            "Religion",
            "Poetry",
            "Other"
        ]
    )

with favourite_col:
    favourites_only = st.checkbox(
        "❤️ Favourites only"
    )

st.divider()
# -------------------------
# FIND A REAL BOOK
# -------------------------

st.header("🔎 Find a Book")

book_search = st.text_input(
    "Start typing a book title",
    placeholder="e.g. Pride and Prejudice",
    key="book_catalogue_search"
)

search_results = []

if len(book_search.strip()) >= 3:

    try:
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": f"intitle:{book_search}",
                "maxResults": 8,
                "key": GOOGLE_BOOKS_API_KEY,
                "country": "GB",
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        for item in data.get("items", []):

            info = item.get("volumeInfo", {})

            search_results.append(
                {
                    "google_id": item.get("id"),
                    "title": info.get("title", "Unknown title"),
                    "author": ", ".join(
                        info.get("authors", ["Unknown author"])
                    ),
                    "total_pages": info.get("pageCount", 0),
                    "published_date": info.get("publishedDate", ""),
                    "thumbnail": info.get(
                        "imageLinks", {}
                    ).get("thumbnail")
                }
            )

    except requests.RequestException as e:
        status_code = e.response.status_code if e.response is not None else "No response"
        error_details = e.response.text if e.response is not None else str(e)
        st.error(f"Book search failed. Status code: {status_code}")
        st.code(error_details)
    

st.divider()


if search_results:

    st.subheader("Book suggestions")

    for book in search_results:

        with st.container(border=True):

            col1, col2 = st.columns([1, 4])

            with col1:

                if book["thumbnail"]:
                    st.image(
                        book["thumbnail"],
                        width=100
                    )

            with col2:

                st.write(f"### {book['title']}")
                st.write(f"✍️ {book['author']}")

                if book["published_date"]:
                    st.write(
                        f"📅 Published: "
                        f"{book['published_date']}"
                    )

                if book["total_pages"] > 1:
                    st.write(
                        f"📄 {book['total_pages']} pages"
                    )

                if st.button("➕ Add to BookNest", key=f"add_google_{book['google_id']}"):
                    cursor.execute("""
                        INSERT INTO books (
                            title,
                            author,
                            genre,
                            status,
                            rating,
                            total_pages,
                            current_page,
                            notes,
                            favourite,
                            google_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        book["title"],
                        book["author"],
                        "Other",
                        "Want to Read",
                        0,
                        book["total_pages"],
                        0,
                        "",
                        0,
                        book["google_id"]
                    ))

                    conn.commit()

                    st.session_state.books.append(
                        {
                            "title": book["title"],
                            "author": book["author"],
                            "genre": "Other",
                            "status": "Want to Read",
                            "rating": 0,
                            "total_pages": book["total_pages"],
                            "current_page": 0,
                            "notes": "",
                            "favourite": False,
                            "google_id": book["google_id"]
                        }
                    )

                    st.success(f"📚 {book['title']} added to your BookNest!")
                    st.rerun()
   

st.divider()
# -------------------------
# ADD A BOOK
# -------------------------

# -------------------------
# READING DASHBOARD
# -------------------------

st.header("📊 My Reading Dashboard")

goal_col, space_col = st.columns([1, 3])

with goal_col:
    st.session_state.reading_goal = st.number_input(
        "🎯 Reading goal",
        min_value=1,
        value=st.session_state.reading_goal,
        step=1
    )

total_books = len(st.session_state.books)

finished_books = len([
    book for book in st.session_state.books
    if book["status"] == "Finished"
])

currently_reading_count = len([
    book for book in st.session_state.books
    if book["status"] == "Currently Reading"
])

pages_read = 0

for book in st.session_state.books:
    if book["status"] == "Finished":
        pages_read += book["total_pages"]

    elif book["status"] == "Currently Reading":
        pages_read += book["current_page"]

rated_books = [
    book["rating"]
    for book in st.session_state.books
    if book["rating"] > 0
]

if rated_books:
    average_rating = sum(rated_books) / len(rated_books)
else:
    average_rating = 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📚 Books", total_books)

with col2:
    st.metric("📖 Reading", currently_reading_count)

with col3:
    st.metric("✅ Finished", finished_books)

with col4:
    st.metric("📄 Pages Read", pages_read)

with col5:
    st.metric("⭐ Average Rating", f"{average_rating:.1f}")

st.subheader("🎯 Reading Goal")

goal_progress = min(
    finished_books / st.session_state.reading_goal,
    1.0
)

st.progress(goal_progress)

st.write(
    f"**{finished_books} of "
    f"{st.session_state.reading_goal} books completed**"
)

if finished_books >= st.session_state.reading_goal:
    st.success("🎉 Reading goal achieved!")


# -------------------------
# GENRE CHART
# -------------------------

if st.session_state.books:

    st.subheader("📚 Books by Genre")

    genre_counts = {}

    for book in st.session_state.books:
        genre = book["genre"]

        if genre in genre_counts:
            genre_counts[genre] += 1
        else:
            genre_counts[genre] = 1

    genre_data = pd.DataFrame(
        {
            "Genre": genre_counts.keys(),
            "Books": genre_counts.values()
        }
    )

    genre_data = genre_data.set_index("Genre")

    

genre_chart = alt.Chart(
    genre_data.reset_index()
).mark_bar(
    color="#A66B7A",
    cornerRadiusTopLeft=8,
    cornerRadiusTopRight=8
).encode(
    x=alt.X(
        "Genre:N",
        title=None,
        axis=alt.Axis(labelColor="#4A4745")
    ),
    y=alt.Y(
        "Books:Q",
        title="Books",
        axis=alt.Axis(
            labelColor="#4A4745",
            titleColor="#4A4745",
            tickMinStep=1
        )
    ),
    tooltip=["Genre", "Books"]
).properties(
    background="#FFFCF8",
    height=320
).configure_view(
    strokeWidth=0
).configure_axis(
    gridColor="#EADFD8",
    gridOpacity=0.45,
    domain=False,
    tickColor="#EADFD8",
    labelColor="#6B5550",
    titleColor="#6B5550"
)

st.altair_chart(genre_chart, use_container_width=True)
st.divider()

st.header("➕ Add a Book")

col1, col2 = st.columns(2)

with col1:
    book_title = st.text_input("Book title", key="new_title")
    author = st.text_input("Author", key="new_author")

    genre = st.selectbox(
        "Genre",
        [
            "Fiction",
            "Fantasy",
            "Romance",
            "Mystery",
            "Thriller",
            "Science Fiction",
            "Historical Fiction",
            "Biography",
            "Memoir",
            "History",
            "Self Development",
            "Philosophy",
            "Religion",
            "Poetry",
            "Other"
        ],
        key="new_genre"
    )

    total_pages = st.number_input(
        "Total pages",
        min_value=0,
        step=1,
        key="new_total_pages"
    )

with col2:
    status = st.selectbox(
        "Reading status",
        ["Want to Read", "Currently Reading", "Finished"],
        key="new_status"
    )

    current_page = st.number_input(
        "Current page",
        min_value=0,
        step=1,
        key="new_current_page"
    )

    rating = st.slider(
        "Rating",
        0,
        5,
        0,
        key="new_rating"
    )

    favourite = st.checkbox(
        "❤️ Add to favourites",
        key="new_favourite"
    )

notes = st.text_area(
    "Notes or review",
    placeholder="Write your thoughts about this book...",
    key="new_notes"
)

if st.button("Add to BookNest", type="primary"):

    if not book_title:
        st.warning("Please enter a book title.")

    elif current_page > total_pages:
        st.warning("Current page cannot be greater than total pages.")

    else:
        new_book = {
            "title": book_title,
            "author": author,
            "genre": genre,
            "status": status,
            "rating": rating,
            "total_pages": total_pages,
            "current_page": current_page,
            "notes": notes,
            "favourite": favourite
        }

        cursor.execute("""
        INSERT INTO books (
            title,
            author,
            genre,
            status,
            rating,
            total_pages,
            current_page,
            notes,
            favourite,
            google_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        book_title,
        author,
        genre,
        status,
        rating,
        total_pages,
        current_page,
        notes,
        int(favourite),
        None
    ))

    conn.commit()
    st.session_state.books.append(new_book)

    st.success(f"📖 {book_title} added to your library!")

st.divider()


# -------------------------
# BOOKSHELF
# -------------------------

st.header("📚 My Bookshelf")

filtered_books = []

for index, book in enumerate(st.session_state.books):

    matches_search = (
        search_term.lower() in book["title"].lower()
        or
        search_term.lower() in book["author"].lower()
    )

    matches_genre = (
        filter_genre == "All"
        or book["genre"] == filter_genre
    )

    matches_favourite = (
        not favourites_only
        or book["favourite"]
    )

    if matches_search and matches_genre and matches_favourite:
        filtered_books.append((index, book))


want_to_read = [
    (index, book)
    for index, book in filtered_books
    if book["status"] == "Want to Read"
]

currently_reading = [
    (index, book)
    for index, book in filtered_books
    if book["status"] == "Currently Reading"
]

finished = [
    (index, book)
    for index, book in filtered_books
    if book["status"] == "Finished"
]

tab1, tab2, tab3 = st.tabs(
    ["📌 Want to Read", "📖 Currently Reading", "✅ Finished"]
)


# -------------------------
# BOOK DISPLAY FUNCTION
# -------------------------

def show_book(book, index):

    title_text = book["title"]

    if book["favourite"]:
        title_text += " ❤️"

    st.subheader(title_text)

    st.write(f"✍️ **Author:** {book['author']}")
    st.write(f"🏷️ **Genre:** {book['genre']}")
    st.write(f"📚 **Status:** {book['status']}")

    if book["status"] == "Currently Reading":

        progress = book["current_page"] / book["total_pages"]
        percentage = round(progress * 100)

        st.write(
            f"📖 Page {book['current_page']} "
            f"of {book['total_pages']}"
        )

        st.progress(progress)

        st.write(f"**{percentage}% complete**")

    elif book["status"] == "Finished":

        st.progress(1.0)
        st.write("**100% complete 🎉**")

    else:
        st.write(f"📄 {book['total_pages']} pages")

    if book["rating"] > 0:
        st.write("⭐" * book["rating"])

    if book["notes"]:
        st.write("📝 **Notes / Review**")
        st.write(book["notes"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "✏️ Edit",
            key=f"edit_{index}"
        ):
            st.session_state.editing_index = index
            st.rerun()

    with col2:
        if st.button(
            "🗑️ Delete",
            key=f"delete_{index}"
        ):
            cursor.execute("DELETE FROM books WHERE id = ?", (book["id"],))
            conn.commit()
            del st.session_state["books"]
            st.session_state.editing_index = None
            st.rerun()

    st.divider()


# -------------------------
# DISPLAY TABS
# -------------------------

with tab1:
    if not want_to_read:
        st.info("No books here yet.")
    else:
        for index, book in want_to_read:
            with st.container(border=True):
                show_book(book, index)

with tab2:
    if not currently_reading:
        st.info("You're not currently reading anything.")
    else:
        for index, book in currently_reading:
            show_book(book, index)

with tab3:
    if not finished:
        st.info("No finished books yet.")
    else:
        for index, book in finished:
            show_book(book, index)


# -------------------------
# EDIT A BOOK
# -------------------------

if st.session_state.editing_index is not None:

    index = st.session_state.editing_index

    if index < len(st.session_state.books):

        book = st.session_state.books[index]

        st.divider()

        st.header("✏️ Edit Book")

        edit_title = st.text_input(
            "Book title",
            value=book["title"],
            key="edit_title"
        )

        edit_author = st.text_input(
            "Author",
            value=book["author"],
            key="edit_author"
        )

        genres = [
            "Fiction",
            "Fantasy",
            "Romance",
            "Mystery",
            "Thriller",
            "Science Fiction",
            "Historical Fiction",
            "Biography",
            "Memoir",
            "History",
            "Self Development",
            "Philosophy",
            "Religion",
            "Poetry",
            "Other"
        ]

        edit_genre = st.selectbox(
            "Genre",
            genres,
            index=genres.index(book["genre"]),
            key="edit_genre"
        )

        statuses = [
            "Want to Read",
            "Currently Reading",
            "Finished"
        ]

        edit_status = st.selectbox(
            "Reading status",
            statuses,
            index=statuses.index(book["status"]),
            key="edit_status"
        )

        edit_total_pages = st.number_input(
            "Total pages",
            min_value=1,
            value=book["total_pages"],
            step=1,
            key="edit_total_pages"
        )

        edit_current_page = st.number_input(
            "Current page",
            min_value=0,
            value=book["current_page"],
            step=1,
            key="edit_current_page"
        )

        edit_rating = st.slider(
            "Rating",
            0,
            5,
            book["rating"],
            key="edit_rating"
        )

        edit_favourite = st.checkbox(
            "❤️ Favourite",
            value=book["favourite"],
            key="edit_favourite"
        )

        edit_notes = st.text_area(
            "Notes or review",
            value=book["notes"],
            key="edit_notes"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "💾 Save Changes",
                type="primary"
            ):

                if edit_current_page > edit_total_pages:
                    st.warning(
                        "Current page cannot be greater "
                        "than total pages."
                    )

                else:

                    cursor.execute("""
                        UPDATE books
                        SET
                            title = ?,
                            author = ?,
                            genre = ?,
                            status = ?,
                            rating = ?,
                            total_pages = ?,
                            current_page = ?,
                            notes = ?,
                            favourite = ?
                        WHERE id = ?
                    """, (
                        edit_title,
                        edit_author,
                        edit_genre,
                        edit_status,
                        edit_rating,
                        edit_total_pages,
                        edit_current_page,
                        edit_notes,
                        int(edit_favourite),
                        st.session_state.books[index]["id"]
                    ))

                    conn.commit()   
                    st.session_state.books[index] = {
                        "title": edit_title,
                        "author": edit_author,
                        "genre": edit_genre,
                        "status": edit_status,
                        "rating": edit_rating,
                        "total_pages": edit_total_pages,
                        "current_page": edit_current_page,
                        "notes": edit_notes,
                        "favourite": edit_favourite,
                        "id": st.session_state.books[index]["id"],
                        "google_id": st.session_state.books[index].get("google_id")
                                            }

                    st.session_state.editing_index = None

                    st.success("Book updated!")

                    st.rerun()

        with col2:

            if st.button("Cancel Editing"):

                st.session_state.editing_index = None
                st.rerun()