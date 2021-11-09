from django.test import TestCase, Client
from django.urls import reverse
from ecomapp.models import *

#Client are used to miamic to how client access your views and another way to do this requestfactory

#it will be good to create object in Individual function 

class TestViews(TestCase):
 # execute before any fuction 
    def setUp(self):
        #arrange
        self.client = Client()
        self.list_url =reverse('ecomapp:allproducts')
        self.detail_url =reverse("ecomapp:productdetail", kwargs={'slug':'product-1'})
        #create the object only for testing but doesnot refelct in our db, 
        self.category =Category.objects.create(title="new", slug="new-new")
        self.product =Product.objects.create(
     title='product1',
     slug='product-1',
     category=self.category,   
     image='products/jar.jpg',
     marked_price=100,
     selling_price=100,
     description="hello from test ",
     warranty="no warranty",
     return_policy="no return",
     view_count=12)


    def test_AllProductsView_GET(self):  
        #act
        response = self.client.get(self.list_url)
        #assert
        self.assertEquals(response.status_code, 200)
        # check the request made from client side is sucessfull or not if success then check whether it is redirecting to the template we specified or not
        self.assertTemplateUsed(response, 'allproducts.html')

    def test_ProductDetailView_GET(self):

        response =self.client.get(self.detail_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'productdetail.html')

# # for post request
# #create dummy objects here to use in this function
    # def test_ProductAddView_POST_add_new_product(self):
    #     response = self.client.post(self.detail_url,{
    #     'title':'product1',
    #     'slug':'product-1',
    #     'category':self.category,   
    #     'image':'products/jar.jpg',
    #     'marked_price':100,
    #     'selling_price':100,
    #     'description':"hello from test ",
    #     'warranty':"no warranty",
    #     'return_policy':"no return",
    #     'view_count':12})
    #     self.assertAlmostEquals(response.status_code, 302)
    #     #redirect is used after data is posted in db from forms ie. redirect's status code is 302
    #     self.assertEquals(self.category.product.first().title, 'product1')
#     # #the first or recent object in product table is reterived and compared with our newly created project

# #Post with no data
#     def test_ProductAddView_POST_no_data(self):
#         #create dummy objects here to use in this function
#         response = self.client.post(self.detail_url)
#         self.assertAlmostEquals(response.status_code, 302)
#         #redirect is used after data is posted in db from forms ie. redirect's status code is 302
#        #if form is posted with no data then no product will added so the no. of rows in product table is 0
#         self.assertEquals(self.category.product.count(), 0)
#         #the first or recent object in product table is reterived and compared with our newly created project


#     def test_ProductDeleteView_deletes_product(self):
#         #create dummy objects here to use in this function
#          response = self.client.delete(self.detail_url,json.dumps({'id':1}))
#         #A 204 ( No Content ) status code if the action has been enacted and no further information is to be supplied.
#          #if redirect is used the then status code of redirect is used 
#          self.assertEquals(response.status_code, 204)
#          self.assertEquals(self.category.product.count(),0)

#     def test_ProductDeleteView_deletes_product(self):
#         #create dummy objects here to use in this function
#          response = self.client.delete(self.detail_url,json.dumps({'id':1}))
#         #A 204 ( No Content ) status code if the action has been enacted and no further information is to be supplied.
#          #if redirect is used the then status code of redirect is used 
#          self.assertEquals(response.status_code, 404)
#          self.assertEquals(self.category.product.count(),1)


    # def test_product_create_POST(self):
    #     url = reverse("adminproductcreate")
    #     response =self.client.post(url,{'title':'product2',
    #   'slug':'product-2',
    #   'category':self.category,   
    #   'image':'products/jar.jpg',
    #   'marked_price':100,
    #   'selling_price':100,
    #   'description':"hello from test ",
    #  'warranty':"no warranty",
    #   'return_policy':"no return",
    #   'view_count':12})
    #     first_category = Category.objects.get(id=1)
    #     second_category = Category.objects.get(id=2)

    #     product2 = Product.objects.get(id=2)
    #     self.assertEquals(product2.name,'product2')
    #     self.assertEquals(first_category.procuct, product2)
    #     self.assertEquals(second_category.procuct, product2)
    #     self.assertEquals(first_category.title, "Electronics")
    #     self.assertEquals(second_category.title, "Shopping")

    # object create garne and tei obj retrieve garera check garne afule rakheko data match garera 
    # respone object get garne and get gareko object ko requect sucess vayeko ki nai check garne and tyo view/url le kata redirect garcha tyo template check garne


    # unit testing