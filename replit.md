# Crowdsourced Decision Maker - Project Documentation

## Project Overview
A Flask-based web application for creating and voting on decision polls with real-time updates, analytics tracking, and social media sharing capabilities. Features a black and white theme with animated background elements.

## Recent Changes (July 22, 2025)
- ✓ Fixed database configuration to support both PostgreSQL (Render) and MySQL (XAMPP)
- ✓ Added poll deletion functionality with confirmation dialogs
- ✓ Created comprehensive Render deployment configuration files
- ✓ Updated templates with delete buttons for polls
- ✓ Created detailed README.md with deployment instructions
- ✓ Added build script and Procfile for Render deployment

## Project Architecture
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (production) or MySQL (local development)
- **Frontend**: Bootstrap 5 with custom CSS animations
- **Real-time Updates**: JavaScript with periodic polling
- **Analytics**: PostgreSQL-based vote tracking with Chart.js visualization
- **Deployment**: Configured for Render.com with automatic PostgreSQL setup

## User Preferences
- Black and white theme with animations and graphic elements
- Social media sharing capabilities (Facebook, LinkedIn, Twitter, Instagram)
- Real-time vote updates without page refresh
- Analytics tracking with visual charts
- Poll deletion functionality with confirmation

## Features Implemented
1. Poll creation with multiple options
2. Real-time voting with session-based duplicate prevention
3. Analytics tracking with charts and device statistics
4. Social media sharing buttons
5. Poll deletion with confirmation dialogs
6. Responsive design with animated backgrounds
7. Both individual poll and all polls view with delete functionality

## Technical Details
- Uses Flask-SQLAlchemy for database operations
- Session-based voting to prevent duplicates
- PostgreSQL analytics for vote tracking
- Bootstrap CSS framework with custom animations
- Chart.js for data visualization
- Gunicorn WSGI server for production deployment

## Deployment Files Created
- `render.yaml`: Infrastructure as Code for Render deployment
- `build.sh`: Build script for database initialization
- `Procfile`: Process configuration for web server
- `README.md`: Comprehensive setup and deployment guide

## File Structure
```
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── routes.py           # URL routes and handlers
├── models.py           # Database models
├── mongo_utils.py      # Analytics utilities
├── templates/          # HTML templates with delete functionality
├── static/            # CSS, JavaScript, and assets
├── render.yaml        # Render deployment configuration
├── build.sh           # Build script for Render
├── Procfile           # Process file for deployment
└── README.md          # Setup and deployment guide
```

## Known Issues
- Database connection temporarily failing (credential issue)
- Some LSP diagnostics present but not affecting functionality

## Next Steps
- Deploy to Render using provided configuration files
- Test poll deletion functionality
- Verify analytics tracking on production deployment