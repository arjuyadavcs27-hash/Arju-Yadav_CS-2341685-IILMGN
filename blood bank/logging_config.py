import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Get log level from config
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    log_file = os.path.join('logs', f'app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=app.config['MAX_LOG_SIZE'],
        backupCount=app.config['LOG_BACKUP_COUNT']
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure SQLAlchemy logging
    if app.config.get('SQLALCHEMY_ECHO'):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Configure Flask logging
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    
    # Configure other loggers
    loggers = [
        'flask',
        'flask_jwt_extended',
        'flask_cors',
        'flask_mail',
        'twilio',
        'requests',
        'urllib3'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    # Log startup message
    app.logger.info('Application startup')
    
    return app.logger

def log_request_info():
    """Log request information."""
    from flask import request
    logger = logging.getLogger('request')
    
    logger.info(f"Request: {request.method} {request.path}")
    logger.info(f"IP: {request.remote_addr}")
    logger.info(f"User-Agent: {request.headers.get('User-Agent')}")
    logger.info(f"Referrer: {request.headers.get('Referer')}")
    logger.info(f"Content-Type: {request.headers.get('Content-Type')}")
    
    if request.method in ['POST', 'PUT']:
        logger.info(f"Request Data: {request.get_json(silent=True)}")

def log_error(error):
    """Log error information."""
    logger = logging.getLogger('error')
    logger.error(f"Error: {str(error)}", exc_info=True)

def log_security_event(event_type, details):
    """Log security-related events."""
    logger = logging.getLogger('security')
    logger.warning(f"Security Event: {event_type} - {details}")

def log_audit_event(user_id, action, details):
    """Log audit events."""
    logger = logging.getLogger('audit')
    logger.info(f"Audit Event - User: {user_id}, Action: {action}, Details: {details}")

def log_performance_metric(metric_name, value):
    """Log performance metrics."""
    logger = logging.getLogger('performance')
    logger.info(f"Performance Metric - {metric_name}: {value}")

def log_database_event(event_type, query, duration):
    """Log database events."""
    logger = logging.getLogger('database')
    logger.debug(f"Database Event - Type: {event_type}, Query: {query}, Duration: {duration}ms")

def log_email_event(recipient, subject, status):
    """Log email events."""
    logger = logging.getLogger('email')
    logger.info(f"Email Event - To: {recipient}, Subject: {subject}, Status: {status}")

def log_sms_event(recipient, message, status):
    """Log SMS events."""
    logger = logging.getLogger('sms')
    logger.info(f"SMS Event - To: {recipient}, Message: {message}, Status: {status}")

def log_api_event(endpoint, method, status_code, duration):
    """Log API events."""
    logger = logging.getLogger('api')
    logger.info(f"API Event - {method} {endpoint}, Status: {status_code}, Duration: {duration}ms") 