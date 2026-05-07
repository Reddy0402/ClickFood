import os

file_path = r'c:\Users\vippa\Downloads\fooddelivery\fooddelivery\orders\templates\home.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where <!-- Custom Popup Modal --> starts
idx = content.find('<!-- Custom Popup Modal -->')
if idx != -1:
    content_top = content[:idx]
    
    new_bottom = """<!-- Custom Popup Modal -->
        <div id="custom-popup" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.4); z-index:9999; align-items:center; justify-content:center; backdrop-filter: blur(4px);">
            <div style="background:#fff; border-radius:12px; padding:32px 24px; min-width:320px; max-width:90vw; box-shadow:0 10px 40px rgba(0,0,0,0.2); text-align:center; position:relative;">
                <span id="custom-popup-message" style="font-size:1.1rem; color:#222; font-weight: 600;"></span>
                <br><br>
                <button id="custom-popup-ok" style="padding:10px 32px; background:#0f172a; color:#fff; border:none; border-radius:8px; font-size:1rem; font-weight:bold; cursor:pointer;">OK</button>
            </div>
        </div>

    </main>

    <footer class="premium-footer">
        <div class="footer-container">
            <div class="footer-brand">
                <h3>ClickFood <span style="font-weight:300; color:#94a3b8;">Premium</span></h3>
                <p>Elevating your dining experience, one click at a time. The finest cuisines delivered with unparalleled speed and elegance.</p>
            </div>
            <div class="footer-links">
                <h4>Explore</h4>
                <ul>
                    <li><a href="#">Our Menu</a></li>
                    <li><a href="#">Top Rated</a></li>
                    <li><a href="#">Special Offers</a></li>
                </ul>
            </div>
            <div class="footer-contact">
                <h4>Contact Elite Support</h4>
                <p>Email: elite@clickfood.com</p>
                <p>Phone: +1 (800) 555-DINE</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2026 ClickFood Premium. All rights reserved.</p>
        </div>
    </footer>

    <!-- Chatbot Widget UI -->
    <div id="chatbot-widget" style="position:fixed; bottom:20px; right:20px; z-index:10000; width:340px; box-shadow: 0 15px 40px rgba(0,0,0,0.3); border-radius:12px; font-family:'Inter', sans-serif;">
        <div id="chatbot-header" style="background: #0f172a; color:#fff; padding:16px; border-radius:12px 12px 0 0; cursor:pointer; display:flex; justify-content:space-between; align-items:center; border: 1px solid rgba(255,255,255,0.1);">
            <span style="font-weight:bold; font-size:1.1rem;">✨ AI Food Concierge</span>
            <i class='bx bx-chevron-up' id="chatbot-toggle" style="font-size:1.5rem;"></i>
        </div>
        <div id="chatbot-body" style="background:#fff; border:1px solid #eee; border-top:none; height:350px; display:none; flex-direction:column; border-radius: 0 0 12px 12px;">
            <div id="chatbot-messages" style="flex:1; padding:15px; overflow-y:auto; font-size:0.95rem; background:#fafafa; display:flex; flex-direction:column; gap:10px;">
                <div style="color:#444; background:#eee; padding:10px; border-radius:10px 10px 10px 0; align-self:flex-start; max-width:80%;">
                    <strong>AI:</strong> Hello! Tell me your mood, weather, or what you're craving, and I'll find the perfect dish for you!
                </div>
            </div>
            <div style="display:flex; border-top:1px solid #eee; padding:5px; background: #fff; border-radius: 0 0 12px 12px;">
                <input type="text" id="chatbot-input" placeholder="e.g. I feel stressed..." style="flex:1; border:none; padding:12px; outline:none; border-radius:0 0 0 12px; font-family:inherit; font-size:0.95rem;">
                <button id="chatbot-send" style="background:#0f172a; border:none; color:#fff; padding:10px 20px; cursor:pointer; border-radius:8px; font-weight:bold; transition: background 0.3s;">Send</button>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.0/vanilla-tilt.min.js"></script>
    <script>
        VanillaTilt.init(document.querySelectorAll(".food-card"), {
            max: 15,
            speed: 400,
            glare: true,
            "max-glare": 0.2,
        });
    </script>
    <script src="{% static 'script.js' %}?v=1.1"></script>
</body>
</html>
"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content_top + new_bottom)
    print("Done")
