# ClickFood Premium - Universal Master Blueprint & Internal Execution Guide

Welcome to the definitive, single-source-of-truth technical guide for **ClickFood Premium**. This document outlines both the high-level architecture of the system and the precise, step-by-step internal execution paths of the codebase.

---

## SECTION 1: High-Level Architecture & MVT Paradigm

ClickFood Premium is built on **Django 4.x** utilizing the traditional **Model-View-Template (MVT)** paradigm but extended with asynchronous **AJAX-driven APIs** to handle real-time state syncing without full page reloads.

```
+---------------------------------------------------------------------------------+
|                               CLIENT LAYER (Browser)                            |
|  [HTML5 / CSS3 / HSL Tokens] <───> [Vanilla JS Event Loop] <───> [VanillaTilt]  |
+---------------------------------------------------------------------------------+
                                         │
                        Asynchronous AJAX (fetch API) / HTTP
                                         │
                                         ▼
+---------------------------------------------------------------------------------+
|                               CONTROLLER LAYER (Views)                          |
|  - views.home             - views.add_to_cart        - views.login_view         |
|  - views.api_get_cart     - views.dummy_payment      - views.chatbot_api        |
+---------------------------------------------------------------------------------+
                         │                                │
                 Django ORM Query                  External Cloud API
                         │                                │
                         ▼                                ▼
+----------------------------------+            +---------------------------------+
|       DATABASE LAYER (SQLite)    |            |       CLOUD GATEWAYS LAYER      |
|  - FoodItem     - Cart           |            |  - Stripe Checkout (Payments)   |
|  - Order        - UserAddress    |            |  - Groq Llama 3.1 8B (AI LLM)   |
+----------------------------------+            +---------------------------------+
```

---

## SECTION 2: Database Models Schema (`orders/models.py`)

The relational database is constructed around five core models managed via Django's Object-Relational Mapper (ORM):

### 1. `FoodItem`
Holds details of the gourmet dishes available on the menu.
- **`name`** (`CharField`, `max_length=200`): Title of the dish.
- **`description`** (`TextField`): A sensory description of the culinary item.
- **`price`** (`DecimalField`, `max_digits=6`, `decimal_places=2`): Cost in INR.
- **`image`** (`ImageField`, `upload_to='food_images/'`): Path to media asset.
- **`category`** (`CharField`, `max_length=100`, `default='Main Course'`): For filtering chips (e.g., Starter, Dessert).

### 2. `Cart`
Represents intermediate items added by guest or registered users prior to checkout.
- **`food_item`** (`ForeignKey` to `FoodItem`, `on_delete=models.CASCADE`): Cascades deletion of cart rows if a menu item is removed.
- **`quantity`** (`PositiveIntegerField`): Number of items in the basket.
- **`created_at`** (`DateTimeField`, `auto_now_add=True`): Insertion timestamp.

### 3. `Order`
Houses final transaction receipts and historical delivery details.
- **`address`** (`JSONField`): A complete, structured copy of the checkout shipping address. Using a JSONField ensures that even if a user deletes their saved address from their profile later, the historical order receipt retains the precise shipping coordinates exactly as they were at the time of purchase.
- **`total_price`** (`DecimalField`, `max_digits=10`, `decimal_places=2`): Billing value.
- **`status`** (`CharField`, `choices`, `default='Placed'`): Live progress status: `Placed`, `Preparing`, `On the Way`, `Delivered`.
- **`created_at`** (`DateTimeField`, `auto_now_add=True`): Processing timestamp.

### 4. `OrderItem`
A junction table establishing a relational link between food items and processed orders.
- **`order`** (`ForeignKey` to `Order`, `related_name='items'`, `on_delete=models.CASCADE`): Link to parent order receipt.
- **`food_item`** (`ForeignKey` to `FoodItem`): Ordered food item.
- **`quantity`** (`PositiveIntegerField`): Amount purchased.

### 5. `UserAddress`
Stores saved addresses for registered user profiles.
- **`user`** (`ForeignKey` to `User`, `related_name='addresses'`, `on_delete=models.CASCADE`): Connects to Django's native authentication user model.
- **`name`**, **`phone`**, **`area`**, **`city`**, **`landmark`**, **`district`**, **`zipcode`**: Full shipping details.
- **`created_at`** (`DateTimeField`, `auto_now_add=True`).

---

## SECTION 3: Detailed URL Routes Mapping (`orders/urls.py`)

Routing handles request delegation using clean, semantic endpoints:

