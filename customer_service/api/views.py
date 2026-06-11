from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from .models import Cart, CartItem, Order, OrderItem
import requests
from decimal import Decimal
import json
from django.views.decorators.csrf import csrf_exempt

# Base URLs for other services inside docker network
LAPTOP_API_URL = "http://laptop_service:8003/api/laptops/"
MOBILE_API_URL = "http://mobile_service:8004/api/mobiles/"
AI_API_URL = "http://ai-service:8005/api/"

def customer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('customer_home') # Redirect to cart
        else:
            # Authentication failed
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def customer_logout(request):
    logout(request)
    return redirect('login')

def customer_home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    
    # AI Recommendations
    recommendations = []
    graph_recommendations = []
    try:
        resp = requests.get(f"{AI_API_URL}recommend/", params={'user_id': request.user.id}, timeout=2)
        if resp.status_code == 200:
            recommendations = resp.json().get('recommendations', [])
            
        g_resp = requests.get(f"{AI_API_URL}graph-recommend/", params={'user_id': request.user.id}, timeout=2)
        if g_resp.status_code == 200:
            graph_recommendations = g_resp.json().get('recommendations', [])
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
    
    # We might want to enrich item data with names from APIs
    # For now, just display IDs
    return render(request, 'home.html', {
        'items': items, 
        'user': request.user, 
        'recommendations': recommendations,
        'graph_recommendations': graph_recommendations
    })

def product_search(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    query = request.GET.get('q', '')
    laptops = []
    mobiles = []
    
    try:
        # Fetch products from services
        l_resp = requests.get(LAPTOP_API_URL, headers={'Host': 'laptop-service'})
        m_resp = requests.get(MOBILE_API_URL, headers={'Host': 'mobile-service'})
        
        if l_resp.status_code == 200:
            laptops = l_resp.json()
        if m_resp.status_code == 200:
            mobiles = m_resp.json()
            
        # Filter if search query exists
        if query:
            laptops = [l for l in laptops if query.lower() in l['name'].lower() or query.lower() in l['brand'].lower()]
            mobiles = [m for m in mobiles if query.lower() in m['name'].lower() or query.lower() in m['brand'].lower()]
            
    except Exception as e:
        print(f"Error searching products: {e}")
        
    # AI Recommendations
    recommendations = []
    graph_recommendations = []
    try:
        resp = requests.get(f"{AI_API_URL}recommend/", params={'user_id': request.user.id, 'query': query}, timeout=2)
        if resp.status_code == 200:
            recommendations = resp.json().get('recommendations', [])
            
        g_resp = requests.get(f"{AI_API_URL}graph-recommend/", params={'user_id': request.user.id}, timeout=2)
        if g_resp.status_code == 200:
            graph_recommendations = g_resp.json().get('recommendations', [])
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        
    return render(request, 'search.html', {
        'laptops': laptops, 
        'mobiles': mobiles, 
        'query': query,
        'recommendations': recommendations,
        'graph_recommendations': graph_recommendations,
        'user': request.user
    })

def add_to_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        product_type = request.POST.get('product_type')
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        item, item_created = CartItem.objects.get_or_create(
            cart=cart, 
            product_type=product_type, 
            product_id=product_id
        )
        if not item_created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        
        # Track view/interest in AI service
        try:
            url = f"{LAPTOP_API_URL if product_type == 'laptop' else MOBILE_API_URL}{product_id}/"
            host = 'laptop-service' if product_type == 'laptop' else 'mobile-service'
            resp = requests.get(url, headers={'Host': host}, timeout=1)
            if resp.status_code == 200:
                p_data = resp.json()
                track_data = {
                    "user_id": request.user.id,
                    "product_id": product_id,
                    "product_type": product_type,
                    "brand": p_data.get('brand'),
                    "name": p_data.get('name'),
                    "price": p_data.get('price'),
                    "description": p_data.get('description')
                }
                requests.post(f"{AI_API_URL}track-view/", json=track_data, timeout=1)
        except Exception as e:
            print(f"Error tracking view: {e}")

        return redirect('customer_home')
        
    return redirect('product_search')

@csrf_exempt
def track_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_type = data.get('product_type')
            product_id = data.get('product_id')
            
            # Fetch product details and track view
            url = f"{LAPTOP_API_URL if product_type == 'laptop' else MOBILE_API_URL}{product_id}/"
            host = 'laptop-service' if product_type == 'laptop' else 'mobile-service'
            resp = requests.get(url, headers={'Host': host}, timeout=1)
            
            if resp.status_code == 200:
                p_data = resp.json()
                track_data = {
                    "user_id": request.user.id,
                    "product_id": product_id,
                    "product_type": product_type,
                    "brand": p_data.get('brand'),
                    "name": p_data.get('name'),
                    "price": p_data.get('price'),
                    "description": p_data.get('description')
                }
                requests.post(f"{AI_API_URL}track-view/", json=track_data, timeout=1)
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        except Exception as e:
            print(f"Error in track_view: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def discard_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    
    return redirect('customer_home')

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('customer_home')
        
    # Start creating order
    order = Order.objects.create(user=request.user)
    total_price = Decimal('0.00')
    
    for item in cart_items:
        url = f"{LAPTOP_API_URL if item.product_type == 'laptop' else MOBILE_API_URL}{item.product_id}/"
        host = 'laptop-service' if item.product_type == 'laptop' else 'mobile-service'
        
        # 1. Fetch current product data (to get name, price and current stock)
        try:
            resp = requests.get(url, headers={'Host': host})
            if resp.status_code == 200:
                product_data = resp.json()
                current_stock = product_data.get('stock', 0)
                price = Decimal(str(product_data.get('price', '0.00')))
                
                # 2. Update stock (Simple reduction logic)
                new_stock = max(0, current_stock - item.quantity)
                requests.patch(url, data={'stock': new_stock}, headers={'Host': host})
                
                # 3. Create OrderItem
                OrderItem.objects.create(
                    order=order,
                    product_type=item.product_type,
                    product_id=item.product_id,
                    product_name=product_data.get('name', 'Unknown'),
                    quantity=item.quantity,
                    price_at_order=price
                )
                total_price += price * item.quantity
        except Exception as e:
            print(f"Error during checkout for item {item.id}: {e}")
            
    order.total_price = total_price
    order.save()
    
    # 4. Clear Cart
    cart_items.delete()
    
    return redirect('order_history')

def order_history(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})
