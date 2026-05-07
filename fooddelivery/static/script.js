function increaseItem(foodId) {
    fetch(`/add-to-cart/${foodId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            updateControlUI(foodId, data.quantity);
            updateCartHeaderCount(1);
        }
    })
    .catch(error => console.error('Error:', error));
}

function decreaseItem(foodId) {
    fetch(`/decrease-cart-item/${foodId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            updateControlUI(foodId, data.quantity);
            updateCartHeaderCount(-1);
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateControlUI(foodId, quantity) {
    const controlDiv = document.getElementById(`controls-${foodId}`);
    if (!controlDiv) return;
    
    if (quantity > 0) {
        controlDiv.innerHTML = `
            <div class="qty-control">
                <button class="btn-qty" onclick="decreaseItem(${foodId})">-</button>
                <span class="qty-display" id="qty-${foodId}">${quantity}</span>
                <button class="btn-qty" onclick="increaseItem(${foodId})">+</button>
            </div>
        `;
    } else {
        controlDiv.innerHTML = `
            <button class="btn-add" onclick="increaseItem(${foodId})">Add to Cart</button>
        `;
    }
}

function updateCartHeaderCount(change) {
    const badge = document.getElementById('header-cart-count');
    if (!badge) return;
    let current = parseInt(badge.textContent || '0');
    current += change;
    badge.textContent = current;
    badge.style.display = current > 0 ? 'flex' : 'none';
}

// Live Search Filtering
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('food-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.food-card');
            let found = 0;
            
            cards.forEach(card => {
                const name = card.querySelector('h2').textContent.toLowerCase();
                const desc = card.querySelector('p').textContent.toLowerCase();
                if (name.includes(term) || desc.includes(term)) {
                    card.style.display = 'block';
                    found++;
                } else {
                    card.style.display = 'none';
                }
            });
        });

        // Search Bar Focus Effect
        searchInput.addEventListener('focus', () => {
            searchInput.style.background = 'rgba(255,255,255,0.1)';
            searchInput.style.borderColor = 'rgba(255,255,255,0.3)';
        });
        searchInput.addEventListener('blur', () => {
            searchInput.style.background = 'rgba(255,255,255,0.05)';
            searchInput.style.borderColor = 'rgba(255,255,255,0.1)';
        });
    }
});


function updateQuantity(cartId) {
    const qty = document.getElementById('qty-' + cartId).value;
    fetch(`/update-cart-quantity/${cartId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ quantity: qty })
    })
    .then(response => response.json())
    .then(data => {
        showPopup(data.message || "Quantity updated!", function() {
            location.reload();
        });
    })
    .catch(error => {
        showPopup("Failed to update quantity.");
        console.error('Error:', error);
    });
}

function deleteItem(cartId) {
    showPopup("Are you sure you want to remove this item from the cart?", function() {
        fetch(`/delete-cart-item/${cartId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(response => response.json())
        .then(data => {
            showPopup(data.message || "Item removed!", function() {
                location.reload();
            });
        })
        .catch(error => {
            showPopup("Failed to remove item.");
            console.error('Error:', error);
        });
    });
}

function showPaymentOptions() {
    document.getElementById('place-order-btn').style.display = 'none';
    document.getElementById('payment-options').style.display = 'block';
}

function submitOrder(paymentMethod) {
    if (paymentMethod === 'online') {
        fetch('/create-stripe-session/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.session_url) {
                window.location.href = data.session_url;
            } else {
                showPopup(data.message || "Failed to start payment.");
            }
        })
        .catch(error => {
            showPopup("Failed to start payment.");
            console.error('Error:', error);
        });
    } else if (paymentMethod === 'dummy') {
        fetch('/dummy-payment/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect_url) {
                showPopup(data.message || "Order placed!", function() {
                    window.location.href = data.redirect_url;
                });
            } else {
                showPopup(data.message || "Order placed!");
            }
        })
        .catch(error => {
            showPopup("Failed to process dummy payment.");
            console.error('Error:', error);
        });
    } else {
        fetch('/place-order/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ payment_method: paymentMethod })
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect_url) {
                showPopup(data.message || "Order placed!", function() {
                    window.location.href = data.redirect_url;
                });
            } else if (data.message && data.message.toLowerCase().includes('cart is empty')) {
                showPopup(data.message, function() {
                    window.location.href = '/cart/';
                });
            } else {
                showPopup(data.message || "Order placed!");
            }
        })
        .catch(error => {
            showPopup("Failed to place order.");
            console.error('Error:', error);
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var placeOrderBtn = document.getElementById('place-order-btn');
    var emptyCartMsg = document.getElementById('empty-cart-msg');
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', function(event) {
            if (emptyCartMsg && emptyCartMsg.style.display !== 'none') {
                event.preventDefault();
                showPopup("Cart is empty!");
            }
        });
    }
});

