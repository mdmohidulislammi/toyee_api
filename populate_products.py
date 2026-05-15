import os
import django
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from toy_api.models import (
    Product, ProductImage, Category, Order, OrderItem, Cart, CartItem, User
)

# ----------------------------------------------------------------------
# 1. CLEAR EXISTING DATA
# ----------------------------------------------------------------------
print("🧹 Clearing existing data...")
OrderItem.objects.all().delete()
Order.objects.all().delete()
CartItem.objects.all().delete()
Cart.objects.all().delete()
ProductImage.objects.all().delete()
Product.objects.all().delete()
Category.objects.all().delete()
print("✅ Data cleared.\n")

# ----------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# ----------------------------------------------------------------------
def create_placeholder_image(product):
    try:
        img = Image.new('RGB', (400, 400), color='#f3f4f6')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        draw.text((200, 200), product.product_name[:30], fill='#9ca3af', anchor='mm', font=font)
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        img_name = f"product_{product.id}_placeholder.jpg"
        ProductImage.objects.create(product=product, img=ContentFile(buffer.getvalue(), name=img_name))
        print(f"  ✓ Created placeholder image for {product.product_name}")
    except Exception as e:
        print(f"  ✗ Failed to create placeholder: {e}")

def download_image(product, url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            ext = 'jpg' if ('jpeg' in content_type or 'jpg' in content_type) else 'png'
            img_name = f"product_{product.id}.{ext}"
            ProductImage.objects.create(product=product, img=ContentFile(response.content, name=img_name))
            print(f"  ✓ Downloaded image for {product.product_name}")
            return True
        else:
            print(f"  ✗ HTTP {response.status_code}, creating placeholder")
            create_placeholder_image(product)
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}, creating placeholder")
        create_placeholder_image(product)
        return False

# ----------------------------------------------------------------------
# 3. CREATE CATEGORIES
# ----------------------------------------------------------------------
category_titles = [
    "Teethers", "Activity Toys", "Stuffed Animals",
    "Soft Dolls", "Push & Pull Toys", "Musical Toys"
]
categories = {}
for title in category_titles:
    cat = Category.objects.create(title=title)
    categories[title] = cat
    print(f"✅ Created category: {title}")

# ----------------------------------------------------------------------
# 4. CREATE ADMIN USER
# ----------------------------------------------------------------------
user, _ = User.objects.get_or_create(
    email='admin@toyee.com',
    defaults={'username': 'admin', 'full_name': 'Toyee Admin'}
)
if not user.is_staff:
    user.is_staff = True
    user.set_password('admin123')
    user.save()
print(f"✅ Admin user: {user.email}")

