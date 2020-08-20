from django.db import models
from ..process.models import Process
from ...inventory.models import Item


class Estimator:
    """
    input = models.JSONField(default={})
    output = models.JSONField(default={})


    def add_input(self, key, value):
        self.input.update({key: value})

    def add_output(self, key, value):
        self.output.update({key: value})
    """

    @classmethod
    def estimate(cls, material, process):
        pass


class RawMaterial(models.Model):
    item = models.OneToOneField(Item, on_delete=models.RESTRICT)
    processes = models.ManyToManyField(Process)


