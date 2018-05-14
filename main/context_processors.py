from main.utils import GlobalSettings


def _globals(request):
    gs = GlobalSettings()
    values = {
        'title': gs.get('siteName'),
    }
    return {'global': values}
