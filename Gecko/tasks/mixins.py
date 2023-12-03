# mixins.py
from .models import Team

class TeamRequiredMixin:
    """Mixin to get the team from the request."""

    def dispatch(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')  # Adjust this based on your URL configuration
        self.team = Team.objects.get(pk=team_id)
        return super().dispatch(request, *args, **kwargs)