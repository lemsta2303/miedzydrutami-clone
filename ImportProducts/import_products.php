<?php

// Konfiguracja
$api_url = 'http://localhost:8080/api'; 
$api_key = 'your_generated_api_key'; // Wstaw tutaj wygenerowany klucz API

// Funkcja do tworzenia kategorii
function create_category($name, $parent_id = 2) {
    global $api_url, $api_key;

    $link_rewrite = strtolower(str_replace(' ', '-', $name)); // Generowanie link_rewrite na podstawie nazwy

    $xml = new SimpleXMLElement('<prestashop/>');
    $category = $xml->addChild('category');
    $category->addChild('id_parent', $parent_id);
    $category->addChild('active', 1);
    $name_node = $category->addChild('name');
    $name_node->addChild('language', $name)->addAttribute('id', 1);
    $link_rewrite_node = $category->addChild('link_rewrite');
    $link_rewrite_node->addChild('language', $link_rewrite)->addAttribute('id', 1);

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $api_url . '/categories?schema=blank');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $xml->asXML());
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Basic ' . base64_encode($api_key . ':'),
        'Content-Type: application/xml'
    ]);

    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'Error:' . curl_error($ch);
    }
    curl_close($ch);

    $response_xml = new SimpleXMLElement($response);
    if (isset($response_xml->category->id)) {
        echo "Category created: " . $response_xml->category->id . "\n";
    } else {
        echo "Failed to create category: " . $name . "\n";
        echo "Response: " . $response . "\n";
    }

    return $response_xml;
}

// Funkcja do tworzenia produktów
function create_product($name, $price, $category_id) {
    global $api_url, $api_key;

    $link_rewrite = strtolower(str_replace(' ', '-', $name)); // Generowanie link_rewrite na podstawie nazwy

    $xml = new SimpleXMLElement('<prestashop/>');
    $product = $xml->addChild('product');
    $product->addChild('id_tax_rules_group', 1); // Ustawienie grupy reguł podatkowych
    $product->addChild('price', $price);
    $product->addChild('id_category_default', $category_id);
    $product->addChild('active', 1);
    $product->addChild('minimal_quantity', 1);
    $product->addChild('available_for_order', 1);
    $product->addChild('show_price', 1);
    $product->addChild('indexed', 1);
    $product->addChild('visibility', 'both');
    $product->addChild('name')->addChild('language', $name)->addAttribute('id', 1);
    $product->addChild('link_rewrite')->addChild('language', $link_rewrite)->addAttribute('id', 1);
    $product->addChild('reference', ''); // Dodanie pustego pola reference, aby uniknąć błędów
    $product->addChild('description')->addChild('language', '')->addAttribute('id', 1); // Dodanie pustego opisu
    $product->addChild('description_short')->addChild('language', '')->addAttribute('id', 1); // Dodanie pustego krótkiego opisu

    // Dodanie kategorii do produktu
    $associations = $product->addChild('associations');
    $categories = $associations->addChild('categories');
    $category = $categories->addChild('category');
    $category->addChild('id', $category_id);

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $api_url . '/products?schema=blank');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $xml->asXML());
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Basic ' . base64_encode($api_key . ':'),
        'Content-Type: application/xml'
    ]);

    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'Error:' . curl_error($ch);
    }
    curl_close($ch);

    $response_xml = new SimpleXMLElement($response);
    if (isset($response_xml->product->id)) {
        echo "Product created: " . $response_xml->product->id . "\n";
    } else {
        echo "Failed to create product: " . $name . "\n";
        echo "Response: " . $response . "\n";
    }

    return $response_xml;
}

// Słowniki do przechowywania ID kategorii i podkategorii
$categories = [];
$subcategories = [];

// Odczyt danych z pliku CSV
if (($handle = fopen('products.csv', 'r')) !== FALSE) {
    fgetcsv($handle); // Pomijanie nagłówka
    while (($data = fgetcsv($handle, 1000, ',')) !== FALSE) {
        list($category_name, $subcategory_name, $product_name, $product_price) = $data;

        // Tworzenie kategorii, jeśli nie istnieje
        if (!isset($categories[$category_name])) {
            $category = create_category($category_name);
            $categories[$category_name] = (int)$category->category->id;
        }

        // Tworzenie podkategorii, jeśli nie istnieje
        if (!isset($subcategories[$subcategory_name])) {
            $subcategory = create_category($subcategory_name, $categories[$category_name]);
            $subcategories[$subcategory_name] = (int)$subcategory->category->id;
        }

        // Tworzenie produktu
        create_product($product_name, $product_price, $subcategories[$subcategory_name]);
    }
    fclose($handle);
}

echo 'Import zakończony.';
?>