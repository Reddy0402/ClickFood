import os

file_path = r'c:\Users\vippa\Downloads\fooddelivery\fooddelivery\static\script.js'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_content = """function increaseItem(foodId) {
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
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content + "\n" + "".join(lines[22:]))

print("Updated script.js successfully!")
