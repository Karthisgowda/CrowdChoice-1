import json
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import Poll, Option
import logging
from mongo_utils import log_vote_to_analytics, get_vote_analytics

@app.route('/')
def index():
    # Get 5 most recent polls for the homepage
    recent_polls = Poll.query.order_by(Poll.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_polls=recent_polls)

@app.route('/create', methods=['GET', 'POST'])
def create_poll():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        options = request.form.getlist('options')
        
        # Validate input
        if not title or len(options) < 2 or '' in options:
            flash('Please provide a title and at least two non-empty options.', 'danger')
            return render_template('create_poll.html', title=title, description=description, options=options)
        
        # Create new poll
        poll = Poll(title=title, description=description)
        db.session.add(poll)
        
        # Add options
        for option_text in options:
            option = Option(text=option_text, poll=poll)
            db.session.add(option)
        
        db.session.commit()
        flash('Poll created successfully!', 'success')
        
        # Redirect to the newly created poll
        return redirect(url_for('view_poll', poll_id=poll.id))
    
    return render_template('create_poll.html')

@app.route('/poll/<poll_id>')
def view_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    
    # Get user's previous votes from session
    user_votes = session.get('user_votes', {})
    has_voted = poll_id in user_votes
    
    # Get analytics data if available
    analytics = None
    try:
        analytics = get_vote_analytics(poll_id)
    except Exception as e:
        app.logger.error(f"Error fetching analytics: {e}")
    
    return render_template('view_poll.html', poll=poll, has_voted=has_voted, analytics=analytics)

@app.route('/api/poll/<poll_id>')
def get_poll_data(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    return jsonify(poll.to_dict())

@app.route('/api/vote', methods=['POST'])
def vote():
    data = request.get_json()
    
    if not data or 'poll_id' not in data or 'option_id' not in data:
        return jsonify({'success': False, 'message': 'Missing required data'}), 400
    
    poll_id = data['poll_id']
    option_id = data['option_id']
    
    # Get user's previous votes from session
    user_votes = session.get('user_votes', {})
    
    # Check if user has already voted on this poll
    if poll_id in user_votes:
        return jsonify({'success': False, 'message': 'You have already voted on this poll'}), 400
    
    # Find the option and increment votes
    option = Option.query.filter_by(id=option_id, poll_id=poll_id).first()
    
    if not option:
        return jsonify({'success': False, 'message': 'Invalid option or poll'}), 400
    
    option.votes += 1
    
    # Record the vote in the session
    user_votes[poll_id] = option_id
    session['user_votes'] = user_votes
    
    db.session.commit()
    
    # Log vote for analytics
    try:
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        log_vote_to_analytics(poll_id, option_id, user_ip, user_agent)
        app.logger.info(f"Vote logged to analytics for poll {poll_id}, option {option_id}")
    except Exception as e:
        app.logger.error(f"Error logging vote to analytics: {e}")
    
    # Return the updated poll data
    poll = Poll.query.get(poll_id)
    return jsonify({'success': True, 'poll': poll.to_dict()})

@app.route('/polls')
def all_polls():
    sort_by = request.args.get('sort', 'recent')
    
    if sort_by == 'popular':
        # This is a simple way to order by popularity - in a real app you might use more sophisticated methods
        polls = Poll.query.all()
        polls.sort(key=lambda p: sum(o.votes for o in p.options), reverse=True)
    else:  # sort by recent (default)
        polls = Poll.query.order_by(Poll.created_at.desc()).all()
    
    return render_template('all_polls.html', polls=polls, sort_by=sort_by)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error='Page not found'), 404

@app.route('/delete_poll/<poll_id>', methods=['POST'])
def delete_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    
    try:
        # Delete all options associated with the poll first
        for option in poll.options:
            db.session.delete(option)
        
        # Delete the poll
        db.session.delete(poll)
        db.session.commit()
        
        flash('Poll deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting poll: {e}")
        flash('Error deleting poll. Please try again.', 'danger')
    
    return redirect(url_for('all_polls'))

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {e}")
    return render_template('index.html', error='Server error. Please try again later.'), 500
