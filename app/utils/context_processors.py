from datetime import datetime

def inject_now():
    """Inject current datetime into templates"""
    return {'now': datetime.utcnow()}
