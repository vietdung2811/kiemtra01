from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
import requests

# Base URLs for other services inside docker network
LAPTOP_API_URL = "http://laptop_service:8003/api/laptops/"
MOBILE_API_URL = "http://mobile_service:8004/api/mobiles/"

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('staff_home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials or not a staff member'})
    return render(request, 'login.html')

def staff_logout(request):
    logout(request)
    return redirect('login')

def staff_home(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    
    # Fetch all items to display
    laptops = []
    mobiles = []
    try:
        laptops = requests.get(LAPTOP_API_URL, headers={'Host': 'laptop-service'}).json()
        mobiles = requests.get(MOBILE_API_URL, headers={'Host': 'mobile-service'}).json()
    except Exception as e:
        print(f"Error fetching items: {e}")

    return render(request, 'staff_home.html', {'laptops': laptops, 'mobiles': mobiles})

def add_item(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    
    if request.method == 'POST':
        product_type = request.POST.get('product_type')
        data = {
            'name': request.POST.get('name'),
            'brand': request.POST.get('brand'),
            'price': request.POST.get('price'),
            'description': request.POST.get('description'),
            'stock': request.POST.get('stock'),
        }
        
        url = LAPTOP_API_URL if product_type == 'laptop' else MOBILE_API_URL
        host = 'laptop-service' if product_type == 'laptop' else 'mobile-service'
        print(f"Sending POST to {url} with data: {data}")
        try:
            response = requests.post(url, data=data, headers={'Host': host})
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:500]}")
            
            if response.status_code == 201:
                return redirect('staff_home')
            else:
                return render(request, 'add_item.html', {'error': f'Failed to add item: {response.status_code}', 'data': data})
        except Exception as e:
            print(f"Exception during POST: {e}")
            return render(request, 'add_item.html', {'error': f'Exception: {e}', 'data': data})
            
    return render(request, 'add_item.html')

def update_item(request, product_type, product_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    
    url = f"{LAPTOP_API_URL if product_type == 'laptop' else MOBILE_API_URL}{product_id}/"
    host = 'laptop-service' if product_type == 'laptop' else 'mobile-service'
    
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'brand': request.POST.get('brand'),
            'price': request.POST.get('price'),
            'description': request.POST.get('description'),
            'stock': request.POST.get('stock'),
        }
        response = requests.put(url, data=data, headers={'Host': host})
        if response.status_code == 200:
            return redirect('staff_home')
        else:
            return render(request, 'update_item.html', {'error': 'Failed to update item', 'item': data, 'product_type': product_type})

    response = requests.get(url, headers={'Host': host})
    if response.status_code == 200:
        item = response.json()
        return render(request, 'update_item.html', {'item': item, 'product_type': product_type})
    
    return redirect('staff_home')

def delete_item(request, product_type, product_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    
    url = f"{LAPTOP_API_URL if product_type == 'laptop' else MOBILE_API_URL}{product_id}/"
    host = 'laptop-service' if product_type == 'laptop' else 'mobile-service'
    
    response = requests.delete(url, headers={'Host': host})
    return redirect('staff_home')
