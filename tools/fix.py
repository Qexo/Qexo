import pymysql
import psycopg2
import pymongo
from pymongo import MongoClient
import getpass

def get_db_connection(db_type, db_info):
    try:
        if db_info.get('conn_string'):
            if db_type == "pgsql":
                conn = psycopg2.connect(db_info['conn_string'])
            elif db_type == "mysql":
                conn = pymysql.connect(db_info['conn_string'])
            elif db_type == "mongodb":
                conn = MongoClient(db_info['conn_string'])
            else:
                raise ValueError("Unsupported database type")
        else:
            if db_type == "pgsql":
                conn = psycopg2.connect(database=db_info['name'], user=db_info['user'], password=db_info['password'],
                                        host=db_info['host'], port=db_info['port'])
            elif db_type == "mysql":
                conn = pymysql.connect(database=db_info['name'], user=db_info['user'], password=db_info['password'],
                                       host=db_info['host'], port=db_info['port'])
            elif db_type == "mongodb":
                conn = MongoClient(f"mongodb://{db_info['user']}:{db_info['password']}@{db_info['host']}:{db_info['port']}/{db_info['name']}")
            else:
                raise ValueError("Unsupported database type")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def reset_admin_password(conn, db_type):
    user = input("Enter admin username: ")
    new_password = "pbkdf2_sha256$260000$oBl27LgTT7KsL1NV66HJ2P$BC59jjYqWo5vKQCpiS3s0OmTg52KphBtxOo1tUEdQ1c="
    try:
        if db_type in ["pgsql", "mysql"]:
            cursor = conn.cursor()
            cursor.execute("UPDATE auth_user SET password=%s WHERE username=%s", (new_password,user))
            conn.commit()
            cursor.close()
        elif db_type == "mongodb":
            db = conn[db_info['name']]
            db.users.update_one({"username": user}, {"$set": {"password": new_password}})
        print("Admin password has been reset to 12345678")
    except Exception as e:
        print(f"Error resetting admin password: {e}")

def update_cdn_to_unpkg(conn, db_type):
    try:
        if db_type in ["pgsql", "mysql"]:
            cursor = conn.cursor()
            cursor.execute("UPDATE hexoweb_settingmodel SET content='https://unpkg.com/qexo-static@{version}/qexo' WHERE name='CDN_PREV'")
            conn.commit()
            cursor.close()
        elif db_type == "mongodb":
            db = conn[db_info['name']]
            db.settings.update_one({"name": "CDN_PREV"}, {"$set": {"content": "https://unpkg.com/qexo-static@{version}/qexo"}})
        print("CDN has been updated to unpkg successfully.")
    except Exception as e:
        print(f"Error updating CDN: {e}")

def main():
    db_type = input("Select database type (pgsql/mysql/mongodb): ").strip().lower()
    
    use_conn_string = input("Do you want to use a connection string? (yes/no): ").strip().lower()
    if use_conn_string == "yes":
        conn_string = input("Enter the connection string: ").strip()
        db_info = {
            'conn_string': conn_string
        }
    else:
        db_info = {
            'name': input("Enter database name: ").strip(),
            'user': input("Enter database user: ").strip(),
            'password': getpass.getpass("Enter database password: ").strip(),
            'host': input("Enter database host: ").strip(),
            'port': input("Enter database port: ").strip(),
        }

    conn = get_db_connection(db_type, db_info)
    if not conn:
        print("Failed to connect to the database. Exiting.")
        return

    action = input("Select an action to perform (1: Reset user password to 12345678, 2: Update CDN to unpkg): ").strip()
    if action == "1":
        reset_admin_password(conn, db_type)
    elif action == "2":
        update_cdn_to_unpkg(conn, db_type)
    else:
        print("Invalid action selected.")

    if db_type in ["pgsql", "mysql"]:
        conn.close()

if __name__ == "__main__":
    main()
