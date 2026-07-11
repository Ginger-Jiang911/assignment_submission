from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, student_id, name, password=None, **extra_fields):
        if not student_id:
            raise ValueError("学号不能为空")
        if not name:
            raise ValueError("姓名不能为空")
        user = self.model(student_id=student_id, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)
        return self.create_user(student_id, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    student_id = models.CharField("学号", max_length=32, unique=True, db_index=True)
    name = models.CharField("姓名", max_length=64)
    is_active = models.BooleanField("激活", default=True)
    is_staff = models.BooleanField("管理员权限", default=False)
    is_admin = models.BooleanField("超级管理员", default=False)
    created_at = models.DateTimeField("注册时间", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "student_id"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student_id} {self.name}"