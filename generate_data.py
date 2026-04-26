import json
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker('ru_RU')
random.seed(42)

PRODUCTS = [
    (1,  "Смартфон Samsung Galaxy A55",           29999.0),
    (2,  "Ноутбук Lenovo IdeaPad 3",              54990.0),
    (3,  "Наушники Sony WH-1000XM5",              19990.0),
    (4,  "Телевизор LG 55UQ7500",                 39990.0),
    (5,  "Планшет Apple iPad 10",                 44990.0),
    (6,  "Кофемашина DeLonghi Magnifica",         34990.0),
    (7,  "Пылесос Dyson V15 Detect",              49990.0),
    (8,  "Фотоаппарат Canon EOS R50",             64990.0),
    (9,  "Умные часы Apple Watch SE",             21990.0),
    (10, "Электросамокат Xiaomi Pro 2",           27990.0),
    (11, "Куртка The North Face Resolve",         12990.0),
    (12, "Кроссовки Nike Air Max 90",              8990.0),
    (13, "Рюкзак Osprey Farpoint 40",             14990.0),
    (14, "Джинсы Levi's 501 Original",             6990.0),
    (15, "Книга Мастер и Маргарита",                590.0),
    (16, "Книга Война и мир",                       890.0),
    (17, "Велосипед Trek Marlin 5",               59990.0),
    (18, "Гантели разборные 20кг",                 4990.0),
    (19, "Йогуртница Oursson FE0205D",             2990.0),
    (20, "Миксер KitchenAid Artisan",             44990.0),
    (21, "Холодильник Bosch KGN39VL25",           54990.0),
    (22, "Стиральная машина Indesit IWUB 4085",   24990.0),
    (23, "Посудомоечная машина Bosch SMS25AW01R", 29990.0),
    (24, "Электрочайник Philips HD9352",           3490.0),
    (25, "Блендер Vitamix 5200",                  39990.0),
    (26, "Игровая консоль Sony PlayStation 5",    54990.0),
    (27, "Игра The Last of Us Part I PS5",         4990.0),
    (28, "Принтер Epson L3250",                   14990.0),
    (29, "Роутер ASUS RT-AX88U",                  19990.0),
    (30, "Внешний диск WD My Passport 2TB",        6990.0),
]
PRODUCT_MAP = {pid: (name, price) for pid, name, price in PRODUCTS}

START = date(2023, 1, 1)
END   = date(2024, 12, 31)

def random_date():
    return (START + timedelta(days=random.randint(0, (END - START).days))).isoformat()

def gen_customer_info():
    name = fake.last_name() + " " + fake.first_name() + " " + fake.middle_name()
    phone = fake.phone_number()
    return f"{name}, тел: {phone}"

# --- purchases ---
purchases = []
for i in range(1, 2031):
    product_id = random.randint(1, 30)
    product_name, unit_price = PRODUCT_MAP[product_id]
    quantity = random.randint(1, 10)
    purchases.append({
        "purchase_id":   i,
        "customer_id":   random.randint(1, 200),
        "customer_info": gen_customer_info(),
        "purchase_date": random_date(),
        "product_id":    product_id,
        "product_name":  product_name,
        "quantity":      quantity,
        "total_price":   round(quantity * unit_price, 2),
    })

with open("data/purchases.json", "w", encoding="utf-8") as f:
    for doc in purchases:
        f.write(json.dumps(doc, ensure_ascii=False) + "\n")
print(f"Generated {len(purchases)} purchases")

# --- products ---
products = []
for i in range(1, 2031):
    _, pname, base_price = PRODUCTS[(i - 1) % 30]
    unit_price = round(base_price * random.uniform(0.8, 1.2), 2)
    products.append({
        "product_id":    i,
        "product_name":  pname,
        "batch_date":    random_date(),
        "stock_quantity": random.randint(10, 500),
        "sold_quantity":  random.randint(0, 200),
        "unit_price":     unit_price,
        "description":    fake.sentence(nb_words=random.randint(8, 15)),
        "image_url":      f"https://shop.example.com/images/product_{i}.jpg",
    })

with open("data/products.json", "w", encoding="utf-8") as f:
    for doc in products:
        f.write(json.dumps(doc, ensure_ascii=False) + "\n")
print(f"Generated {len(products)} products")
