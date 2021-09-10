from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from .models import Item
from .forms import AddNewItemForm
import requests
import re
def make_soup(url: str) -> BeautifulSoup:
    res = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'
    })
    res.raise_for_status()
    return BeautifulSoup(res.text, 'lxml')

def parse_product_page(soup: BeautifulSoup) -> dict:
    title = soup.select_one('#productTitle').text.strip()
    clean_price = 0
    try :
        x = soup.select_one('#priceblock_ourprice').text.strip()
    except:
        x = soup.select_one('#priceblock_saleprice').text.strip()
    clean_price = x;

    clean_price = clean_price.split('.', 1)[0]
    clean_price =  re.sub("[^0-9]", "",clean_price)
    price = float(clean_price)
    return {'title': title, 'last_price':price }

def tracker_view(request):
    items = Item.objects.order_by('-id')
    form = AddNewItemForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            url = form.cleaned_data.get('url')
            url = url.split('/ref=sr_1', 1)[0]
            requested_price = form.cleaned_data.get('requested_price')
            soup = make_soup(url)
            info = parse_product_page(soup)
            Item.objects.create(
            url = url,
            title = info['title'],
            requested_price=requested_price,
            last_price=info['last_price'],
            discount_price='No Discount Yet',
            )
            context = {
        'items':items,
        'form':form,
    }
            return render(request, 'tracker.html', context)
        else:
            form = AddNewItemForm()
    context = {
        'items':items,
        'form':form,
    }
    return render(request, 'tracker.html', context)