// Helper function to get CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// Show custom popup with message and optional callback for OK
function showPopup(message, onOk) {
    const popup = document.getElementById('custom-popup');
    const msg = document.getElementById('custom-popup-message');
    const okBtn = document.getElementById('custom-popup-ok');
    msg.textContent = message;
    popup.style.display = 'flex';
    okBtn.onclick = function() {
        popup.style.display = 'none';
        if (typeof onOk === 'function') onOk();
    };
}

function deleteOrder(orderId) {
    if (!confirm("Are you sure you want to delete this order history?")) return;
    fetch(`/delete-order/${orderId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(function(data) {
        document.getElementById('custom-popup-message').innerText = data.message || "Order deleted!";
        document.getElementById('custom-popup').style.display = 'flex';
        setTimeout(() => {
            location.reload();
        }, 1500);
    })
    .catch(error => {
        showPopup("Failed to delete order.");
        console.error('Error:', error);
    });
}

// Chatbot Toggle Logic
document.addEventListener('DOMContentLoaded', () => {
    const trigger = document.getElementById('chatbot-trigger');
    const win = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('chatbot-close');
    const input = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send');
    const messages = document.getElementById('chatbot-messages');

    if (trigger && win) {
        trigger.addEventListener('click', () => {
            const isHidden = win.style.display === 'none' || win.style.display === '';
            win.style.display = isHidden ? 'flex' : 'none';
            if (isHidden) {
                trigger.style.transform = 'scale(0.8) rotate(90deg)';
                input.focus();
            } else {
                trigger.style.transform = 'scale(1) rotate(0)';
            }
        });

        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            win.style.display = 'none';
            trigger.style.transform = 'scale(1) rotate(0)';
        });

        function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            // Add user message
            appendMessage('User', text, true);
            input.value = '';

            // Add typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.id = 'ai-typing';
            typingDiv.style.padding = '14px 18px';
            typingDiv.style.borderRadius = '16px 16px 16px 0';
            typingDiv.style.alignSelf = 'flex-start';
            typingDiv.style.background = '#fff';
            typingDiv.style.border = '1px solid #f1f5f9';
            typingDiv.style.boxShadow = '0 5px 15px rgba(0,0,0,0.03)';
            typingDiv.innerHTML = '<span style="color:#64748b; font-size:0.8rem; font-weight:600;">AI Concierge is thinking...</span>';
            messages.appendChild(typingDiv);
            messages.scrollTop = messages.scrollHeight;

            fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            })
            .then(res => res.json())
            .then(data => {
                const indicator = document.getElementById('ai-typing');
                if (indicator) indicator.remove();
                appendMessage('AI', data.reply, false);
            });
        }

        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        function appendMessage(sender, text, isUser) {
            const div = document.createElement('div');
            div.style.padding = '14px 18px';
            div.style.borderRadius = isUser ? '16px 16px 0 16px' : '16px 16px 16px 0';
            div.style.alignSelf = isUser ? 'flex-end' : 'flex-start';
            div.style.maxWidth = '88%';
            div.style.fontSize = '0.9rem';
            div.style.lineHeight = '1.5';
            div.style.boxShadow = isUser ? '0 5px 15px rgba(15,23,42,0.1)' : '0 5px 15px rgba(0,0,0,0.03)';
            div.style.border = isUser ? 'none' : '1px solid #f1f5f9';
            div.style.background = isUser ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)' : '#fff';
            div.style.color = isUser ? '#fff' : '#334155';
            div.style.position = 'relative';
            
            const senderTag = `<small style="display:block; margin-bottom:4px; font-weight:800; font-size:0.7rem; color:${isUser ? '#94a3b8' : '#64748b'}; text-transform:uppercase;">${sender}</small>`;
            div.innerHTML = `${senderTag}${text}`;
            
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    }
});


