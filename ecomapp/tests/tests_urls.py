

from django.urls.base import resolve, reverse
from ecomapp.views import ContactView, ProductDetailView, render_pdf_view
from django.test import SimpleTestCase

class TestUrls(SimpleTestCase):

    def test_contact_resolves(self):
        url = reverse("ecomapp:contact")
        self.assertEquals(resolve(url).func.view_class,ContactView )
        

    def test_rendertopdf_resolves(self):
        url = reverse("ecomapp:rendertopdf")
        self.assertEquals(resolve(url).func, render_pdf_view)


    def test_productdetail_resolves(self):
        url =reverse("ecomapp:productdetail", kwargs={'slug':'water-jar'})
        self.assertEquals(resolve(url).func.view_class, ProductDetailView)

        # productdetail veiw is class based view so that func.view_class is used

# unit testing