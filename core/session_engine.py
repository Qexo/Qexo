def get_session_engine(is_vercel):
    if is_vercel:
        return 'django.contrib.sessions.backends.signed_cookies'
    return 'django.contrib.sessions.backends.db'
