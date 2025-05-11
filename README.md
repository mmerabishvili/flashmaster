# FlashMaster

**FlashMaster** is a flashcard-based study web app designed to improve memory retention and help users track their learning progress over time. Built with Flask and PostgreSQL, it allows users to create and organize flashcards by topic, study them interactively in two modes, and track their performance. It’s simple, personal, and effective for academic use or self-study.

---

## Features

- User authentication (sign up / login / logout) with secure password hashing  
- Topic and flashcard creation & management  
- Two study modes: **Practice** and **Tracked** (interactive card flipping)  
- Track correct and incorrect answers to monitor performance  
- Study session history and comparison  
- Profile page to change password or delete account  
- Admin panel for privileged users  
- Clean, responsive UI using Bootstrap  
- Fully containerized with Docker for easy deployment  

---

## Technologies Used

- **Python 3.12.3** — Main programming language  
- **Flask** — Web framework for routing, templating, and backend logic  
- **PostgreSQL** — Relational database for storing users, flashcards, and history  
- **SQLAlchemy ORM** — Database abstraction and relationship management  
- **Flask-Login** — User session and authentication management  
- **Jinja2** — HTML templating engine  
- **HTML, CSS, Bootstrap 5** — Frontend structure and styling  
- **Docker & Docker Compose** — Containerized setup  
- **python-dotenv** — Load environment variables from `.env`  
- **Vanilla JavaScript** — For card flipping and simple interactions  

---

## Limitations

- **Timezone Note**:  
  Study session timestamps are currently displayed in the local timezone (Asia/Tbilisi).  

---

## Project Structure

```
flashmaster/
│
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── models.py          # SQLAlchemy models
│   ├── routes.py          # Main routes and views
│   ├── templates/         # Jinja2 HTML templates
│   └── static/            # CSS and static assets
│
├── run.py                 # Entry point to run the Flask app
├── .dockerignore          # Files to exclude from Docker image
├── Dockerfile             # Flask container definition
├── docker-compose.yml     # Web + DB container setup
├── requirements.txt       # Python dependencies
├── .env.example           # Sample environment config
└── README.md
```

---

## Setup Instructions (with Docker)
1. **Clone the repo**  

```
git clone https://github.com/mmerabishvili/flashmaster.git
cd flashmaster
```

### 2. Set Up Environment Variables

Copy the example env file and fill in your own values:

```
cp .env.example .env
```

Edit `.env` and fill in:

```
# Flask settings
SECRET_KEY=your-secret-key
FLASK_ENV=development

# PostgreSQL settings (used by both the app and the db container)
POSTGRES_DB=your-db-name
POSTGRES_USER=your-db-username
POSTGRES_PASSWORD=your-db-password

# App-specific DB config
DB_NAME=your-db-name
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

# SQLAlchemy connection URI used by Flask
DATABASE_URL=postgresql://your-db-username:your-db-password@db:5432/your-db-name
```

 `POSTGRES_*` variables are used by the PostgreSQL Docker container.
-`DB_*` and `DATABASE_URL` are used by the Flask app to connect to the database.
Make sure `DB_USER` and `DB_PASSWORD` match `POSTGRES_USER` and `POSTGRES_PASSWORD`.


### 3. Build and Start the Containers

```
docker-compose up --build
```

### 4. Open the App in Your Browser

Visit [http://localhost:5000](http://localhost:5000)

> If you're using a terminal or an IDE like VS Code, the `http://127.0.0.1:5000` link shown in the logs may be clickable - feel free to use that directly to access the app.

---

## How to Use the App

1. **Register a new account** or log in with an existing one  
2. **Create topics** to organize flashcards  
3. **Add flashcards** with a question and answer under each topic  
4. **Study flashcards** using:  
   - **Practice Mode** — Flip cards freely (progress not saved)  
   - **Tracked Mode** — Mark correct/incorrect and track your results  
5. **View progress** after each session and compare with your history  
6. **Check progress history** by topic  
7. Use the **Profile page** to:  
   - Change password  
   - Permanently delete your account  
8. If you're an admin, access the **Admin Panel** to manage users and content  
   *(To test this, manually set `is_admin = True` for your user in the database.)*

---