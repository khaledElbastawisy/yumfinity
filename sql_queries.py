import sqlite3
import os

path=r"C:\Users\moham\Downloads\swe-proj\Yumfinity\apps\db.sqlite3"
# Get the absolute path to the current directory



conn = sqlite3.connect(path)
c = conn.cursor()

#c.execute('''DROP TABLE IF EXISTS Users;''')

c.execute('''DELETE FROM Ingredient WHERE recipe_id = 9;''')


#c.execute('''DROP TABLE IF EXISTS Comment ;''')
#c.execute('''DROP TABLE IF EXISTS Rating ;''')
#c.execute('''DROP TABLE IF EXISTS Recipe ;''')
#c.execute('''DROP TABLE IF EXISTS User;''')
#c.execute('''DROP TABLE IF EXISTS Instruction;''')
#c.execute('''DROP TABLE IF EXISTS Ingredient;''')
#c.execute('''DROP TABLE IF EXISTS User_Profile;''')
#c.execute('''DROP TABLE IF EXISTS User_Activity;''')
#c.execute('''DROP TABLE IF EXISTS Follow;''')







conn.commit()
conn.close()
# Connect to the database using the absolute path to the database file
# conn = sqlite3.connect(path)

# # Create a cursor to execute queries
# cursor = conn.cursor()

# # Add some sample data to the recipes table
# data = [
#     (1, 'Italian', 'Spaghetti Carbonara', 4, 'Delicious!', 1),
#     (2, 'Mexican', 'Chicken Enchiladas', 3, 'A bit spicy for my taste', 2),
#     (3, 'Chinese', 'Kung Pao Chicken', 5, 'Amazing recipe, highly recommend', 3),
#     (4, 'Indian', 'Butter Chicken', 4, 'Creamy and flavorful', 1),
#     (5, 'French', 'Beef Bourguignon', 5, 'A classic dish that never disappoints', 2),
# ]

# for recipe in data:
#     cursor.execute('INSERT INTO recipes VALUES (?, ?, ?, ?, ?, ?)',recipe)

# # Commit the changes
# conn.commit()

# # Close the connection
# conn.close()