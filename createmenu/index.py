import requests
import json
import sys
import io
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT token obtained from authentication
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL25ndXllbm5nb2N0dWFuMDcuY29tIiwiaWF0IjoxNzIxOTg0MDM2LCJuYmYiOjE3MjE5ODQwMzYsImV4cCI6MTcyMjU4ODgzNiwiZGF0YSI6eyJ1c2VyIjp7ImlkIjoiMSJ9fX0.0xQEnLNrz86Z-JtG-nbAuej60rrO7nOCfZFgJdLlh50'
base_url = 'https://nguyenngoctuan07.com/wp-json'

# Thiết lập mã hóa UTF-8 cho stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Tạo session cho requests
session = requests.Session()
session.headers.update({'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})

def check_auth():
    url = f"{base_url}/wp/v2/users/me"
    response = session.get(url)
    if response.status_code != 200:
        logger.error("Authentication failed. Please check your token.")
        sys.exit(1)
    logger.info("Authentication successful.")

def check_endpoints():
    endpoints = ['/wp/v2/menus', '/wp/v2/menu-items']
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        response = session.get(url)
        if response.status_code == 404:
            logger.error(f"Endpoint {endpoint} not found. Please check your API or installed plugins.")
            sys.exit(1)
    logger.info("All required endpoints are available.")

def get_category_and_subcategories(cat_id):
    def get_subcategories(parent_id):
        url = f"{base_url}/wc/v3/products/categories?parent={parent_id}"
        response = session.get(url)
        
        if response.status_code != 200:
            logger.error(f"Error: Received status code {response.status_code}")
            return []

        try:
            subcategories = response.json()
            for subcat in subcategories:
                subcat['children'] = get_subcategories(subcat['id'])
            return subcategories
        except json.JSONDecodeError:
            logger.error("Error: Failed to decode JSON response for subcategories")
            logger.error(f"Response content: {response.text}")
            return []

    url = f"{base_url}/wc/v3/products/categories/{cat_id}"
    response = session.get(url)
    
    if response.status_code != 200:
        logger.error(f"Error: Received status code {response.status_code}")
        return None

    try:
        category = response.json()
        category['subcategories'] = get_subcategories(cat_id)
        logger.info(f"Category and subcategories retrieved: {json.dumps(category, ensure_ascii=False, indent=4)}")
        return category
    except json.JSONDecodeError:
        logger.error("Error: Failed to decode JSON response")
        logger.error(f"Response content: {response.text}")
        return None

def create_menu(category):
    menu_name = category['name']
    url = f"{base_url}/wp/v2/menus"
    
    # Check if menu already exists
    response = session.get(url)
    if response.status_code != 200:
        logger.error(f"Error: Received status code {response.status_code} while fetching menus")
        return

    try:
        menus = response.json()
    except json.JSONDecodeError:
        logger.error("Error: Failed to decode JSON response while fetching menus")
        logger.error(f"Response content: {response.text}")
        return

    menu_id = next((menu['id'] for menu in menus if menu['name'] == menu_name), None)

    # Create menu if it doesn't exist
    if not menu_id:
        data = {
            'name': menu_name,
            'slug': menu_name.lower().replace(' ', '-')
        }
        response = session.post(url, json=data)
        
        if response.status_code != 201:
            logger.error(f"Error: Received status code {response.status_code} while creating menu")
            logger.error(f"Response content: {response.text}")
            return

        try:
            menu_id = response.json()['id']
        except json.JSONDecodeError:
            logger.error("Error: Failed to decode JSON response while creating menu")
            logger.error(f"Response content: {response.text}")
            return

    # Clear existing menu items
    clear_menu_items(menu_id)

    # Add menu items
    add_menu_items(menu_id, category['subcategories'])

    logger.info(f"Menu '{menu_name}' creation/update completed.")

def clear_menu_items(menu_id):
    url = f"{base_url}/wp/v2/menu-items"
    response = session.get(url, params={'menus': menu_id})

    if response.status_code != 200:
        logger.error(f"Error: Received status code {response.status_code} while fetching menu items")
        return

    try:
        items = response.json()
    except json.JSONDecodeError:
        logger.error("Error: Failed to decode JSON response while fetching menu items")
        logger.error(f"Response content: {response.text}")
        return

    for item in items:
        delete_url = f"{url}/{item['id']}"
        session.delete(delete_url)

def add_menu_items(menu_id, subcategories, parent_id=0):
    url = f"{base_url}/wp/v2/menu-items"

    for subcategory in subcategories:
        subcategory_data = {
            'title': subcategory['name'],
            'menu_order': 1,
            'type': 'taxonomy',
            'status': 'publish',
            'menus': menu_id,
            'object': 'product_cat',
            'object_id': subcategory['id'],
            'parent': parent_id
        }
        response = session.post(url, json=subcategory_data)
        
        if response.status_code != 201:
            logger.error(f"Error: Received status code {response.status_code} while adding subcategory menu item")
            logger.error(f"Response content: {response.text}")
            continue
        else:
            logger.info(f"Added menu item: {subcategory['name']}")
            
        # If this subcategory has children, add them recursively
        if subcategory['children']:
            try:
                new_parent_id = response.json()['id']
                add_menu_items(menu_id, subcategory['children'], new_parent_id)
            except json.JSONDecodeError:
                logger.error("Error: Failed to decode JSON response while adding child menu item")
                logger.error(f"Response content: {response.text}")

if __name__ == "__main__":
    check_auth()
    check_endpoints()
    cat_id = input("Enter the category ID: ")
    category = get_category_and_subcategories(cat_id)
    if category:
        create_menu(category)
    else:
        logger.warning("Category not found. Menu not created.")