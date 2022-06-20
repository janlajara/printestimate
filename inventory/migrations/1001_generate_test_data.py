from django.db import migrations
from inventory.models import Item, BaseStockUnit, AlternateStockUnit
from inventory.properties.models import PaperProperties


def create_items(apps, schema_editor):
    def _create_item(type, name, base_uom, alternate_uom, 
            override_price, **kwargs):
        item = Item.objects.create_item(type=type, name=name, 
            base_uom=base_uom, alternate_uom=alternate_uom,
            override_price=override_price)
        item.properties.width_value = 32
        item.properties.length_value = 28
        item.properties.size_uom = 'inch'
        item.properties.save()
    
    sheet_uom = BaseStockUnit.objects.get(name='Sheet')
    ream_uom = AlternateStockUnit.objects.get(name='Ream')

    _create_item(type=Item.PAPER, name='Carbonless White', 
        base_uom=sheet_uom, alternate_uom=ream_uom, override_price=2.5)
    _create_item(type=Item.PAPER, name='Carbonless Yellow', 
        base_uom=sheet_uom, alternate_uom=ream_uom, override_price=2.5)
    _create_item(type=Item.PAPER, name='Carbonless Blue', 
        base_uom=sheet_uom, alternate_uom=ream_uom, override_price=2.5)
    
    kraft_item = Item.objects.create_item(type=Item.PAPER, name='Kraft #80', 
        base_uom=sheet_uom, override_price=4)
    kraft_item.properties.width_value = 34
    kraft_item.properties.length_value = 24
    kraft_item.properties.size_uom = 'inch'
    kraft_item.properties.save()


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('inventory', '1000_populate_uoms'),
    ]

    operations = [
        migrations.RunPython(create_items, reverse_code=migrations.RunPython.noop)
    ]
