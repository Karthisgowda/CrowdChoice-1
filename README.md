# Crowdsourced Decision Maker

A Flask-based web application for creating and voting on decision polls with real-time updates and analytics.

## Features

- Create polls with multiple options
- Real-time voting with automatic result updates
- Analytics tracking with charts and statistics
- Social media sharing (Facebook, Twitter, LinkedIn, Instagram)
- Poll deletion functionality
- Responsive design with black and white theme
- Animated background elements

## Deployment on Render

### Prerequisites
1. A Render account (sign up at [render.com](https://render.com))
2. This project repository on GitHub, GitLab, or Bitbucket

### Step-by-Step Deployment

1. **Connect Your Repository**
   - Log into your Render dashboard
   - Click "New +" and select "Web Service"
   - Connect your Git repository containing this project

2. **Configure Build Settings**
   - Build Command: `./build.sh` (or leave empty to use automatic detection)
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload main:app`
   - Environment: `Python 3`

3. **Add Environment Variables**
   - `SESSION_SECRET`: Generate a random secret key (Render can auto-generate this)
   - `DATABASE_URL`: Will be automatically set when you add a PostgreSQL database

4. **Add PostgreSQL Database**
   - In your Render dashboard, click "New +" and select "PostgreSQL"
   - Name it `postgres-db` or similar
   - Once created, copy the External Database URL
   - Add it as `DATABASE_URL` environment variable in your web service

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Your app will be available at `https://your-app-name.onrender.com`

### Alternative: Using render.yaml (Infrastructure as Code)

This project includes a `render.yaml` file for automatic deployment:

1. In your Render dashboard, go to "Blueprint" and click "New Blueprint Instance"
2. Connect your repository
3. Render will automatically create the web service and database based on the `render.yaml` configuration

## Local Development (XAMPP)

### Prerequisites
- XAMPP with Apache and MySQL
- Python 3.8 or newer
- Git

### Setup Instructions

1. **Install XAMPP**
   - Download from [apachefriends.org](https://www.apachefriends.org/)
   - Start Apache and MySQL services

2. **Create MySQL Database**
   - Open phpMyAdmin (click "Admin" next to MySQL in XAMPP)
   - Create a new database named `polls_db`

3. **Install Python Dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-wtf email-validator pymysql
   ```

4. **Configure Database**
   - The app will automatically use MySQL for local development
   - Default connection: `mysql+pymysql://root:@localhost/polls_db`
   - If you have a MySQL password, update the connection string in `app.py`

5. **Initialize Database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created!')"
   ```

6. **Run the Application**
   ```bash
   python main.py
   ```
   - Access the app at `http://localhost:5000`

## Usage

1. **Create a Poll**
   - Click "Create New Poll" on the homepage
   - Add a title, description, and at least 2 options
   - Submit to create your poll

2. **Vote on Polls**
   - Select an option and click "Submit Vote"
   - Results update automatically in real-time
   - Each browser session can vote once per poll

3. **Share Polls**
   - Use the social sharing buttons
   - Copy the poll URL to share directly

4. **Delete Polls**
   - Click the "Delete Poll" button on poll pages or in the polls list
   - Confirm the deletion (this action cannot be undone)

5. **View Analytics**
   - Analytics appear after voting on a poll
   - Shows voting activity over time and voter device information

## Technical Details

- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (Render) or MySQL (local XAMPP)
- **Frontend**: Bootstrap 5 with custom CSS animations
- **Real-time Updates**: JavaScript with periodic polling
- **Charts**: Chart.js for analytics visualization

## File Structure

```
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── routes.py           # URL routes and handlers
├── models.py           # Database models
├── mongo_utils.py      # Analytics utilities
├── templates/          # HTML templates
├── static/            # CSS, JavaScript, and assets
├── render.yaml        # Render deployment configuration
├── build.sh           # Build script for Render
├── Procfile           # Process file for deployment
└── README.md          # This file
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure your DATABASE_URL is correctly set
   - For local development, make sure MySQL is running in XAMPP

2. **Port Conflicts**
   - Change the port in `main.py` if 5000 is already in use
   - Use `app.run(host="0.0.0.0", port=8080, debug=True)`

3. **Missing Dependencies**
   - Run `pip install -r pyproject.toml` to install all required packages

4. **Build Failures on Render**
   - Check the build logs in your Render dashboard
   - Ensure all environment variables are properly set

## License

This project is open source and available under the MIT License.