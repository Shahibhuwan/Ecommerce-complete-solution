# from django.test import SimpleTestCase
# from ecomapp.forms import CustomerRegistrationForm

# class TestForms(SimpleTestCase):

#     def test_customerregistration_formvalid_data(self):
#         form= CustomerRegistrationForm(
#             data={
#                 'username':'Bhuwan'
#                 'password':'Shahi12'
#                 'email':'shahi@gmail.com'
#             }
#         )

#         self.assertTrue(form.is_valid())

#     def test_customerregistration_no_data(self):
#         form = CustomerRegistrationForm(data={})

#         self.assertFalse(form.is_valid())
#         self.assertEquals(len(form.errors), number of fields)


# unit testing