- `/` (`views.home` | `name='home'`): Primary catalog and landing page.
- `/login/` (`views.login_view` | `name='login_view'`): Unified login/signup page.
- `/register/` (`views.register_view` | `name='register_view'`): Process account registration submissions.
- `/logout/` (`views.logout_view` | `name='logout_view'`): Clears authentication credentials.
- `/cart/` (`views.view_cart` | `name='view_cart'`): Dedicated checkout cart dashboard.
- `/api/cart/` (`views.api_get_cart` | `name='api_get_cart'`): Serialized JSON cart details for the drawer.
- `/add-to-cart/<id>/` (`views.add_to_cart` | `name='add_to_cart'`): AJAX endpoint to increment item quantity.
- `/decrease-cart-item/<id>/` (`views.decrease_cart_item` | `name='decrease_cart_item'`): AJAX endpoint to decrement item quantity.
- `/update-cart-quantity/<id>/` (`views.update_cart_quantity` | `name='update_cart_quantity'`): Sets quantity directly.
- `/delete-cart-item/<id>/` (`views.delete_cart_item` | `name='delete_cart_item'`): Instant cart row deletion.
- `/address/` (`views.address` | `name='address'`): Delivery address forms.
- `/confirm-order/` (`views.confirm_order` | `name='confirm_order'`): Review order details and pick payment method.
- `/place-order/` (`views.place_order` | `name='place_order'`): Finalizes order via Cash on Delivery.
- `/dummy-payment/` (`views.dummy_payment` | `name='dummy_payment'`): Finalizes order via simulated gateway success.
- `/create-stripe-session/` (`views.create_stripe_session` | `name='create_stripe_session'`): Securely redirects to Stripe Checkout.
- `/my-orders/` (`views.my_orders` | `name='my_orders'`): Customer orders history and tracking.
- `/delete-order/<id>/` (`views.delete_order` | `name='delete_order'`): Removes receipt from visible dashboard.
- `/api/chatbot/` (`views.chatbot_api` | `name='chatbot_api'`): AJAX messaging to the AI concierge.

---

## SECTION 4: Step-by-Step Internal Code Execution

Here is exactly how the code works under the hood during key system flows.

### 1. The Core Catalog Request Flow (Visiting `/`)
- **Step A: Matching**: Your browser requests `http://127.0.0.1:8000/`. Django's URL resolver matches `/` to `views.home`.
- **Step B: Query Execution**:
  - The view checks for an active query filter: `category = request.GET.get('category')`.
  - It uses Django's ORM to perform a database query. For example:
    ```python
    FoodItem.objects.filter(category=selected_category)
    ```
    Django dynamically converts this Python ORM query into standard SQL:
    ```sql
    SELECT * FROM orders_fooditem WHERE category = 'Starter';
    ```
  - It also fetches all active cart rows using `Cart.objects.all()`.
- **Step C: In-Memory Synchronization**:
  To ensure the catalog shows correct quantities, the view loops through the query results in memory and appends a temporary attribute:
  ```python
  for food in food_items:
      food.cart_quantity = cart_dict.get(food.id, 0)
  ```
- **Step D: Rendering**:
  The view packages these variables and calls the template compiler:
  ```python
  return render(request, 'home.html', {'food_items': food_items, ...})
  ```
  Django processes `home.html`, replaces tags (like `{% for food in food_items %}` and `{{ food.name }}`) with raw strings, and returns a compiled `200 OK` HTML document.

---

### 2. Asynchronous AJAX Cart Engine (No Page Reloads)
When you click `+` or `-` next to a food item, the app triggers an asynchronous **AJAX** cycle instead of reloading the entire page:

- **Step A: JavaScript Capture**:
  Clicking `+` invokes `increaseItem(foodId)` inside `static/script.js`. The script launches an HTTP POST request to the backend:
  ```javascript
  fetch('/add-to-cart/' + foodId + '/', { method: 'POST' })
  ```
- **Step B: Django AJAX Controller**:
  The `add_to_cart(request, food_id)` view executes:
  - It locates the `FoodItem` matching the ID.
  - It uses Django ORM's `get_or_create` to locate or generate a row in the `Cart` table:
    ```python
    cart_item, created = Cart.objects.get_or_create(food_item=food_item, defaults={'quantity': 1})
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    ```
  - It returns the updated quantity as a JSON payload:
    ```python
    return JsonResponse({'message': 'Item added!', 'quantity': cart_item.quantity})
    ```
- **Step C: DOM Manipulation**:
  The browser receives the JSON response. JavaScript reads `data.quantity` and instantly updates only that specific card's quantity display in the DOM:
  ```javascript
  document.getElementById('qty-' + foodId).textContent = data.quantity;
  ```
- **Step D: Sliding Cart Drawer Sync**:
  Opening the sliding cart drawer triggers a fetch request to `/api/cart/`. The view collects all cart items, serializes them into JSON, and returns them. The frontend JavaScript parses the JSON, dynamically compiles HTML list elements, updates the drawer content, and slides it into view using CSS `transform: translateX(0)`.

---

### 3. Authentication & Cookies Engine
Django manages both **registered accounts** and **anonymous guests** simultaneously using cookie-based sessions.

- **Step A: Login/Signup Actions**:
  When a user submits credentials on the login screen, `login_view` processes the request:
  1. It extracts `username` and `password` from `request.POST`.
  2. It invokes Django's secure hashing and validation engine:
     ```python
     user = authenticate(request, username=username, password=password)
     ```
     Internally, Django hashes the entered password using **PBKDF2 with a SHA256** signature and compares it with the stored hash in the database.
  3. If authenticated, `django_login(request, user)` executes. This generates a **Session ID** cookie (`sessionid`) in your browser and stores the corresponding login state in Django's database session store.
