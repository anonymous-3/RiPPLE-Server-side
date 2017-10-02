# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Question, Topic
admin.site.register(Question)
admin.site.register(Topic)
