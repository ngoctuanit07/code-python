import requests
import json
import sys
import io
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT token obtained from authentication
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2hhbmduaGF0YmFuLnZuIiwiaWF0IjoxNzI3OTE2NjMzLCJuYmYiOjE3Mjc5MTY2MzMsImV4cCI6MTcyODUyMTQzMywiZGF0YSI6eyJ1c2VyIjp7ImlkIjoiMSJ9fX0.nnU_MVwV6yk42TseK4z59MqHuugZHCMuPZTu_blvjsE'
base_url = 'https://hangnhatban.vn/wp-json'

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

def get_all_categories():
    url = f"{base_url}/wc/v3/products/categories"
    params = {'per_page': 100}
    response = session.get(url, params=params)
    
    if response.status_code != 200:
        logger.error(f"Error: Received status code {response.status_code}")
        return []

    try:
        categories = response.json()
        return categories
    except json.JSONDecodeError:
        logger.error("Error: Failed to decode JSON response for categories")
        logger.error(f"Response content: {response.text}")
        return []

def get_subcategories(parent_id):
    url = f"{base_url}/wc/v3/products/categories"
    params = {'parent': parent_id, 'per_page': 100}
    response = session.get(url, params=params)
    
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

def get_category_and_subcategories(cat_id):
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

def delete_level_4_categories():
    categories = get_all_categories()
    
    if not categories:
        logger.warning("No categories found.")
        return

    # Duyệt qua tất cả các danh mục để tìm danh mục cấp 4
    for category in categories:
        if category['parent'] != 0:
            continue

        subcategories = get_subcategories(category['id'])
        for subcategory in subcategories:
            if subcategory['children']:
                for child in subcategory['children']:
                    if child['children']:
                        for level_4_category in child['children']:
                            delete_category(level_4_category['id'])

if __name__ == "__main__":
    check_auth()
    check_endpoints()
    
    # Lựa chọn chức năng
    choice = input("Enter '1' to create menu, '2' to get parent categories, or '3' to delete level 4 categories: ")
    
    if choice == '1':
        cat_id = input("Enter the category ID: ")
        category = get_category_and_subcategories(cat_id)
        if category:
            create_menu(category)
        else:
            logger.warning("Category not found. Menu not created.")
    elif choice == '2':
        parent_categories = get_parent_categories()
        if parent_categories:
            logger.info(f"Parent categories retrieved successfully.")
        else:
            logger.warning("No parent categories found.")
    elif choice == '3':
        delete_level_4_categories()
    else:
        logger.error("Invalid choice. Exiting.")