"""
Analytics Utility Functions for Polls Application
This module provides functions for analytics and data processing using PostgreSQL.
"""
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import inspect, text
from app import db

def log_vote_to_analytics(poll_id, option_id, user_ip, user_agent):
    """
    Log vote data for analytics.
    """
    try:
        dialect = db.engine.dialect.name
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS vote_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id VARCHAR(36) NOT NULL,
                option_id INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_ip VARCHAR(45),
                user_agent TEXT
            )
        """
        if dialect == "postgresql":
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS vote_analytics (
                    id SERIAL PRIMARY KEY,
                    poll_id VARCHAR(36) NOT NULL,
                    option_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    user_ip VARCHAR(45),
                    user_agent TEXT
                )
            """

        with db.engine.begin() as conn:
            conn.execute(text(create_table_sql))
            if dialect == "postgresql":
                result = conn.execute(text("""
                    INSERT INTO vote_analytics
                    (poll_id, option_id, timestamp, user_ip, user_agent)
                    VALUES (:poll_id, :option_id, :timestamp, :user_ip, :user_agent)
                    RETURNING id
                """), {
                    "poll_id": poll_id,
                    "option_id": option_id,
                    "timestamp": datetime.utcnow(),
                    "user_ip": user_ip,
                    "user_agent": user_agent
                })
                inserted_id = result.scalar_one()
            else:
                result = conn.execute(text("""
                    INSERT INTO vote_analytics
                    (poll_id, option_id, timestamp, user_ip, user_agent)
                    VALUES (:poll_id, :option_id, :timestamp, :user_ip, :user_agent)
                """), {
                    "poll_id": poll_id,
                    "option_id": option_id,
                    "timestamp": datetime.utcnow(),
                    "user_ip": user_ip,
                    "user_agent": user_agent
                })
                inserted_id = result.lastrowid

        current_app.logger.info(f"Vote logged to analytics table: {inserted_id}")
        return inserted_id
    except Exception as e:
        current_app.logger.error(f"Error logging vote to analytics: {e}")
        return None

def get_vote_analytics(poll_id):
    """
    Get analytics for a specific poll.
    """
    try:
        table_exists = inspect(db.engine).has_table("vote_analytics")
        if not table_exists:
            return {
                "hourly_votes": [],
                "browser_stats": [],
                "total_logged_votes": 0
            }

        dialect = db.engine.dialect.name
        hourly_votes_query = text("""
            SELECT
                DATE(timestamp) as date,
                EXTRACT(HOUR FROM timestamp) as hour,
                COUNT(*) as count
            FROM vote_analytics
            WHERE poll_id = :poll_id
            GROUP BY DATE(timestamp), EXTRACT(HOUR FROM timestamp)
            ORDER BY date, hour
        """)
        if dialect == "sqlite":
            hourly_votes_query = text("""
                SELECT
                    DATE(timestamp) as date,
                    CAST(STRFTIME('%H', timestamp) AS INTEGER) as hour,
                    COUNT(*) as count
                FROM vote_analytics
                WHERE poll_id = :poll_id
                GROUP BY DATE(timestamp), STRFTIME('%H', timestamp)
                ORDER BY date, hour
            """)

        with db.engine.connect() as conn:
            if not table_exists:
                return {
                    "hourly_votes": [],
                    "browser_stats": [],
                    "total_logged_votes": 0
                }

            hourly_votes_result = conn.execute(hourly_votes_query, {"poll_id": poll_id})
            hourly_votes = [
                {
                    "_id": {"date": str(row.date), "hour": int(row.hour)},
                    "count": row.count
                }
                for row in hourly_votes_result
            ]

            browser_stats_query = text("""
                SELECT
                    user_agent,
                    COUNT(*) as count
                FROM vote_analytics
                WHERE poll_id = :poll_id
                GROUP BY user_agent
                ORDER BY count DESC
            """)

            browser_stats_result = conn.execute(browser_stats_query, {"poll_id": poll_id})
            browser_stats = [
                {"_id": row.user_agent, "count": row.count}
                for row in browser_stats_result
            ]

            total_query = text("""
                SELECT COUNT(*) as total
                FROM vote_analytics
                WHERE poll_id = :poll_id
            """)

            total_result = conn.execute(total_query, {"poll_id": poll_id})
            total_logged_votes = total_result.scalar_one()

            return {
                "hourly_votes": hourly_votes,
                "browser_stats": browser_stats,
                "total_logged_votes": total_logged_votes
            }
    except Exception as e:
        current_app.logger.error(f"Error getting vote analytics: {e}")
        return {
            "hourly_votes": [],
            "browser_stats": [],
            "total_logged_votes": 0
        }

def archive_old_polls(days=30):
    """
    Mark polls as archived that are older than specified days
    """
    try:
        from models import Poll
        
        # Get polls older than the specified number of days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Check if we have an archived_polls table, if not create it
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS archived_polls (
                    id VARCHAR(36) PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    archived_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    poll_data JSONB NOT NULL
                )
            """))
            conn.commit()
        
        # Archive each old poll
        old_polls = Poll.query.filter(Poll.created_at < cutoff_date).all()
        archived_count = 0
        
        for poll in old_polls:
            # Convert the poll and its options to a dictionary
            poll_data = poll.to_dict()
            
            # Insert into archived_polls table
            with db.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO archived_polls 
                    (id, title, description, created_at, archived_at, poll_data)
                    VALUES 
                    (:id, :title, :description, :created_at, :archived_at, :poll_data)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    "id": poll.id,
                    "title": poll.title,
                    "description": poll.description,
                    "created_at": poll.created_at,
                    "archived_at": datetime.utcnow(),
                    "poll_data": db.engine.dialect.json_serializer(poll_data)
                })
                conn.commit()
                archived_count += 1
        
        current_app.logger.info(f"Archived {archived_count} old polls")
        return True
    except Exception as e:
        current_app.logger.error(f"Error archiving old polls: {e}")
        return False
