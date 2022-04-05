from django.db import models
from estimation.product.models import ProductEstimate


class ConfigCostAddon(models.Model):
    PERCENTAGE = 'percentage'
    FLAT = 'flat'
    TYPES = [
        (PERCENTAGE, 'Percentage'),
        (FLAT, 'Flat')
    ]
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=10, choices=TYPES)
    allow_custom_value = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)

    @property
    def symbol(self):
        return '%' if self.type == ConfigCostAddon.PERCENTAGE else 'PHP'

    @property
    def has_options(self):
        return len(self.config_cost_addon_options.all()) > 0

    def add_option(self, value, label, is_required=False):
        option = ConfigCostAddonOption.objects.create(
            config_cost_addon=self, value=value, label=label, is_required=is_required)
        return option


class ConfigCostAddonOption(models.Model):
    value = models.DecimalField(decimal_places=2, max_digits=8)
    label = models.CharField(max_length=40)
    config_cost_addon = models.ForeignKey(ConfigCostAddon, on_delete=models.CASCADE,
        related_name='config_cost_addon_options')

    @property
    def formatted_value(self):
        return '%s %s' % (self.value, self.config_cost_addon.symbol)


class TemplateCostAddonSet(models.Model):
    name = models.CharField(max_length=40)
    is_default = models.BooleanField(default=False)

    @property
    def next_sequence(self):
        current_size = len(self.template_cost_addon_items.all())
        next_sequence = current_size + 1
        return next_sequence

    def set_default(self):
        results = (TemplateCostAddonSet.objects
            .filter(is_default=True)
            .update(is_default=False))
        self.is_default = True
        self.save()

    def add_item(self, config_cost_addon, sequence=None):
        if sequence is None:
            sequence = self.next_sequence

        return TemplateCostAddonItem.objects.create(template_cost_addon_set=self,
            sequence=sequence, config_cost_addon=config_cost_addon)


class TemplateCostAddonItem(models.Model):
    sequence = models.IntegerField()
    template_cost_addon_set = models.ForeignKey(TemplateCostAddonSet, 
        on_delete=models.CASCADE, related_name='template_cost_addon_items')
    config_cost_addon = models.ForeignKey(ConfigCostAddon, on_delete=models.CASCADE)


class EstimateAddonSet(models.Model):
    product_estimate = models.OneToOneField(ProductEstimate, on_delete=models.CASCADE,
        related_name='estimate_addon_set')


class EstimateAddonItem(models.Model):
    name = models.CharField(max_length=40)
    sequence = models.IntegerField()
    type = models.CharField(max_length=10, choices=ConfigCostAddon.TYPES)
    value = models.DecimalField(decimal_places=2, max_digits=8)
    estimate_addon_set = models.ForeignKey(EstimateAddonSet, on_delete=models.CASCADE,
        related_name='estimate_addon_items')
    config_cost_addon = models.ManyToManyField(ConfigCostAddon, blank=True)

    @property
    def allow_custom_value(self):
        return self.config_cost_addon.allow_custom_value

    @property
    def options(self):
        return self.config_cost_addon.config_cost_addon_options.all()

