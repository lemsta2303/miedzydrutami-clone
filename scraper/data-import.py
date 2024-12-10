import requests
from pathlib import Path
import json
import os
import urllib3
import xml.etree.ElementTree as ET
import random
from jinja2 import Environment, FileSystemLoader
from alive_progress import alive_bar
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = Path(__file__).resolve().parent.parent
API_KEY = "1743CVHJIMQTNZPF3DC51RGUEEQ6BXU9"
JSON_DIR = BASE_DIR / "scraper-data"
JSON_FILE = JSON_DIR / "data.json"
XML_VIEW = BASE_DIR / "scraper/views"
SHOP_URL = "https://localhost:443"
PRODUCT_PATH = f"https://localhost:443/api/products"
CATEGORY_PATH = f"https://localhost:443/api/categories"
STOCK_PATH = f"https://localhost:443/api/stock_availables"
IMAGE_PATH = f"https://localhost:443/api/images/products"
QUANTITY = 10

jinja_env = Environment(loader=FileSystemLoader(XML_VIEW))

def create_category(category_name: str, session: requests.Session) -> dict:
    category_data = {"name": category_name}
    template = jinja_env.get_template("category.xml")
    category_xml = template.render(name=category_name)
    response = session.post(CATEGORY_PATH, data=category_xml.encode("utf-8"))
    if not response.ok:
        print(f"Failed to create category {category_name} with {response.text}")
        return None
    root = ET.fromstring(response.text)
    category_data["id"] = int(root.find("category/id").text)
    return category_data

def create_subcategory(subcategory_name: str, parent_category: dict, session: requests.Session) -> dict:
    subcategory_data = {"name": subcategory_name, "parent_id": parent_category["id"]}
    template = jinja_env.get_template("subcategory.xml")
    subcategory_xml = template.render(name=subcategory_name, parent_id=parent_category["id"])
    response = session.post(CATEGORY_PATH, data=subcategory_xml.encode("utf-8"))
    if not response.ok:
        print(f"Failed to create subcategory {subcategory_name} with {response.text}")
        return None
    root = ET.fromstring(response.text)
    subcategory_data["id"] = int(root.find("category/id").text)
    return subcategory_data

def create_product(product_data: dict, category_data: dict, session: requests.Session) -> dict:
    product_details = {
        "name": product_data["name"],
        "price": product_data["price"],
        "images_paths": [Path(__file__).parent.parent / image["local-path"] for image in product_data["images"]],
        "short_description": product_data["short-description"],
        "description": product_data["description"],
        "ean13": "".join([str(random.randint(0, 9)) for _ in range(13)]),
        "category_id": category_data["id"]
    }
    template = jinja_env.get_template("product.xml")
    product_xml = template.render(
        ean13=product_details["ean13"],
        category_id=product_details["category_id"],
        name=product_details["name"],
        description=product_details["description"],
        summary=product_details["short_description"],
        price=product_details["price"],
        images_paths=product_details["images_paths"]
    )
    response = session.post(PRODUCT_PATH, data=product_xml.encode("utf-8"))
    if not response.ok:
        print(f"Failed to create product {product_details['name']} with {response.text}")
        return None
    root = ET.fromstring(response.text)
    product_details["id"] = int(root.find("product/id").text)
    patch_stock(product_details["id"], QUANTITY, session)
    upload_images(product_details["id"], product_details["images_paths"], session)
    return product_details

def patch_stock(product_id: int, stock_quantity: int, session: requests.Session):
    stock_xml = session.get(f"{STOCK_PATH}?filter[id_product]={product_id}&display=full").text
    root = ET.fromstring(stock_xml)
    stock_id = int(root.find("stock_availables/stock_available/id").text)
    template = jinja_env.get_template("quantity.xml")
    patch_xml = template.render(stock_id=stock_id, product_id=product_id, stock=stock_quantity)
    response = session.put(f"{STOCK_PATH}/{stock_id}", data=patch_xml)
    if not response.ok:
        print(f"Failed updating stock for product {product_id} with {response.text}")

def upload_images(product_id: int, image_paths: list[Path], session: requests.Session):
    for image_path in image_paths:
        mime_type = "image/jpeg" if image_path.suffix.lower() == ".jpg" else "image/webp"
        files = {"image": (image_path.name, open(image_path, "rb"), mime_type)}
        response = session.post(f"{IMAGE_PATH}/{product_id}", files=files)
        if not response.ok:
            print(f"Failed uploading image {image_path} for product {product_id} with {response.text}")

