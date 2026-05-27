from django.db import models
from django.contrib.auth.models import User

class StartupIdea(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )

    idea = models.TextField()

    result = models.CharField(max_length=100)

    score = models.FloatField()

    demand = models.IntegerField()

    competition = models.IntegerField()

    feasibility = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.idea