import enum
from django.core.management.base import BaseCommand
from products.models import Product, ProductApplication, ProductMaterial, ProductStyle
from products import enums

class Command(BaseCommand):
    help = 'Converts many to many models to new structure'

    def handle(self, *args, **options):
        
        products = Product.objects.filter(id=120)

        for product in products:
            materials = []
            applications = []
            styles = []

            for material in product.materials.all():
                if material.name == 'Keramikk':
                    materials.append(enums.ProductMaterials.CERAMIC)
                if material.name == 'Metall':
                    materials.append(enums.ProductMaterials.METAL)
                if material.name == 'Porselen':
                    materials.append(enums.ProductMaterials.PORCELAIN)
                if material.name == 'Tre':
                    materials.append(enums.ProductMaterials.WOOD)

            for application in product.applications.all():
                if application.name == 'Bord':
                    applications.append(enums.ProductApplications.TABLE)
                if application.name == 'Gulv':
                    applications.append(enums.ProductApplications.FLOOR)
                if application.name == 'Tak':
                    applications.append(enums.ProductApplications.CEILING)
                if application.name == 'Vask':
                    applications.append(enums.ProductApplications.SINK)
                if application.name == 'Vegger':
                    applications.append(enums.ProductApplications.WALLS)

            for style in product.styles.all():
                if style.name == 'Betong':
                    styles.append(enums.ProductStyles.CONCRETE)
                if style.name == 'Klassisk':
                    styles.append(enums.ProductStyles.CLASSIC)
                if style.name == 'Lux':
                    styles.append(enums.ProductStyles.LUXURIOUS)
                if style.name == 'Marmor':
                    styles.append(enums.ProductStyles.MARBLE)
                if style.name == 'Naturlig':
                    styles.append(enums.ProductStyles.NATURAL)
                if style.name == 'Skandinavisk':
                    styles.append(enums.ProductStyles.SCANDINAVIAN)
                if style.name == 'Strukturert':
                    styles.append(enums.ProductStyles.STRUCTURED)

            product.temp_materials = materials
            product.temp_applications = applications
            product.temp_styles = styles
            product.save()