# --- 2.3 Products data (same 40 entries as before) ---
products_data = [
    # ---------- Teethers (8) ----------
    {
        "product_name": "Rainbow Silicone Teether",
        "category": "Teethers",
        "description": "Easy-to-grip rainbow-shaped teether with textured surfaces to soothe sore gums. Made of food‑grade silicone, BPA‑free, dishwasher safe.",
        "price": 999,
        "stock": 145,
        "min_age": 3,
        "max_age": 12,
        "image_url": "https://m.media-amazon.com/images/I/61hQYZncUXL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Hedgehog Teether",
        "category": "Teethers",
        "description": "Soft silicone hedgehog with multi‑textured bumps for gum massage. Lightweight and easy for tiny hands to hold.",
        "price": 699,
        "stock": 178,
        "min_age": 3,
        "max_age": 12,
        "image_url": "https://m.media-amazon.com/images/I/71hKkdSqNdL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Teething Keys Set",
        "category": "Teethers",
        "description": "Classic set of 4 silicone keys that are soft, chewable, and easy to grasp. Comes with a storage case.",
        "price": 599,
        "stock": 203,
        "min_age": 3,
        "max_age": 12,
        "image_url": "https://m.media-amazon.com/images/I/61QK5sKcKfL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Fruit Teether Set",
        "category": "Teethers",
        "description": "Set of 3 fruit‑shaped silicone teethers (strawberry, banana, orange). Each has a different texture for sensory exploration.",
        "price": 1299,
        "stock": 95,
        "min_age": 3,
        "max_age": 12,
        "image_url": "https://m.media-amazon.com/images/I/81JkM+K8BHL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Giraffe Teether Toy",
        "category": "Teethers",
        "description": "Natural rubber teether shaped like a giraffe – soft, flexible, and safe. Gentle on gums and free from harmful chemicals.",
        "price": 849,
        "stock": 112,
        "min_age": 3,
        "max_age": 12,
        "image_url": "https://m.media-amazon.com/images/I/71iWcfHfRkL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Nuby Bite & Spin Teether",
        "category": "Teethers",
        "description": "Textured silicone ring that spins freely, providing a fun massaging action for sore gums. Dishwasher safe.",
        "price": 749,
        "stock": 88,
        "min_age": 3,
        "max_age": 12,
        "image_url": "https://m.media-amazon.com/images/I/71kKzXHcziL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Twisted Teether Ring",
        "category": "Teethers",
        "description": "Twisted silicone ring with bumps on both sides. Soft, easy to hold, and perfect for front and back teeth.",
        "price": 549,
        "stock": 156,
        "min_age": 3,
        "max_age": 12,
        "image_url": "https://m.media-amazon.com/images/I/71y-KY1gyhL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Carrot Teething Ring",
        "category": "Teethers",
        "description": "Bright orange carrot‑shaped teether with leaf‑shaped handles. Made of 100% food‑grade silicone.",
        "price": 649,
        "stock": 134,
        "min_age": 3,
        "max_age": 12,
        "image_url": "https://m.media-amazon.com/images/I/81IhJY9qjcL._AC_SL1500_.jpg",
    },

    # ---------- Activity Toys (8) ----------
    {
        "product_name": "Wooden Activity Cube (5‑in‑1)",
        "category": "Activity Toys",
        "description": "Five‑sided wooden cube with bead maze, shape sorter, spinning gears, animal sliders, and a clock. Develops motor skills and problem‑solving.",
        "price": 3995,
        "stock": 58,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81jW9yZUzzL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Stacking Rings",
        "category": "Activity Toys",
        "description": "Classic rocking base stacking rings with different textures and colors. Teaches size sequencing and hand‑eye coordination.",
        "price": 799,
        "stock": 112,
        "min_age": 6,
        "max_age": 18,
        "image_url": "https://m.media-amazon.com/images/I/71L3lHZe6dL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Shape Sorter Truck",
        "category": "Activity Toys",
        "description": "Wooden truck with shape sorting blocks. Helps with problem‑solving, fine motor skills, and color recognition.",
        "price": 2199,
        "stock": 46,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81-C8a9VbwL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Busy Board",
        "category": "Activity Toys",
        "description": "Sensory board with zippers, latches, switches, shoelaces, and a clock – develops fine motor skills and real‑world independence.",
        "price": 3599,
        "stock": 28,
        "min_age": 18,
        "max_age": 48,
        "image_url": "https://m.media-amazon.com/images/I/81bZTMTbR4L._AC_SL1500_.jpg",
    },
    {
        "product_name": "Nesting Eggs",
        "category": "Activity Toys",
        "description": "Six colorful nesting eggs with different faces – encourages matching, sorting, and open‑ended imaginative play.",
        "price": 1499,
        "stock": 67,
        "min_age": 12,
        "max_age": 24,
        "image_url": "https://m.media-amazon.com/images/I/71wFLUyfZDL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Activity Walk & Play Center",
        "category": "Activity Toys",
        "description": "2‑in‑1 walker and activity center with lights, sounds, gears, and a bead maze. Supports first steps and sensory play.",
        "price": 4599,
        "stock": 15,
        "min_age": 9,
        "max_age": 24,
        "image_url": "https://m.media-amazon.com/images/I/81XjJg4rwnL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Rainbow Spinning Gears",
        "category": "Activity Toys",
        "description": "Set of five interlocking gears that spin together. Teaches cause‑and‑effect and encourages problem‑solving.",
        "price": 1299,
        "stock": 84,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81k51PgMh3L._AC_SL1500_.jpg",
    },
    {
        "product_name": "Magnetic Drawing Board",
        "category": "Activity Toys",
        "description": "Portable magnetic doodle board for mess‑free drawing. Comes with a stylus and four shape stamps.",
        "price": 1799,
        "stock": 93,
        "min_age": 18,
        "max_age": 48,
        "image_url": "https://m.media-amazon.com/images/I/71s5t0Ux3jL._AC_SL1500_.jpg",
    },

    # ---------- Stuffed Animals (8) ----------
    {
        "product_name": "Fluffy Bunny Stuffed Animal",
        "category": "Stuffed Animals",
        "description": "Super soft hypoallergenic plush bunny, machine washable, perfect cuddle companion for newborns and toddlers.",
        "price": 1299,
        "stock": 89,
        "min_age": 0,
        "max_age": 24,
        "image_url": "https://m.media-amazon.com/images/I/61myUQzqKLL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Panda Plush",
        "category": "Stuffed Animals",
        "description": "Adorable 12‑inch panda bear made from recycled materials. Safe for all ages, perfect for snuggling.",
        "price": 1099,
        "stock": 76,
        "min_age": 0,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/61nIxS0rYhL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Elephant Lovey",
        "category": "Stuffed Animals",
        "description": "Soft elephant security blanket with knotted trunk and ears – perfect for comfort during naps and travel.",
        "price": 1199,
        "stock": 52,
        "min_age": 0,
        "max_age": 18,
        "image_url": "https://m.media-amazon.com/images/I/71nK54h5NxL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Lion Plush Toy",
        "category": "Stuffed Animals",
        "description": "Cuddly lion with a mane that makes crinkle sounds – stimulates hearing and tactile senses.",
        "price": 999,
        "stock": 64,
        "min_age": 0,
        "max_age": 24,
        "image_url": "https://m.media-amazon.com/images/I/71pY3dI-iBL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Sloth Stuffed Animal",
        "category": "Stuffed Animals",
        "description": "Super soft sloth with long, dangling arms – perfect for hugging and sensory play. Lightweight and travel‑friendly.",
        "price": 1399,
        "stock": 41,
        "min_age": 0,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/71qU-f3uYHL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Giraffe Plush with Rattle",
        "category": "Stuffed Animals",
        "description": "Adorable 10‑inch giraffe with a gentle rattle inside. Perfect for shaking, hugging, and on‑the‑go play.",
        "price": 899,
        "stock": 73,
        "min_age": 0,
        "max_age": 24,
        "image_url": "https://m.media-amazon.com/images/I/71Bp7WmZSCL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Koala Bear Plush",
        "category": "Stuffed Animals",
        "description": "Ultra‑soft koala bear with a gentle, huggable body. Made from premium materials that are safe for babies.",
        "price": 1199,
        "stock": 58,
        "min_age": 0,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/71MnJbUoYvL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Unicorn Lovey Blanket",
        "category": "Stuffed Animals",
        "description": "Plush unicorn head attached to a soft, silky blanket – soothing for newborns and a great travel companion.",
        "price": 1499,
        "stock": 47,
        "min_age": 0,
        "max_age": 18,
        "image_url": "https://m.media-amazon.com/images/I/71V5kZJ-DYL._AC_SL1500_.jpg",
    },

    # ---------- Soft Dolls (6) ----------
    {
        "product_name": "Soft Doll – Lila",
        "category": "Soft Dolls",
        "description": "Baby‑safe cloth doll with embroidered face, removable onesie, and soft huggable body. Machine washable.",
        "price": 1899,
        "stock": 27,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/71-Nw-KhBCL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Soft Doll – Ethan",
        "category": "Soft Dolls",
        "description": "Neutral outfit cloth doll with embroidered features, perfect for nurturing play. Machine washable and durable.",
        "price": 1899,
        "stock": 31,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/71safd7WzAL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Soft Doll – Mia (Hispanic)",
        "category": "Soft Dolls",
        "description": "Diverse cloth doll with textured hair, embroidered face, and removable clothes. Celebrates inclusivity.",
        "price": 1999,
        "stock": 23,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/71B4-WK+77L._AC_SL1500_.jpg",
    },
    {
        "product_name": "Mini Soft Doll Set",
        "category": "Soft Dolls",
        "description": "Set of 3 small cloth dolls (different skin tones) with magnetic pacifiers. Encourages empathy and role play.",
        "price": 2499,
        "stock": 19,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/71WcVq-NNyL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Doll Stroller",
        "category": "Soft Dolls",
        "description": "Folding doll stroller – fits most soft dolls up to 16 inches. Sturdy and easy for little hands to push.",
        "price": 2799,
        "stock": 14,
        "min_age": 18,
        "max_age": 48,
        "image_url": "https://m.media-amazon.com/images/I/81OgLtK4YaL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Baby Doll Carrier",
        "category": "Soft Dolls",
        "description": "Adjustable soft doll carrier – lets toddlers carry their favourite soft doll just like Mom or Dad.",
        "price": 1499,
        "stock": 38,
        "min_age": 18,
        "max_age": 48,
        "image_url": "https://m.media-amazon.com/images/I/71SxwZ5q+GL._AC_SL1500_.jpg",
    },

    # ---------- Push & Pull Toys (5) ----------
    {
        "product_name": "Pull Along Duck",
        "category": "Push & Pull Toys",
        "description": "Waddling wooden duck on wheels, makes gentle clicking sounds when pulled. Develops walking skills and coordination.",
        "price": 1599,
        "stock": 42,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81OHD3P4eEL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Push Car (Wooden)",
        "category": "Push & Pull Toys",
        "description": "Wooden push car with silent wheels, helps build gross motor skills and encourages active play.",
        "price": 1299,
        "stock": 64,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81iMRVpVt4L._AC_SL1500_.jpg",
    },
    {
        "product_name": "Snail Pull Toy",
        "category": "Push & Pull Toys",
        "description": "Colorful wooden snail that wobbles when pulled – develops walking and coordination. Comes with a soft string.",
        "price": 1399,
        "stock": 38,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81wNWAHSfML._AC_SL1500_.jpg",
    },
    {
        "product_name": "Push & Ride Elephant",
        "category": "Push & Pull Toys",
        "description": "2‑in‑1 ride‑on and push toy – sturdy wheels and storage under the seat. Great for indoor/outdoor use.",
        "price": 4999,
        "stock": 9,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81He9aCPYFL._AC_SL1500_.jpg",
    },
    {
        "product_name": "VTech Pop‑a‑Balls Push & Pop Bulldozer",
        "category": "Push & Pull Toys",
        "description": "Interactive bulldozer that pops balls when pushed. Teaches colors, numbers, and motor skills. For ages 1–3 years.",
        "price": 3899,
        "stock": 17,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81zQ0m0LQCL._AC_SL1500_.jpg",
    },

    # ---------- Musical Toys (5) ----------
    {
        "product_name": "Musical Xylophone",
        "category": "Musical Toys",
        "description": "Colorful 8‑note xylophone with mallet. Encourages rhythm and hand‑eye coordination. Includes songbook.",
        "price": 2499,
        "stock": 34,
        "min_age": 12,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/81FbMMQwRkL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Drum Set for Toddlers",
        "category": "Musical Toys",
        "description": "Mini drum set with two drumsticks, tambourine, and maracas. Great for sensory play and rhythm exploration.",
        "price": 3499,
        "stock": 22,
        "min_age": 18,
        "max_age": 48,
        "image_url": "https://m.media-amazon.com/images/I/81ENg50T+gL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Elephant Musical Toy",
        "category": "Musical Toys",
        "description": "Plush elephant that plays five lullabies and glows softly. Batteries included. Perfect for bedtime.",
        "price": 1899,
        "stock": 39,
        "min_age": 6,
        "max_age": 24,
        "image_url": "https://m.media-amazon.com/images/I/71KUCXSkZSL._AC_SL1500_.jpg",
    },
    {
        "product_name": "Maraca Set (Pair)",
        "category": "Musical Toys",
        "description": "Two wooden maracas with non‑toxic paint – safe for little hands. Creates a gentle, rhythmic sound.",
        "price": 799,
        "stock": 83,
        "min_age": 6,
        "max_age": 36,
        "image_url": "https://m.media-amazon.com/images/I/71y7-5Olp2L._AC_SL1500_.jpg",
    },
    {
        "product_name": "Piano Mat",
        "category": "Musical Toys",
        "description": "Floor piano mat with 8 large keys – play music by stepping or tapping. Encourages movement and musical creativity.",
        "price": 3999,
        "stock": 16,
        "min_age": 12,
        "max_age": 48,
        "image_url": "https://m.media-amazon.com/images/I/81fAuV0fdrL._AC_SL1500_.jpg",
    },
]

# --- 2.4 Insert products and download images ---
for data in products_data:
    cat_title = data.pop("category")
    cat = categories[cat_title]
    image_url = data.pop("image_url")
    product = Product.objects.create(
        **data,
        user=user,
        category=cat,
        is_available=True
    )
    print(f"✅ Created: {product.product_name}")
    if image_url:
        download_image(product, image_url)
    else:
        create_placeholder_image(product)

print(f"\n🎉 Done! Products: {Product.objects.count()}, Images: {ProductImage.objects.count()}")