import pytest
import os
from datetime import timedelta
from config import Config, DevelopmentConfig, TestingConfig, ProductionConfig, get_config

def test_base_config():
    """Test base configuration settings."""
    config = Config()
    
    # Test secret keys
    assert config.SECRET_KEY == os.getenv('SECRET_KEY', 'your-secret-key')
    assert config.JWT_SECRET_KEY == os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    
    # Test JWT settings
    assert config.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=1)
    assert config.JWT_REFRESH_TOKEN_EXPIRES == timedelta(days=7)
    assert config.JWT_BLACKLIST_ENABLED == True
    assert config.JWT_BLACKLIST_TOKEN_CHECKS == ['access', 'refresh']
    
    # Test database settings
    assert config.SQLALCHEMY_DATABASE_URI == os.getenv('DATABASE_URL', 'mysql://root:@localhost/blood_bank')
    assert config.SQLALCHEMY_TRACK_MODIFICATIONS == False
    
    # Test email settings
    assert config.MAIL_SERVER == os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    assert config.MAIL_PORT == int(os.getenv('MAIL_PORT', 587))
    assert config.MAIL_USE_TLS == True
    
    # Test security settings
    assert config.PASSWORD_RESET_TIMEOUT == 3600
    assert config.MAX_LOGIN_ATTEMPTS == 5
    assert config.ACCOUNT_LOCK_DURATION == 1800
    assert config.SESSION_TIMEOUT == 3600
    
    # Test file upload settings
    assert config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
    assert config.UPLOAD_FOLDER == 'uploads'
    assert config.ALLOWED_EXTENSIONS == {'pdf', 'jpg', 'jpeg', 'png'}
    
    # Test rate limiting
    assert config.RATELIMIT_DEFAULT == "100/hour"
    assert config.RATELIMIT_STORAGE_URL == "memory://"
    
    # Test CORS settings
    assert 'http://localhost:3000' in config.CORS_ORIGINS
    assert 'http://localhost:5000' in config.CORS_ORIGINS
    assert 'https://lifeflow.in' in config.CORS_ORIGINS
    
    # Test logging settings
    assert config.LOG_LEVEL == 'INFO'
    assert config.LOG_FILE == 'app.log'
    assert config.MAX_LOG_SIZE == 10 * 1024 * 1024
    assert config.LOG_BACKUP_COUNT == 5

def test_development_config():
    """Test development configuration settings."""
    config = DevelopmentConfig()
    
    assert config.DEBUG == True
    assert config.SQLALCHEMY_ECHO == True
    assert config.LOG_LEVEL == 'DEBUG'

def test_testing_config():
    """Test testing configuration settings."""
    config = TestingConfig()
    
    assert config.TESTING == True
    assert config.SQLALCHEMY_DATABASE_URI == 'mysql://root:@localhost/blood_bank_test'
    assert config.WTF_CSRF_ENABLED == False
    assert config.LOG_LEVEL == 'DEBUG'

def test_production_config():
    """Test production configuration settings."""
    config = ProductionConfig()
    
    assert config.DEBUG == False
    assert config.TESTING == False
    assert config.LOG_LEVEL == 'WARNING'
    
    # Test security settings
    assert config.SESSION_COOKIE_SECURE == True
    assert config.REMEMBER_COOKIE_SECURE == True
    assert config.SESSION_COOKIE_HTTPONLY == True
    assert config.REMEMBER_COOKIE_HTTPONLY == True
    assert config.SSL_REDIRECT == True
    
    # Test security headers
    assert 'Strict-Transport-Security' in config.SECURITY_HEADERS
    assert 'X-Content-Type-Options' in config.SECURITY_HEADERS
    assert 'X-Frame-Options' in config.SECURITY_HEADERS
    assert 'X-XSS-Protection' in config.SECURITY_HEADERS
    assert 'Content-Security-Policy' in config.SECURITY_HEADERS

def test_get_config():
    """Test configuration selection based on environment."""
    # Test default configuration
    os.environ.pop('FLASK_ENV', None)
    config = get_config()
    assert isinstance(config, DevelopmentConfig)
    
    # Test development configuration
    os.environ['FLASK_ENV'] = 'development'
    config = get_config()
    assert isinstance(config, DevelopmentConfig)
    
    # Test testing configuration
    os.environ['FLASK_ENV'] = 'testing'
    config = get_config()
    assert isinstance(config, TestingConfig)
    
    # Test production configuration
    os.environ['FLASK_ENV'] = 'production'
    config = get_config()
    assert isinstance(config, ProductionConfig)
    
    # Test invalid environment
    os.environ['FLASK_ENV'] = 'invalid'
    config = get_config()
    assert isinstance(config, DevelopmentConfig)  # Should fall back to default

def test_config_override():
    """Test configuration override through environment variables."""
    # Test database URL override
    os.environ['DATABASE_URL'] = 'mysql://user:pass@localhost/test_db'
    config = Config()
    assert config.SQLALCHEMY_DATABASE_URI == 'mysql://user:pass@localhost/test_db'
    
    # Test mail settings override
    os.environ['MAIL_SERVER'] = 'smtp.example.com'
    os.environ['MAIL_PORT'] = '587'
    config = Config()
    assert config.MAIL_SERVER == 'smtp.example.com'
    assert config.MAIL_PORT == 587
    
    # Test JWT settings override
    os.environ['JWT_SECRET_KEY'] = 'custom-secret-key'
    config = Config()
    assert config.JWT_SECRET_KEY == 'custom-secret-key'
    
    # Clean up environment variables
    os.environ.pop('DATABASE_URL', None)
    os.environ.pop('MAIL_SERVER', None)
    os.environ.pop('MAIL_PORT', None)
    os.environ.pop('JWT_SECRET_KEY', None) 