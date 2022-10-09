import os
import psycopg2
from flask import Blueprint, request

from Functions.select_items import select_items

items = Blueprint('items_blueprint', __name__)

url = os.environ.get("DATABASE_URI")  # gets variables from environment
connection = psycopg2.connect(url)

#get all items, create item
@items.route('/', methods=['GET', 'POST'])
def get_create_items():
    if request.method == 'POST':
        item = request.get_json()
        values = list(item.values())
        with connection:
                with connection.cursor() as cursor:
                    try:
                        cursor.execute("""INSERT INTO items (title, type, status, category, subcategory, colour, description, last_location, found_lost_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
                    except:
                        return {"error": "Validation failed."}, 400

    with connection:
        with connection.cursor() as cursor:
            items = select_items(cursor)
        return items

#get one user, delete one user, edit one user
@items.route('/<int:id>', methods=['GET', 'DELETE', 'PUT'])
def item(id):
    if request.method == 'DELETE':
        with connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT FROM items WHERE id={id}")
                    check_exist = cursor.fetchall()
                    print(check_exist)
                    if len(check_exist) == 0:
                        return {"error": "Item not found."}, 404
                    else:
                        cursor.execute(f"DELETE FROM items WHERE id={id}")
                        return {"msg": "Successfully deleted item."}, 200

    elif request.method == 'PUT':
        item = request.get_json()
        values = list(item.values())
        values.append(id)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT FROM items WHERE id={id}")
                check_exist = cursor.fetchall()
                if len(check_exist) == 0:
                    return {"error": "Item not found."}, 404
                else:
                    try:
                        cursor.execute("UPDATE items SET title=%s, type=%s, status=%s, category=%s, subcategory=%s, colour=%s, description=%s, last_location=%s, found_lost_by=%s, retrieved_by=%s WHERE id=%s", values)
                    except:
                        return {"error": "Validation failed."}, 400
    with connection:
        with connection.cursor() as cursor:
            item = select_items(cursor, id)
            if len(item) == 0:
                return {"error": "Item not found."}, 404

        return item[0], 200

# search items based on input and filters and sort_by
@items.route('/search', methods=['GET'])
def search():
    query = request.args
    with connection:
            with connection.cursor() as cursor:
                items = select_items(cursor, query=query)
    return items, 200