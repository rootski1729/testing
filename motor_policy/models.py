from typing import Required
from django.db import models
from core.models import ModuleModel
from motor_quote.enums import Insurer,Product,ProductType,ProductSubType,ProductCategory,PolicyCategory,PolicyType
from django.contrib.postgres.fields import ArrayField

class MotorPolicy(ModuleModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    mongo_id = models.CharField(max_length=24, unique=True)
    insurer = models.CharField(max_length=50, choices=Insurer.choices(), null=True, blank=True)
    product = models.CharField(max_length=50, choices=Product.choices(), null=True, blank=True)
    product_type = models.CharField(max_length=50, choices=ProductType.choices(), null=True, blank=True)
    product_sub_type = models.CharField(max_length=50, choices=ProductSubType.choices(), null=True, blank=True)
    product_category = models.CharField(max_length=50, choices=ProductCategory.choices(), null=True, blank=True)
    policy_category = models.CharField(max_length=50, choices=PolicyCategory.choices(), null=True, blank=True)
    policy_type = models.CharField(max_length=50, choices=PolicyType.choices(), null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)