from django.test import TestCase
from ecomapp.models import Category, Product




class TestModels(TestCase):
    def setUp(self):
        self.category =Category.objects.create(title="new", slug="new-new")
        self.product =Product.objects.create(
        title='product1',
        #when slugify is defined it is automatically assigned
        slug='product-1',
        category=self.category,   
        image='products/jar.jpg',
        marked_price=100,
        selling_price=100,
        description="hello from test ",
        warranty="no warranty",
        return_policy="no return",
        view_count=12)

#when slug is automatically assigned through title of product
    def test_product_is_assigned_slug_on_creation(self):
        self.assertEquals(self.product.slug,'product-1')

# create objects and test with our given data
    
# unit testing