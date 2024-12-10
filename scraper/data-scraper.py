import os
import json
import requests
from lxml import html, etree
from urllib.parse import urljoin
from alive_progress import alive_bar

SHOP_URL = 'https://miedzydrutami.pl'
DESTINATION_DIR = '../scraper-data'
DESTINATION_JSON = os.path.join(DESTINATION_DIR, 'data.json')
IMAGES_DIR = os.path.join(DESTINATION_DIR, 'images')

os.makedirs(IMAGES_DIR, exist_ok=True)

def clean_images_folder():
    for filename in os.listdir(IMAGES_DIR):
        file_path = os.path.join(IMAGES_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print(f"Cleaned the images folder: {IMAGES_DIR}")

def download_image(image_url: str, local_path: str):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        else:
            print(f"Failed to download image: {image_url}")
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")

def get_product_details(product_link: str, max_images: int = 5):
    response = requests.get(product_link)
    if response.status_code != 200:
        print(f"Failed to fetch product: {product_link}")
        return None

    product_root = html.fromstring(response.content, parser=html.HTMLParser(encoding='utf-8'))

    name = product_root.xpath('//h1[@class="product_title entry-title"]/text()')
    price = [p.strip() for p in product_root.xpath('//span[@class="woocommerce-Price-amount amount"]/bdi/text()')]

    description_element = product_root.xpath('//div[@id="tab-description"]')
    description = ''.join([etree.tostring(child, encoding='unicode', method='html') for child in description_element[0].iterchildren()]) if description_element else None

    short_description_element = product_root.xpath('//div[@class="woocommerce-product-details__short-description"]/*')
    short_description = ''.join([html.tostring(child, encoding='unicode', method='html') for child in short_description_element])

    if len(short_description) > 950:
        short_description = short_description[:950] + "..."

    image_elements = product_root.xpath('//div[@class="woocommerce-product-gallery__image"]//a/@href')
    images = []
    for img_url in image_elements[:max_images]:
        img_url = urljoin(SHOP_URL, img_url)
        
        img_filename = os.path.basename(img_url)
        local_img_path = os.path.join(IMAGES_DIR, img_filename)
        
        download_image(img_url, local_img_path)
        
        images.append({
            "url-image": img_url,
            "local-path": os.path.relpath(local_img_path, DESTINATION_DIR).replace("images", "scraper-data/images")
        })

    product_details = {
        "name": name[0] if name else None,
        "price": price[0] if price else None,
        "images": images,
        "description": description,
        "short-description": short_description,
    }

    return product_details

def get_products(subcategory_link: str, max_products: int = 1000, max_images: int = 5, bar=None):
    response = requests.get(subcategory_link)
    if response.status_code != 200:
        print(f"Failed to fetch subcategory: {subcategory_link}")
        return []

    subcategory_root = html.fromstring(response.content, parser=html.HTMLParser(encoding='utf-8'))

    product_links = subcategory_root.xpath('//*[@id="rz-shop-content"]/ul/li/div/div[1]/div[1]/a/@href')
    product_links = product_links[:max_products]

    products = []
    for product_link in product_links:
        product_details = get_product_details(product_link, max_images=max_images)
        if product_details:
            products.append(product_details)
        if bar:
            bar()

    return products

def get_subcategories(subcategory_element, bar=None, max_products: int = 1000, max_images: int = 5):
    subcategory_links = subcategory_element.xpath('./ul/li/a')
    subcategories = {}
    for subcategory in subcategory_links:
        subcategory_name = subcategory.text.strip()
        subcategory_link = subcategory.get('href')
        
        products = get_products(subcategory_link, max_products=max_products, max_images=max_images, bar=bar)

        subcategories[subcategory_name] = {
            'subcategory-link': subcategory_link,
            'products': products
        }
    return subcategories

def get_categories(main_root: html.HtmlElement, bar=None, max_products: int = 2, max_images: int = 5):
    category_elements = main_root.xpath('//*[@id="menu-menu-glowne"]/li[2]/ul/li/div')

    categories = {}
    for category_element in category_elements:
        category_name_element = category_element.xpath('./a')
        if not category_name_element:
            continue
        category_name = category_name_element[0].text.strip()
        category_link = category_name_element[0].get('href')

        subcategories = get_subcategories(category_element, bar=bar, max_products=max_products, max_images=max_images)

        categories[category_name] = {
            'category-link': category_link,
            'subcategories': subcategories
        }

    return categories

def scraper(main_page: str, max_products: int = 1000, max_images: int = 5):
    clean_images_folder()

    response = requests.get(main_page)
    if response.status_code != 200:
        print(f"Failed to fetch {main_page}: {response.status_code}")
        return

    main_root = html.fromstring(response.content, parser=html.HTMLParser(encoding='utf-8'))
    category_elements = main_root.xpath('//*[@id="menu-menu-glowne"]/li[2]/ul/li/div')

    total_products = 0
    for category_element in category_elements:
        subcategory_links = category_element.xpath('./ul/li/a')
        for subcategory in subcategory_links:
            subcategory_link = subcategory.get('href')
            response = requests.get(subcategory_link)
            if response.status_code == 200:
                subcategory_root = html.fromstring(response.content, parser=html.HTMLParser(encoding='utf-8'))
                product_links = subcategory_root.xpath('//*[@id="rz-shop-content"]/ul/li/div/div[1]/div[1]/a/@href')
                total_products += min(len(product_links), max_products)

    with alive_bar(total_products, title="Fetching products") as bar:
        categories = get_categories(main_root, bar=bar, max_products=max_products, max_images=max_images)

    os.makedirs(DESTINATION_DIR, exist_ok=True)
    with open(DESTINATION_JSON, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=4)

    print(f"Data has been saved to {DESTINATION_JSON}")

if __name__ == '__main__':
    scraper(SHOP_URL, max_products=1000, max_images=5)