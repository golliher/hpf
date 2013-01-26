from django.db import models

# Create your models here.
# -*- coding: utf-8 -*-

class Document(models.Model):
    docfile = models.FileField(upload_to='uploads/')