def read_and_seed(json_dir: Path, product_limit: int = 3) -> list[dict]:
    data_json_file = json_dir / JSON_FILE
    with open(data_json_file, "r") as file:
        categories_data = json.load(file)

    session = requests.Session()
    session.verify = False
    session.auth = requests.auth.HTTPBasicAuth(API_KEY, "")

    total_products = sum(
        min(len(subcategory["products"]), product_limit)
        for category in categories_data.values()
        for subcategory in category["subcategories"].values()
    )
    products_list = []
    with alive_bar(total_products, title="Importing products") as bar:
        for category_name, category_data in categories_data.items():
            category = create_category(category_name, session)
            if category is None:
                exit(1)
            for subcategory_name, subcategory_data in category_data["subcategories"].items():
                subcategory = create_subcategory(subcategory_name, category, session)
                if subcategory is None:
                    exit(1)
                for i, product in enumerate(subcategory_data["products"]):
                    if i == product_limit:
                        break
                    created_product = create_product(product, subcategory, session)
                    if created_product is not None:
                        products_list.append(created_product)
                    else:
                        print("Skipped product")
                    bar()
    return products_list

def zero_stock(products_list: list[dict], session: requests.Session):
    with alive_bar(len(products_list), title="Some products out of stock") as bar:
        for product in products_list:
            patch_stock(product["id"], 0, session)
            bar()

def fix_products(shop_url: str, api_key: str):
    def update_product_tax_and_price(product_element):
        id_tax_rules_group = product_element.find("id_tax_rules_group")
        if id_tax_rules_group is not None:
            id_tax_rules_group.text = "1"

        price = product_element.find("price")
        if price is not None:
            price.text = "{:.6f}".format(float(price.text) / 1.23)

    def remove_unnecessary_elements(product_element):
        for tag in ["manufacturer_name", "quantity", "low_stock_threshold"]:
            element = product_element.find(tag)
            if element is not None:
                product_element.remove(element)

    session = requests.Session()
    session.verify = False
    session.auth = requests.auth.HTTPBasicAuth(api_key, "")
    products_endpoint = f"{shop_url}/api/products"

    all_products_xml = session.get(products_endpoint).text
    root = ET.fromstring(all_products_xml)
    products = root.findall("products/product")

    with alive_bar(len(products), title="Correct tax") as bar:
        for product in products:
            product_id = int(product.attrib["id"])
            product_xml = session.get(f"{products_endpoint}/{product_id}").text
            product_root = ET.fromstring(product_xml)
            product_element = product_root.find("product")

            if product_element is not None:
                update_product_tax_and_price(product_element)
                remove_unnecessary_elements(product_element)

                id_element = product_element.find("id")
                if id_element is None:
                    id_element = ET.SubElement(product_element, "id")
                id_element.text = str(product_id)

                product_data = ET.tostring(product_root)
                response = session.put(f"{products_endpoint}/{product_id}", data=product_data)
                if not response.ok:
                    print(f"Failed tax set to 1 {product_id}")
                    print(response.text)
            bar()

def remove_all():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/xml"})
    session.verify = False
    session.auth = requests.auth.HTTPBasicAuth(API_KEY, "")

    products_xml = session.get(PRODUCT_PATH).text
    root = ET.fromstring(products_xml)
    products = root.findall("products/product")
    with alive_bar(len(products), title="Deleting products") as bar:
        for product in products:
            product_id = product.attrib["id"]
            session.delete(f"{PRODUCT_PATH}/{product_id}")
            bar()

    categories_xml = session.get(CATEGORY_PATH).text
    root = ET.fromstring(categories_xml)
    categories = root.findall("categories/category")
    with alive_bar(len(categories) - 2, title="Deleting categories") as bar:
        for category in categories:
            category_id = category.attrib["id"]
            if int(category_id) == 1 or int(category_id) == 2:
                continue
            session.delete(f"{CATEGORY_PATH}/{category_id}")
            bar()

    stock_xml = session.get(STOCK_PATH).text
    root = ET.fromstring(stock_xml)
    stock_items = root.findall("stock_availables/stock_available")
    with alive_bar(len(stock_items), title="Deleting stock items") as bar:
        for stock_item in stock_items:
            stock_id = stock_item.attrib["id"]
            session.delete(f"{STOCK_PATH}/{stock_id}")
            bar()

if __name__ == "__main__":
    remove_all()
    print("Deleted all content from prestashop")
    created_products = read_and_seed(JSON_DIR, product_limit=1000)
    print(f"Product imported to prestshop: {len(created_products)}")
    session = requests.Session()
    session.verify = False
    session.auth = requests.auth.HTTPBasicAuth(API_KEY, "")
    zero_stock(created_products[:10], session)
    fix_products(SHOP_URL, API_KEY)