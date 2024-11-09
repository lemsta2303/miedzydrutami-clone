import os
import requests
from bs4 import BeautifulSoup

base_url = "https://miedzydrutami.pl/sklep/"
image_folder = "../ScrapResults/Images"
def get_products(page):
    url = f"{base_url}page/{page}/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page {page}\n")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='product-inner')

    if not products:
        print(f"No products found on page {page}, {url}")
        return None

    product_data = []
    print(f"Found {len(products)} products on page {page}\n")
    for product in products:
        name = product.find('h2', class_='woocommerce-loop-product__title').text.strip() if product.find('h2',
                                                                                                         class_='woocommerce-loop-product__title') else "N/A"
        price = product.find('span', class_='woocommerce-Price-amount').text.strip() if product.find('span',
                                                                                                     class_='woocommerce-Price-amount') else "N/A"
        link = product.find('a', class_='woocommerce-LoopProduct-link')['href'] if product.find('a',
                                                                                                class_='woocommerce-LoopProduct-link') else "N/A"

        image_tag = product.find('img', class_='attachment-woocommerce_thumbnail')
        image_url = image_tag['src'] if image_tag else None
        image_filename = None
        if image_url:
            image_filename = download_image(image_url, name)

        product_data.append({
            "name": name,
            "price": price,
            "link": link,
            "image_filename": image_filename
        })

    return product_data

def save_to_file(data):
    with open('../ScrapResults/products.txt', 'w') as file:
        for product in data:
            file.write(f"{product['name']}, {product['price']}, {product['link']}\n")


def download_image(url, product_name):
    image_filename = f"{product_name.replace(' ', '_').replace('/', '_')}.jpg"
    image_path = os.path.join(image_folder, image_filename)

    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(image_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Image saved as {image_filename}")
            return image_filename
        else:
            print(f"Failed to download image: {url}")
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

all_products = []
page = 1
while True:
    products = get_products(page)
    if not products:
        break
    all_products.extend(products)
    print(f"Collected {len(products)} products from page {page}")
    page += 1

print(f"Total products collected: {len(all_products)}\n")
for product in all_products:
    print(product)

save_to_file(all_products)
