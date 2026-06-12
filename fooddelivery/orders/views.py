from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import FoodItem, Cart, Order, OrderItem, UserAddress
import json
import stripe
from django.conf import settings
import os
from groq import Groq

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def home(request):
    selected_category = request.GET.get('category')
    if selected_category and selected_category != 'All':
        food_items = list(FoodItem.objects.filter(category=selected_category))
    else:
        food_items = list(FoodItem.objects.all())
    
    categories = FoodItem.objects.values_list('category', flat=True).distinct()
    
    cart_items = Cart.objects.all()
    cart_dict = {item.food_item.id: item.quantity for item in cart_items}
    cart_count = sum(cart_dict.values())
    
    for food in food_items:
        food.cart_quantity = cart_dict.get(food.id, 0)
        
    return render(request, 'home.html', {
        'food_items': food_items,
        'cart_count': cart_count,
        'categories': categories,
        'selected_category': selected_category or 'All'
    })

@csrf_exempt  # Temporarily disable CSRF for testing (use CSRF token in production)
def add_to_cart(request, food_id):
    if request.method == 'POST':
        try:
            food_item = FoodItem.objects.get(id=food_id)
            cart_item, created = Cart.objects.get_or_create(
                food_item=food_item,
                defaults={'quantity': 1}  # Ensure quantity is set for new items
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            return JsonResponse({'message': 'Item added to cart!', 'quantity': cart_item.quantity})
        except FoodItem.DoesNotExist:
            return JsonResponse({'message': 'Food item not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@csrf_exempt
def decrease_cart_item(request, food_id):
    if request.method == 'POST':
        try:
            food_item = FoodItem.objects.get(id=food_id)
            cart_item = Cart.objects.get(food_item=food_item)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return JsonResponse({'message': 'Quantity decreased!', 'quantity': cart_item.quantity})
            else:
                cart_item.delete()
                return JsonResponse({'message': 'Item removed from cart!', 'quantity': 0})
        except (FoodItem.DoesNotExist, Cart.DoesNotExist):
            return JsonResponse({'message': 'Item not found in cart!'}, status=404)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

def api_get_cart(request):
    try:
        cart_items = Cart.objects.all()
        items_data = []
        total_price = 0
        for item in cart_items:
            try:
                image_url = item.food_item.image.url if item.food_item.image else ''
            except Exception:
                image_url = ''
                
            items_data.append({
                'id': item.id,
                'food_id': item.food_item.id,
                'name': item.food_item.name,
                'price': float(item.food_item.price),
                'image_url': image_url,
                'quantity': item.quantity,
                'total_price': float(item.food_item.price * item.quantity),
            })
            total_price += float(item.food_item.price * item.quantity)
        return JsonResponse({
            'items': items_data,
            'total_price': total_price,
            'cart_count': sum(item.quantity for item in cart_items)
        })
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

def view_cart(request):
    cart_items = Cart.objects.all()
    for item in cart_items:
        item.total_price = item.food_item.price * item.quantity
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        # Get address from session
        address = request.session.get('delivery_address', '')
        cart_items = Cart.objects.all()
        if not cart_items:
            return JsonResponse({'message': 'Cart is empty!'}, status=400)
        total_price = sum(item.food_item.price * item.quantity for item in cart_items)
        order = Order.objects.create(address=address, total_price=total_price)
        for item in cart_items:
            OrderItem.objects.create(order=order, food_item=item.food_item, quantity=item.quantity)
        cart_items.delete()
        # Save to session history for guests
        request.session['last_used_address'] = address
        request.session.pop('delivery_address', None)
        # Redirect to my orders page after placing order
        return JsonResponse({'redirect_url': '/my-orders/'})
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@csrf_exempt
def update_cart_quantity(request, cart_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            if quantity < 1:
                return JsonResponse({'message': 'Quantity must be at least 1.'}, status=400)
            cart_item = Cart.objects.get(id=cart_id)
            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'message': 'Quantity updated!'})
        except Cart.DoesNotExist:
            return JsonResponse({'message': 'Cart item not found!'}, status=404)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@csrf_exempt
def delete_cart_item(request, cart_id):
    if request.method == 'POST':
        try:
            cart_item = Cart.objects.get(id=cart_id)
            cart_item.delete()
            return JsonResponse({'message': 'Item removed from cart!'})
        except Cart.DoesNotExist:
            return JsonResponse({'message': 'Cart item not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

def my_orders(request):
    orders = Order.objects.all().order_by('-created_at')  # or filter by user if needed
    return render(request, 'my_orders.html', {'orders': orders})

@csrf_exempt
def delete_order(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            return JsonResponse({'message': 'Order deleted successfully!'})
        except Order.DoesNotExist:
            return JsonResponse({'message': 'Order not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@csrf_exempt
def create_stripe_session(request):
    if request.method == 'POST':
        cart_items = Cart.objects.all()
        if not cart_items:
            return JsonResponse({'message': 'Cart is empty!'}, status=400)
        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': item.food_item.name,
                    },
                    'unit_amount': int(item.food_item.price * 100),
                },
                'quantity': item.quantity,
            })
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri('/cart/'),
                cancel_url=request.build_absolute_uri('/cart/'),
            )
            return JsonResponse({'session_url': session.url})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

def address(request):
    previous_addresses = []
    if request.user.is_authenticated:
        previous_addresses = list(UserAddress.objects.filter(user=request.user).order_by('-id'))
    
    # Guest session history support
    session_addr = request.session.get('last_used_address')
    if session_addr and isinstance(session_addr, dict):
        # Check if this session address is already in the list
        already_exists = False
        for a in previous_addresses:
            a_phone = getattr(a, 'phone', a.get('phone') if isinstance(a, dict) else '')
            a_zip = getattr(a, 'zipcode', a.get('zipcode') if isinstance(a, dict) else '')
            if a_phone == session_addr.get('phone') and a_zip == session_addr.get('zipcode'):
                already_exists = True
                break
        
        if not already_exists:
            previous_addresses.insert(0, session_addr)
        
    # Auto-use the latest address if it exists and we aren't explicitly trying to change it
    if previous_addresses and request.method == 'GET' and 'change' not in request.GET:
        latest = previous_addresses[0]
        # Handle both object and dict
        if hasattr(latest, 'name'):
            address_data = {'name': latest.name, 'phone': latest.phone, 'area': latest.area, 'city': latest.city, 'landmark': latest.landmark, 'district': latest.district, 'zipcode': latest.zipcode}
        else:
            address_data = latest
        request.session['delivery_address'] = address_data
        return redirect('confirm_order')
        
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id and request.user.is_authenticated:
            address_obj = UserAddress.objects.get(id=selected_address_id, user=request.user)
            address_data = {
                'name': address_obj.name,
                'phone': address_obj.phone,
                'area': address_obj.area,
                'city': address_obj.city,
                'landmark': address_obj.landmark,
                'district': address_obj.district,
                'zipcode': address_obj.zipcode,
            }
        else:
            address_data = {
                'name': request.POST.get('name'),
                'phone': request.POST.get('phone'),
                'area': request.POST.get('area'),
                'city': request.POST.get('city'),
                'landmark': request.POST.get('landmark', ''),
                'district': request.POST.get('district'),
                'zipcode': request.POST.get('zipcode'),
            }
            # Save new address for future use if the user is logged in
            if request.user.is_authenticated:
                UserAddress.objects.create(user=request.user, **address_data)
                
        request.session['delivery_address'] = address_data
        request.session['last_used_address'] = address_data # Save to history immediately
        return redirect('confirm_order')
        
    return render(request, 'address.html', {'previous_addresses': previous_addresses})

def confirm_order(request):
    cart_items = Cart.objects.all()
    if not cart_items:
        return redirect('view_cart')
    address = request.session.get('delivery_address')
    if not address:
        return redirect('address')
    return render(request, 'confirm_order.html', {'address': address})

def my_orders(request):
    orders = Order.objects.all().order_by('-created_at')  # or filter by user if needed
    return render(request, 'my_orders.html', {'orders': orders})

@require_POST
def delete_address(request, address_id):
    try:
        address = UserAddress.objects.get(id=address_id, user=request.user)
        address.delete()
        return JsonResponse({'success': True, 'message': 'Address deleted.'})
    except UserAddress.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Address not found.'}, status=404)

@csrf_exempt
def dummy_payment(request):
    if request.method == 'POST':
        # Simulate payment success
        address = request.session.get('delivery_address', '')
        cart_items = Cart.objects.all()
        if not cart_items:
            return JsonResponse({'message': 'Cart is empty!'}, status=400)
        total_price = sum(item.food_item.price * item.quantity for item in cart_items)
        order = Order.objects.create(address=address, total_price=total_price)
        for item in cart_items:
            OrderItem.objects.create(order=order, food_item=item.food_item, quantity=item.quantity)
        cart_items.delete()
        
        # Save to session history for guests
        request.session['last_used_address'] = address
        request.session.pop('delivery_address', None)
        return JsonResponse({'redirect_url': '/my-orders/', 'message': 'Order Placed!'})
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Fetch menu context
            food_items = FoodItem.objects.all()
            menu_context = "Here is our menu:\n"
            for item in food_items:
                menu_context += f"- {item.name}: Rs.{item.price} ({item.description})\n"
                
            prompt = f"You are a helpful, premium AI food concierge for 'ClickFood Premium'. The user says: '{user_message}'. Based on the following menu, recommend a dish, combo, or pairing that fits their mood/request. Be very polite, enthusiastic, and keep it concise (under 3 sentences).\n\n{menu_context}"
            
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                return JsonResponse({'reply': 'Groq API key not configured yet. Please check .env file.'})
                
            client = Groq(api_key=groq_api_key)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150,
            )
            
            reply = completion.choices[0].message.content
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'reply': f'Error processing request: {str(e)}'})
    return JsonResponse({'reply': 'Invalid request method.'})


from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    next_url = request.GET.get('next', 'home')
    if request.user.is_authenticated:
        return redirect(next_url)
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'login.html', {'next': next_url})
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'login.html', {'next': next_url})

def register_view(request):
    next_url = request.GET.get('next', 'home')
    if request.user.is_authenticated:
        return redirect(next_url)
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'login.html', {'next': next_url, 'active_tab': 'signup'})
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'login.html', {'next': next_url, 'active_tab': 'signup', 'username': username, 'email': email})
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'login.html', {'next': next_url, 'active_tab': 'signup', 'email': email})
            
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            django_login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}.")
            return redirect(next_url)
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            
    return render(request, 'login.html', {'next': next_url, 'active_tab': 'signup'})

def logout_view(request):
    django_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')




