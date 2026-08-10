# 📚 BookNest

**A personal reading tracker built with Python and Streamlit.**

## 📸 App Preview

![BookNest App Preview](booknest%20preview.png)

BookNest is a web-based application that allows users to organise their books, track their reading progress and view statistics about their reading habits.

I developed BookNest as a personal programming project to build my practical skills in Python, databases, APIs and web application development.

## ✨ Features

- 🔎 Search for books using the Google Books API
- ➕ Add books manually or from search results
- 📌 Organise books into Want to Read, Currently Reading and Finished
- 📖 Track the current page and reading progress
- ⭐ Rate finished books
- ❤️ Mark books as favourites
- 📝 Add personal notes and reviews
- ✏️ Edit existing book information
- 🗑️ Delete books from the library
- 🎯 Set a personal reading goal
- 📊 View reading statistics and books by genre
- 💾 Persistent storage using SQLite

## 🛠️ Technologies Used

- **Python** – core application logic
- **Streamlit** – interactive web interface
- **SQLite** – persistent book storage
- **Google Books API** – book search and metadata
- **Pandas** – data handling
- **Altair** – data visualisation
- **python-dotenv** – secure management of the API key
- **Git & GitHub** – version control and project hosting

## 💡 What I Learned

Building BookNest gave me practical experience of developing an application from an initial idea into a working project.

During development I worked with API requests, JSON data, Python dictionaries, loops, conditional logic, functions, session state and SQL queries.

I also learned how to connect a Python application to a SQLite database so that user data persists when the application is restarted.

One of the most useful parts of the project was learning how the different parts of an application work together — the user interface, application logic, external API and database.

I encountered and debugged issues involving database IDs, session state, saving edited records and persistent data. Working through these problems helped me develop my debugging and problem-solving skills.

## 🔐 Security

The Google Books API key is stored locally using environment variables and is excluded from this repository using `.gitignore`.

## 🚀 Future Development

I would like to continue developing BookNest by adding features such as:

- User accounts
- Individual reading profiles
- Book cover images throughout the library
- Reading streaks and achievements
- Improved mobile layout
- Personal reading recommendations
- Deployment as a publicly accessible web application

---

*BookNest is an ongoing personal project created to develop and demonstrate my programming and Computer Science skills.*
