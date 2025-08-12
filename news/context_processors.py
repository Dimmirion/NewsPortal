from datetime import datetime

def theme_processor(request):
    hour = datetime.now().hour
    theme = 'dark' if 20 <= hour < 6 else 'light'
    return {'theme': theme}