"""
MongoDB Utility Functions for Polls Application
This module provides functions to interact with MongoDB for analytics and data processing.
"""
from datetime import datetime
from flask import current_app
from bson.objectid import ObjectId

def get_mongo_db():
    """
    Get the MongoDB database connection if available
    """
    if current_app.config.get('MONGODB_CONNECTED', False):
        from app import mongo_db
        return mongo_db
    return None

def log_vote_to_mongodb(poll_id, option_id, user_ip, user_agent):
    """
    Log vote data to MongoDB for analytics
    """
    db = get_mongo_db()
    if not db:
        current_app.logger.warning("MongoDB not connected. Vote analytics not logged.")
        return None
    
    try:
        vote_data = {
            "poll_id": poll_id,
            "option_id": option_id,
            "timestamp": datetime.utcnow(),
            "user_ip": user_ip,
            "user_agent": user_agent
        }
        
        result = db.vote_logs.insert_one(vote_data)
        current_app.logger.info(f"Vote logged to MongoDB: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        current_app.logger.error(f"Error logging vote to MongoDB: {e}")
        return None

def get_vote_analytics(poll_id):
    """
    Get analytics for a specific poll
    """
    db = get_mongo_db()
    if not db:
        current_app.logger.warning("MongoDB not connected. Analytics not available.")
        return None
    
    try:
        # Get vote count by hour
        pipeline = [
            {"$match": {"poll_id": poll_id}},
            {"$project": {
                "hour": {"$hour": "$timestamp"},
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
            }},
            {"$group": {
                "_id": {"date": "$date", "hour": "$hour"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1, "_id.hour": 1}}
        ]
        
        hourly_votes = list(db.vote_logs.aggregate(pipeline))
        
        # Get vote count by user agent (browser type)
        browser_pipeline = [
            {"$match": {"poll_id": poll_id}},
            {"$group": {
                "_id": "$user_agent",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        browser_stats = list(db.vote_logs.aggregate(browser_pipeline))
        
        return {
            "hourly_votes": hourly_votes,
            "browser_stats": browser_stats,
            "total_logged_votes": db.vote_logs.count_documents({"poll_id": poll_id})
        }
    except Exception as e:
        current_app.logger.error(f"Error getting vote analytics from MongoDB: {e}")
        return None

def archive_old_polls(days=30):
    """
    Archive polls older than specified days
    """
    db = get_mongo_db()
    if not db:
        current_app.logger.warning("MongoDB not connected. Archiving not available.")
        return False
    
    try:
        from models import Poll
        from app import db as sql_db
        import datetime
        
        # Get polls older than the specified number of days
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        old_polls = Poll.query.filter(Poll.created_at < cutoff_date).all()
        
        # Archive each poll to MongoDB
        archived_count = 0
        for poll in old_polls:
            # Convert the poll and its options to a dictionary
            poll_data = poll.to_dict()
            poll_data['archived_at'] = datetime.datetime.utcnow()
            
            # Insert into MongoDB archive collection
            result = db.archived_polls.insert_one(poll_data)
            if result.inserted_id:
                archived_count += 1
        
        current_app.logger.info(f"Archived {archived_count} old polls to MongoDB")
        return True
    except Exception as e:
        current_app.logger.error(f"Error archiving old polls to MongoDB: {e}")
        return False