- **Step B: Global Greeting & UI Customization**:
  The auth context processor (`django.contrib.auth.context_processors.auth`) automatically injects the `{{ user }}` variable into every template. On page render, Django checks:
  ```html
  {% if user.is_authenticated %}
  ```
  If the browser's `sessionid` cookie matches a valid session, the condition resolves to `True`, rendering `"Hi, username"` and the `"Sign Out"` link.

---

### 4. Checkout & Payment Pathways

ClickFood supports three transaction flows:

#### A. Cash on Delivery (COD)
- **View**: `place_order(request)`
- **Execution**:
  - Collects the delivery address from the session: `request.session.get('delivery_address')`.
  - Queries active cart items: `Cart.objects.all()`.
  - Inserts an `Order` entry:
    ```python
    order = Order.objects.create(address=address, total_price=total_price)
    ```
  - Creates corresponding `OrderItem` relational entries for each cart item.
  - Deletes all rows in the `Cart` table to empty the cart.
  - Redirects the user to the orders page.

#### B. Stripe Online Gateway
- **View**: `create_stripe_session(request)`
- **Execution**:
  - Gathers active `Cart` rows.
  - Formats them into Stripe's API schema:
    ```python
    line_items.append({
        'price_data': {
            'currency': 'inr',
            'product_data': {'name': item.food_item.name},
            'unit_amount': int(item.food_item.price * 100), # Multiplied by 100 to convert to subunit integer (Paise)
        },
        'quantity': item.quantity,
     })
    ```
  - Invokes `stripe.checkout.Session.create(...)` with the line items and redirect URLs.
  - Stripe returns a secure checkout URL. Django sends this URL back to the frontend as JSON, and JavaScript redirects the browser:
    ```javascript
    window.location.href = data.session_url;
    ```

#### C. Dummy Gateway Payment
- **View**: `dummy_payment(request)`
- **Execution**:
  - Simulates gateway success internally. It bypasses external API calls, executes the database state transitions (creates `Order` and `OrderItem` entries, deletes `Cart` rows), clears session caches, and redirects the user to the orders page.

---

### 5. Menu-Aware AI Concierge Widget
The chat widget at the bottom right provides real-time recommendations tailored to the live database menu:

- **Step A: Input Capture**:
  You type `"What desserts do you have?"` and press Send. JavaScript POSTs the text to `/api/chatbot/`.
- **Step B: Database Menu Mining**:
  The view fetches all `FoodItem` records:
  ```python
  food_items = FoodItem.objects.all()
  ```
- **Step C: Contextual Prompt Assembly**:
  The backend structures this database content into a formatted text block:
  ```text
  Here is our menu:
  - Chocolate Lava Cake: Rs.180 (Rich chocolate dessert...)
  - Fruit Trifle: Rs.150 (Fresh fruit cream...)
  ```
  It wraps this context with a system prompt:
  ```text
  You are a helpful, premium AI food concierge for 'Dhee Quick Bites'. The user says: 'What desserts do you have?'. Based on the following menu, recommend a dish, combo, or pairing that fits their mood/request. Be very polite, enthusiastic, and keep it concise (under 3 sentences).
  ```
- **Step D: LLM Completion**:
  The backend sends this compiled prompt to **Groq's Cloud API** using the `llama-3.1-8b-instant` model. Groq returns a natural-sounding, menu-accurate recommendation, which Django parses and returns as JSON for the chat UI to display.

---

## SECTION 5: Aesthetics, Theme Configurations, and CSS Tokens

ClickFood Premium implements clean CSS styling (`static/style.css`) combined with modern JavaScript animations to create a premium user experience:

- **Theme Variable Tokens**:
  Transitions between light and dark modes are controlled globally using CSS variables:
  - **Light Theme** (Default):
    - Background: `#f8fafc` (Neutral slate-light)
    - Card background: `#ffffff`
    - Core font color: `#0f172a` (Deep slate)
    - Border: `rgba(15, 23, 42, 0.08)`
  - **Dark Theme** (`body.dark-theme`):
    - Background: `#0b0f19` (Midnight obsidian)
    - Card background: `rgba(30, 41, 59, 0.45)` with `backdrop-filter: blur(10px)`
    - Core font color: `#f1f5f9` (Bright gray)
    - Border: `rgba(255, 255, 255, 0.08)`
- **Interactive Animations**:
  - **3D Tilt Effect**: Powered by `VanillaTilt.js`. Hovering over food cards applies 3D rotational transformations based on your mouse coordinates.
  - **Glassmorphic Login Card**: Floating labels animate smoothly using CSS focus triggers (`:focus-within` and `:not(:placeholder-shown)`).
  - **Live Timeline Progress**: The order history timeline calculates progress percentages based on the order's backend state (`Placed` = `0%`, `Preparing` = `33.3%`, `On the Way` = `66.6%`, `Delivered` = `100%`) and animates the progress bar width accordingly.
