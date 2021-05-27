from django.contrib.auth.models import AbstractUser
from core.models import AbsModel


class User(AbsModel, AbstractUser):
    """Base user model"""

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "accounts_user"
        ordering = ["first_name"]

    def __str__(self):
        return self.username
