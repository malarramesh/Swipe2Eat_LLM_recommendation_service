# llm_aggregator_v3.py

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


# -------------------------------
# 🔌 DB CONNECTION
# -------------------------------
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )


# -------------------------------
# 💰 BUDGET MAPPING
# -------------------------------
def map_budget(value):
    if not value:
        return 10.0

    value = str(value).lower()

    if value == "low":
        return 10.0
    elif value == "medium":
        return 15.0
    elif value == "high":
        return 25.0
    else:
        try:
            return float(value)
        except:
            return 10.0


# -------------------------------
# 🌶️ SPICE MAPPING (SAFE)
# -------------------------------
def map_spice(value):
    if not value:
        return 3

    if isinstance(value, int):
        return value

    value = str(value).lower()

    if value == "mild":
        return 2
    elif value == "medium":
        return 3
    elif value == "hot":
        return 5
    else:
        try:
            return int(value)
        except:
            return 3
# -------------------------------
# 🔹 GET ALL USER IDS (FOR RANDOM SELECTION)
# -------------------------------
def get_all_user_ids():
    """
    Fetch all active user IDs from the database.
    Used to pick a random user dynamically.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users")  # optionally: WHERE active = true
        user_ids = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print("DB ERROR (get_all_user_ids):", e)
        user_ids = []
    finally:
        cursor.close()
        conn.close()

    return user_ids

# -------------------------------
# 🧠 AGGREGATOR
# -------------------------------
def get_user_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Basic user
    cursor.execute("SELECT name, city FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return None

    profile = {
        "name": row[0],
        "city": row[1]
    }

    # Budget
    cursor.execute("""
        SELECT budget
        FROM user_budget_preference
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    profile["budget"] = map_budget(row[0]) if row else 10.0

    # Spice
    cursor.execute("""
        SELECT spice_level
        FROM user_spice_preference
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    profile["spice_level"] = map_spice(row[0]) if row else 3

    # Dietary
    cursor.execute("""
        SELECT diet_type, allergies, forbidden_items
        FROM user_dietary_preference
        WHERE user_id = %s
    """, (user_id,))
    row = cursor.fetchone()
    profile["dietary_preferences"] = {
        "diet_type": row[0] if row else None,
        "allergies": row[1] if row else None,
        "forbidden_items": row[2] if row else None
    }

    # Cuisines
    cursor.execute("""
        SELECT c.name
        FROM cuisine c
        JOIN user_cuisine_preference ucp ON c.id = ucp.cuisine_id
        WHERE ucp.user_id = %s
    """, (user_id,))
    profile["favorite_cuisines"] = [r[0] for r in cursor.fetchall()]

    # Likes / Dislikes
    cursor.execute("""
        SELECT f.name, ufp.status
        FROM food f
        JOIN user_food_preference ufp ON f.id = ufp.food_id
        WHERE ufp.user_id = %s
    """, (user_id,))

    likes, dislikes = [], []
    for name, status in cursor.fetchall():
        if status:
            likes.append(name)
        else:
            dislikes.append(name)

    profile["likes"] = likes
    profile["dislikes"] = dislikes

    # Available food
    cursor.execute("SELECT name, price, spice_level FROM food")
    profile["available_food"] = [
        {
            "name": r[0],
            "price": float(r[1]),
            "spice_level": map_spice(r[2])
        }
        for r in cursor.fetchall()
    ]

    # ⚡ ENSURE ALL LISTS ARE SAFE
    profile["favorite_cuisines"] = profile.get("favorite_cuisines") or []
    profile["likes"] = profile.get("likes") or []
    profile["dislikes"] = profile.get("dislikes") or []
    profile["available_food"] = profile.get("available_food") or []

    cursor.close()
    conn.close()

    return profile