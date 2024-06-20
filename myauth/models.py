from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.hashers import make_password
from shortuuidfield import ShortUUIDField

# Create your models here.


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("Username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


# 重写User模型
class UserStatusChoices(models.IntegerChoices):
    ACTIVATED = 1
    UNACTIVATED = 2
    LOCKED = 3


class OAUser(AbstractBaseUser, PermissionsMixin):
    """
    自定义的User模型
    """

    uid = ShortUUIDField(primary_key=True)
    username = models.CharField(
        max_length=150,
        unique=False,
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, blank=False)
    telephone = models.CharField(max_length=20, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    status = models.IntegerField(
        choices=UserStatusChoices, default=UserStatusChoices.ACTIVATED
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    department = models.ForeignKey(
        "OADepartment",
        null=True,
        on_delete=models.SET_NULL,
        related_name="staffs",
        related_query_name="staffs",
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"  # 鉴权字段 在authenticate 的username参数中 传给USERNAME_FIELD 传给指定字段
    REQUIRED_FIELDS = ["username", "password"]  # 指定那些字段必填,但是不能重复

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name


class OADepartment(models.Model):
    name = models.CharField(max_length=100)
    intro = models.CharField(max_length=200)
    # leader 一对一
    leader = models.OneToOneField(
        OAUser,
        null=True,
        on_delete=models.SET_NULL,
        related_name="leader_department",
        related_query_name="leader_department",
    )
    # manager 一对多
    manager = models.ForeignKey(
        OAUser,
        null=True,
        on_delete=models.SET_NULL,
        related_name="manager_departments",
        related_query_name="manager_departments",
    )
