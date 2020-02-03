from django.db import models


class Payment(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.TextField()

    def __str__(self):
        return self.type
