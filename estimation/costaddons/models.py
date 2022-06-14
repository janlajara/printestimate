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

    def add_option(self, value, label):
        option = ConfigCostAddonOption.objects.create(
            config_cost_addon=self, value=value, label=label)
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
    class AddonCostSet:
        def __init__(self, order_quantity, addon_costs):
            self.order_quantity = order_quantity
            self.addon_costs = addon_costs

    product_estimate = models.OneToOneField(ProductEstimate, on_delete=models.CASCADE,
        related_name='estimate_addon_set')

    def add_addon_item(self, name, sequence, type, value, allow_custom_value=False, 
            config_cost_addon=None):
        addon_item = EstimateAddonItem.objects.create(
            name=name, sequence=sequence,
            type=type, value=value, 
            allow_custom_value=allow_custom_value, 
            config_cost_addon=config_cost_addon,
            estimate_addon_set=self)
        return addon_item

    def get_addon_cost_set(self, order_quantity, initial_value):
        addon_costs = self.get_addon_costs(initial_value)
        return EstimateAddonSet.AddonCostSet(order_quantity, addon_costs)

    def get_addon_costs(self, initial_value):
        addon_costs = []
        total_cost = initial_value
        for addon_item in self.estimate_addon_items.all().order_by('sequence'):
            addon_cost = EstimateAddonItem.AddonCost(
                addon_item.id, addon_item.name,
                addon_item.sequence, addon_item.type,
                total_cost, addon_item.value)
            addon_costs.append(addon_cost)
            total_cost += addon_cost.addon_cost
        
        return addon_costs


class EstimateAddonItem(models.Model):
    class AddonCost:
        def __init__(self, id, name, sequence, type, initial_value, addon_value):
            self.id = id
            self.name = name
            self.sequence = sequence
            self.type = type
            self.initial_value = initial_value
            self.addon_value = addon_value

        @property
        def addon_cost(self):
            addon_cost = (self.addon_value 
                if self.type == ConfigCostAddon.FLAT 
                else self.initial_value * (self.addon_value / 100))
            return addon_cost


    name = models.CharField(max_length=40)
    sequence = models.IntegerField()
    type = models.CharField(max_length=10, choices=ConfigCostAddon.TYPES)
    value = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    estimate_addon_set = models.ForeignKey(EstimateAddonSet, on_delete=models.CASCADE,
        related_name='estimate_addon_items')
    config_cost_addon = models.ForeignKey(ConfigCostAddon, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='estimate_addon_items')
    allow_custom_value = models.BooleanField(default=False)

    @property
    def options(self):
        if self.config_cost_addon is not None:
            return self.config_cost_addon.config_cost_addon_options.all()