import sqlite3
import os

def delete_recipe():
        path=r"K:\Software Engineering\\Yumfinity\\apps\db.sqlite3"
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('''SELECT id FROM recipe WHERE name = 'dfc';''')
        result = c.fetchone()
        if result is not None:
            user_id = result[0]
            print(user_id)
            tables = ["instruction", "ingredient", "rating", "comment", "user_activity"]
            for table in tables:
                query = "DELETE FROM "+table+" WHERE recipe_id = "+str(user_id)+";"
                c.execute(query)
        c.execute('''DELETE FROM recipe WHERE name = 'dfc';''')
        conn.commit()
        conn.close()

delete_recipe()


