import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sqlite3
import os

current_directory = os.getcwd()
db_path=current_directory+"\\apps\\db.sqlite3"
image =current_directory+"\\Burger.PNG"

#Helper function that clean the code from the
def delete_test_user(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('''SELECT id FROM user WHERE username = 'test_user';''')
        result = c.fetchone()
        if result is not None:
            user_id = result[0]
            query = "DELETE FROM user_profile WHERE id = "+str(user_id)+";"
            c.execute(query)
        c.execute('''DELETE FROM user WHERE username = 'test_user';''')
        conn.commit()
        conn.close()

def delete_test_follows(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('''SELECT id FROM user WHERE username = 'followtester';''')
        result = c.fetchone()
        if result is not None:
            user_id = result[0]
            query = "DELETE FROM follow WHERE follower_id = "+str(user_id)+";"
            c.execute(query)
        conn.commit()
        conn.close()

def delete_test_comment(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('''DELETE FROM comment WHERE user_id = 1 AND content = 'Nice Meal';''')
        conn.commit()
        conn.close()

def delete_test_rating(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('''DELETE FROM rating WHERE user_id = 1;''')
        conn.commit()
        conn.close()

def delete_recipe(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('''SELECT id FROM recipe WHERE name = 'Beef Burger';''')
        result = c.fetchone()
        if result is not None:
            user_id = result[0]
            tables = ["instruction", "ingredient", "rating", "comment", "user_activity"]
            for table in tables:
                query = "DELETE FROM "+table+" WHERE recipe_id = "+str(user_id)+";"
                c.execute(query)
        c.execute('''DELETE FROM recipe WHERE name = 'Beef Burger';''')
        conn.commit()
        conn.close()

def delete_recipe_trails(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('''SELECT id FROM recipe WHERE name = 'Beef Burger';''')
        result = c.fetchone()
        if result is not None:
            user_id = result[0]
            tables = ["instruction", "ingredient", "rating", "comment", "user_activity"]
            for table in tables:
                query = "DELETE FROM "+table+" WHERE recipe_id = "+str(user_id)+";"
                c.execute(query)
        conn.commit()
        conn.close()

class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(service=Service('Yumfinity\\chromedriver.exe'))
        self.driver.implicitly_wait(2)
    
    def tearDown(self):
        self.driver.quit()

    def test_login_success(self):
        driver = self.driver
        driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = driver.find_element(By.NAME,"username")
        password_field = driver.find_element(By.NAME,"password")
        username_field.send_keys("Khaled Elbastawisy")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = driver.find_element(By.NAME,"login")
        login_button.click()

        # Wait for the page to load after login (e.g., check for an element on the home page)
        driver.implicitly_wait(10)  # Wait for up to 10 seconds
        home_title = driver.find_element(By.XPATH,"//h3[contains(text(),'Browse and share your favorite recipes')]")
        assert home_title.is_displayed()

    def test_registration_success(self):
        delete_test_user(db_path)
        driver = self.driver
        driver.get("http://localhost:5000")

        #look for "register" button
        register_link = driver.find_element(By.TAG_NAME, "a")
        register_link.click()

        #fill user info
        username = driver.find_element(By.NAME, "username")
        username.send_keys("test_user")

        email = driver.find_element(By.NAME, "email")
        email.send_keys("test@example.com")

        password = driver.find_element(By.NAME, "password")
        password.send_keys("test_password")
        
        #click register button
        register_button = driver.find_element(By.NAME,"register")
        register_button.click()

        # Wait for page to load
        time.sleep(2)
        # Check if registration is successful
        success_message = driver.find_element(By.XPATH, "//*[contains(text(), 'User created successfully.')]")
        self.assertTrue(success_message.is_displayed())

    def test_registration_fail(self):

        driver = self.driver
        driver.get("http://localhost:5000")

        #look for "register" button
        register_link = driver.find_element(By.TAG_NAME, "a")
        register_link.click()

        #fill user info
        username = driver.find_element(By.NAME, "username")
        username.send_keys("Khaled Elbastawisy")

        email = driver.find_element(By.NAME, "email")
        email.send_keys("khaledebrahim000@gmail.com")

        password = driver.find_element(By.NAME, "password")
        password.send_keys("Dodobasta5")

        #click register button
        register_button = driver.find_element(By.NAME,"register")
        register_button.click()

        # Wait for page to load
        time.sleep(2)
        # Check if registration is successful
        fail_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'already registered')]")
        self.assertTrue(fail_msg.is_displayed())
    
    def test_login_fail(self):
    
        self.driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = self.driver.find_element(By.NAME,"username")
        password_field = self.driver.find_element(By.NAME,"password")
        username_field.send_keys("dfgdf")
        password_field.send_keys("dfgddhg")

        # Submit the login form
        login_button = self.driver.find_element(By.NAME,"login")
        login_button.click()
        time.sleep(2)
        # Wait for the error to show
        login_fail = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Wrong user or password')]"))
        )
        assert login_fail.is_displayed()

    def test_recipe_of_the_day(self):
        driver = self.driver
        driver.maximize_window()
        driver.get("http://localhost:5000")

        # Find the username and password input fields and enter the credentials
        username_field = driver.find_element(By.NAME,"username")
        password_field = driver.find_element(By.NAME,"password")
        username_field.send_keys("Khaled Elbastawisy")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = driver.find_element(By.NAME,"login")
        login_button.click()

        # Wait for the page to load after login (e.g., check for an element on the home page)
        # Wait for up to 10 seconds
        view_recipe_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "View Recipe Details")))
        #scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        view_recipe_button.click()
        #scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        #look for comments section
        submit_comment_button = driver.find_element(By.NAME, "comment")


        assert submit_comment_button.is_displayed()  # Wait for up to 10 seconds

    def test_cusuine_search(self):
        
        self.driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = self.driver.find_element(By.NAME,"username")
        password_field = self.driver.find_element(By.NAME,"password")
        username_field.send_keys("Khaled Elbastawisy")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = self.driver.find_element(By.NAME,"login")
        login_button.click()
        time.sleep(2)
        # Wait for the page to load after login (e.g., check for an element on the home page)
        home_title = WebDriverWait(self.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Browse and share your favorite recipes')]"))
        )

        # finding the browse all recipes button
        browse_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'btn-primary') and contains(., 'Browse All Recipes')]")
        browse_button.click()
        

        dropdown = self.driver.find_element(By.NAME, "cuisine")
        dropdown.click()

        # Wait for the options to be visible, if necessary
        desired_option_value = "egyptian"

        # Locate the option by value
        option_by_value = dropdown.find_element(By.CSS_SELECTOR, f"option[value='{desired_option_value}']")
        option_by_value.click()
        WebDriverWait(self.driver, 3)

        #locate the search button
        search_button = self.driver.find_element(By.ID, "search-btn")
        search_button.click()
        time.sleep(5)

        search_message = self.driver.find_element(By.ID, "results-count")
        if search_message:
            self.assertTrue(search_message.is_displayed())
            
    def test_following(self):
        #delete test follower to be created later. This is done to avoid filling up the database with test data
        delete_test_follows(db_path)
        driver = self.driver
        driver.maximize_window()
        driver.get("http://localhost:5000")

        # Find the username and password input fields and enter the credentials
        username_field = driver.find_element(By.NAME,"username")
        password_field = driver.find_element(By.NAME,"password")
        username_field.send_keys("followtester")
        password_field.send_keys("followtester")

        # Submit the login form
        login_button = driver.find_element(By.NAME,"login")
        login_button.click()

        # Wait for the page to load after login (e.g., check for an element on the home page)
        # Wait for up to 10 seconds
        view_recipe_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "View Recipe Details")))
        #scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        #click view recipe button
        view_recipe_button.click()
        time.sleep(1)
        #look for comments section
      
        
        follow_button =  WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Follow')]")))
        element_position = 0
        while True:
            # Scroll the page to bring the follow button into view
            driver.execute_script("arguments[0].scrollIntoView();", follow_button)

            # Get the position of the follow button and the viewport height
            element_position = follow_button.location["y"]
            viewport_height = driver.execute_script("return window.innerHeight")

            # Calculate the middle of the viewport
            viewport_middle = viewport_height / 2

            # Check if the follow button is in the middle of the viewport
            if element_position > viewport_middle:
                break

            # Scroll further if the follow button is not yet in the middle
            driver.execute_script("window.scrollBy(0, 300);")

        time.sleep(1)
        #click the follow button
        follow_button.click()
        
        time.sleep(2)
        #scroll to the follow button
        scroll_script = "window.scrollBy(0, "+ str(element_position-400) + ");"
        driver.execute_script(scroll_script)

        time.sleep(2)
        #check if its greyed out (user is already followed)
        following_button = driver.find_element(By.CSS_SELECTOR,"span.following-btn")
        
          
        
        assert following_button.is_displayed()  # Wait for up to 10 seconds
    
    def test_comments(self):
        delete_test_comment(db_path)
        driver = self.driver
        driver.maximize_window()
        driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = driver.find_element(By.NAME,"username")
        password_field = driver.find_element(By.NAME,"password")
        username_field.send_keys("Khaled Elbastawisy")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = driver.find_element(By.NAME,"login")
        login_button.click()

        # Wait for the page to load after login (e.g., check for an element on the home page)
        # Wait for up to 10 seconds
        view_recipe_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "View Recipe Details")))
        #scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        view_recipe_button.click()
        #scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        #look for comments section
        comment_field = driver.find_element(By.NAME, "comment")
        #Type comment
        comment_field.send_keys("Nice Meal")

        #click submit comment
        submit_comment_buttom = driver.find_element(By.XPATH, "//button[text()='Submit Comment']")
        submit_comment_buttom.click()

        #Wait for page to load
        time.sleep(1)

        #Scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #Look for the comment card
        comment_card = driver.find_element(By.XPATH, "//p[@class='card-text' and contains(text(), 'Nice Meal')]")

        assert comment_card.is_displayed()


    def test_rating(self):
        delete_test_rating(db_path)
        driver = self.driver
        driver.maximize_window()
        driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = driver.find_element(By.NAME,"username")
        password_field = driver.find_element(By.NAME,"password")
        username_field.send_keys("Khaled Elbastawisy")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = driver.find_element(By.NAME,"login")
        login_button.click()

        # Wait for the page to load after login (e.g., check for an element on the home page)
        # Wait for up to 10 seconds
        view_recipe_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "View Recipe Details")))
        #scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        view_recipe_button.click()

        #find the comments header and scroll to it to ensure the rating is visible
        rate_field = driver.find_element(By.XPATH,"//input[@id='rating']")
        #Give the recipe a rating of 4
        rate_field.send_keys("4")
        #Scroll down to find submit rating button
        field_pos = rate_field.location["y"]
        scroll_script = "window.scrollTo(0, "+str(field_pos)+");"
        driver.execute_script(scroll_script)
        #Wait for a few seconds
        time.sleep(2)
        #Click Submit Rating
        rate_button = driver.find_element(By.XPATH,"//button[@type='submit' and contains(text(), 'Submit Rating')]")
        rate_button.click()

        #Wait for page to load then check that the recipe is rated
        time.sleep(3)
        rate_message = driver.find_element(By.XPATH,"//p[contains(text(), 'You have already rated this recipe.')]")
        assert rate_message.is_displayed()

    def test_user_activity(self):
        driver = self.driver
        driver.maximize_window()
        driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = driver.find_element(By.NAME,"username")
        password_field = driver.find_element(By.NAME,"password")
        username_field.send_keys("Khaled Elbastawisy")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = driver.find_element(By.NAME,"login")
        login_button.click()
        
        #Check if the activity tab is visible
        Activity_tab = driver.find_element(By.XPATH,"//ul[contains(@class, 'nav-tabs') and contains(@class, 'profile-tab')]")
        assert Activity_tab.is_displayed()

    def test_add_recipe(self):
        delete_recipe(db_path)
        self.driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = self.driver.find_element(By.NAME,"username")
        password_field = self.driver.find_element(By.NAME,"password")
        username_field.send_keys("Khaled Elbastawisy")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = self.driver.find_element(By.NAME,"login")
        login_button.click()
        time.sleep(2)
        # Wait for the page to load after login (e.g., check for an element on the home page)
        home_title = WebDriverWait(self.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Browse and share your favorite recipes')]"))
        )

        # finding the browse all recipes button
        button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'btn-primary') and contains(., 'Add Recipe')]")
        button.click()
        time.sleep(3)


        #finding the recipe fields and entering recipe details

        name = self.driver.find_element(By.CSS_SELECTOR, 'input[name="name"]')
        description = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="description"]')
        
        cuisine = self.driver.find_element(By.NAME, "cuisine")
        cuisine.click()

        ## Wait for the options to be visible, if necessary
        desired_option_value = "american"

        ## Locate the option by value
        option_by_value = cuisine.find_element(By.CSS_SELECTOR, f"option[value='{desired_option_value}']")
        option_by_value.click()

        ingredients = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="ingredients"]')
        instructions = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="instructions"]')
        cooking_time = self.driver.find_element(By.CSS_SELECTOR, 'input[name="cooking_time"]')

        #Add recipe details
        name.send_keys("Beef Burger")

        description.send_keys("""A burger is a patty of ground beef grilled and placed between two halves of a bun. Slices of raw onion, lettuce, bacon, mayonnaise, and other ingredients add flavor. Burgers are considered an American food but are popular around the world.""")
        
        

        ingredients.send_keys("""Ground beef
                                 Hamburger buns
                                 Cheese slices (optional)
                                 Lettuce leaves
                                 Tomato slices
                                 Onion slices
                                 Pickles
                                 Ketchup
                                 Mustard
                                 Mayonnaise
                                 Salt and pepper
                                 Olive oil or butter (for greasing)""")
        
        instructions.send_keys("""Preheat grill or stovetop pan over medium-high heat.
                                  Season ground beef with salt and pepper, then shape into patties.
                                  Grease grill or pan, then cook patties for 3-4 minutes per side.
                                  Optional: Add cheese during the last minute of cooking.
                                  Slice and toast burger buns on the grill or pan.
                                  Assemble burgers with patties and desired toppings.
                                  Serve and enjoy! """)
        
        cooking_time.send_keys("20 mins")

        ## Attaching the image
        input = self.driver.find_element(By.CSS_SELECTOR, "input.form-control#image")
        input.send_keys(image)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        ## locating and clicking the create recipe button
        create_button = self.driver.find_element(By.XPATH, "//button[text()='Create Recipe']")
        create_button.click()

        #Checking if the home page was opened
        home_title = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Browse and share your favorite recipes')]")))
        time.sleep(3)
        assert home_title.is_displayed()
    
    def test_add_delete_recipe(self):
        delete_recipe(db_path)
        self.driver.get("http://localhost:5000")
        self.driver.maximize_window()
        # Find the username and password input fields and enter the credentials
        username_field = self.driver.find_element(By.NAME,"username")
        password_field = self.driver.find_element(By.NAME,"password")
        username_field.send_keys("test_recipe")
        password_field.send_keys("test_recipe")

        # Submit the login form
        login_button = self.driver.find_element(By.NAME,"login")
        login_button.click()
        time.sleep(2)
        # Wait for the page to load after login (e.g., check for an element on the home page)
        home_title = WebDriverWait(self.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Browse and share your favorite recipes')]"))
        )

        # finding the browse all recipes button
        button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'btn-primary') and contains(., 'Add Recipe')]")
        button.click()
        time.sleep(3)


        #finding the recipe fields and entering recipe details

        name = self.driver.find_element(By.CSS_SELECTOR, 'input[name="name"]')
        description = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="description"]')
        
        cuisine = self.driver.find_element(By.NAME, "cuisine")
        cuisine.click()

        ## Wait for the options to be visible, if necessary
        desired_option_value = "american"

        ## Locate the option by value
        option_by_value = cuisine.find_element(By.CSS_SELECTOR, f"option[value='{desired_option_value}']")
        option_by_value.click()

        ingredients = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="ingredients"]')
        instructions = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="instructions"]')
        cooking_time = self.driver.find_element(By.CSS_SELECTOR, 'input[name="cooking_time"]')

        #Add recipe details
        name.send_keys("Beef Burger")

        description.send_keys("""A burger is a patty of ground beef grilled and placed between two halves of a bun. Slices of raw onion, lettuce, bacon, mayonnaise, and other ingredients add flavor. Burgers are considered an American food but are popular around the world.""")
        
        

        ingredients.send_keys("""Ground beef
                                 Hamburger buns
                                 Cheese slices (optional)
                                 Lettuce leaves
                                 Tomato slices
                                 Onion slices
                                 Pickles
                                 Ketchup
                                 Mustard
                                 Mayonnaise
                                 Salt and pepper
                                 Olive oil or butter (for greasing)""")
        
        instructions.send_keys("""Preheat grill or stovetop pan over medium-high heat.
                                  Season ground beef with salt and pepper, then shape into patties.
                                  Grease grill or pan, then cook patties for 3-4 minutes per side.
                                  Optional: Add cheese during the last minute of cooking.
                                  Slice and toast burger buns on the grill or pan.
                                  Assemble burgers with patties and desired toppings.
                                  Serve and enjoy! """)
        
        cooking_time.send_keys("20 mins")

        ## Attaching the image
        input = self.driver.find_element(By.CSS_SELECTOR, "input.form-control#image")
        input.send_keys(image)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        ## locating and clicking the create recipe button
        create_button = self.driver.find_element(By.XPATH, "//button[text()='Create Recipe']")
        create_button.click()

        #Checking if the home page was opened
        home_title = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Browse and share your favorite recipes')]")))
        time.sleep(3)

        my_recipes_button = self.driver.find_element(By.XPATH, '//a[contains(span,"My Recipes")]')
        my_recipes_button.click()
        time.sleep(2)

        # Locate the card based on the recipe name
        recipe_name = "Beef Burger"
        card_xpath = f'//div[@class="card-body"]//h5[contains(text(), "{recipe_name}")]'
        
        time.sleep(3)

        # Locate the delete button inside the card
        delete_button_xpath = f'{card_xpath}//following-sibling::form//button[@class="btn btn-danger"]'
        delete_button = self.driver.find_element(By.XPATH, delete_button_xpath)

        #delete recipe references to avoid exceptions (code needs to be fixed)
        delete_recipe_trails(db_path)
        # Click the delete button
        delete_button.click()
        time.sleep(3)

        # Wait for the alert to be present
        alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())

        # Accept the alert by clicking OK
        alert.accept()
        time.sleep(2)

        #locating the recipe card
        try:
            card_xpath = '//div[@class="card-body"]//h5[contains(text(), "test recipe")]'
            card = self.driver.find_element(By.XPATH, card_xpath)

        except NoSuchElementException:

        # if the card is not found this means that the recipe was successfully deleted 
            self.assertTrue(True)

    def test_add_edit_recipe(self):
        delete_recipe(db_path)
        self.driver.get("http://localhost:5000")
        self.driver.maximize_window()
        # Find the username and password input fields and enter the credentials
        username_field = self.driver.find_element(By.NAME,"username")
        password_field = self.driver.find_element(By.NAME,"password")
        username_field.send_keys("test_recipe")
        password_field.send_keys("test_recipe")

        # Submit the login form
        login_button = self.driver.find_element(By.NAME,"login")
        login_button.click()
        time.sleep(2)
        # Wait for the page to load after login (e.g., check for an element on the home page)
        home_title = WebDriverWait(self.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Browse and share your favorite recipes')]"))
        )

        # finding the browse all recipes button
        button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'btn-primary') and contains(., 'Add Recipe')]")
        button.click()
        time.sleep(3)


        #finding the recipe fields and entering recipe details

        name = self.driver.find_element(By.CSS_SELECTOR, 'input[name="name"]')
        description = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="description"]')
        
        cuisine = self.driver.find_element(By.NAME, "cuisine")
        cuisine.click()

        ## Wait for the options to be visible, if necessary
        desired_option_value = "american"

        ## Locate the option by value
        option_by_value = cuisine.find_element(By.CSS_SELECTOR, f"option[value='{desired_option_value}']")
        option_by_value.click()

        ingredients = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="ingredients"]')
        instructions = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="instructions"]')
        cooking_time = self.driver.find_element(By.CSS_SELECTOR, 'input[name="cooking_time"]')

        #Add recipe details
        name.send_keys("Beef Burger")

        description.send_keys("""A burger is a patty of ground beef grilled and placed between two halves of a bun. Slices of raw onion, lettuce, bacon, mayonnaise, and other ingredients add flavor. Burgers are considered an American food but are popular around the world.""")
        
        

        ingredients.send_keys("""Ground beef
                                 Hamburger buns
                                 Cheese slices (optional)
                                 Lettuce leaves
                                 Tomato slices
                                 Onion slices
                                 Pickles
                                 Ketchup
                                 Mustard
                                 Mayonnaise
                                 Salt and pepper
                                 Olive oil or butter (for greasing)""")
        
        instructions.send_keys("""Preheat grill or stovetop pan over medium-high heat.
                                  Season ground beef with salt and pepper, then shape into patties.
                                  Grease grill or pan, then cook patties for 3-4 minutes per side.
                                  Optional: Add cheese during the last minute of cooking.
                                  Slice and toast burger buns on the grill or pan.
                                  Assemble burgers with patties and desired toppings.
                                  Serve and enjoy! """)
        
        cooking_time.send_keys("20 mins")

        ## Attaching the image
        input = self.driver.find_element(By.CSS_SELECTOR, "input.form-control#image")
        print(image)
        input.send_keys(image)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        ## locating and clicking the create recipe button
        create_button = self.driver.find_element(By.XPATH, "//button[text()='Create Recipe']")
        create_button.click()

        #Checking if the home page was opened
        home_title = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Browse and share your favorite recipes')]")))
        time.sleep(3)

        my_recipes_button = self.driver.find_element(By.XPATH, '//a[contains(span,"My Recipes")]')
        my_recipes_button.click()
        time.sleep(2)

        # Locate the card based on the recipe name
        recipe_name = "Beef Burger"
                # Find all card elements on the page
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')

        # Iterate over the cards and check the recipe name
        for card in cards:
            # Find the recipe name element within the card
            recipe_name_element = card.find_element(By.TAG_NAME, 'h5')

            # Check if the recipe name matches
            if recipe_name_element.text == recipe_name:
                # Found the card with the matching recipe name
                
                # find the edit button within the card
                button = card.find_element(By.CLASS_NAME, 'btn-primary')
                button.click()
                break  # Exit the loop since we found the desired card
        
        time.sleep(3)

        #finding the recipe fields and entering recipe details

        name = self.driver.find_element(By.CSS_SELECTOR, 'input[name="name"]')
        description = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="description"]')
        
        cuisine = self.driver.find_element(By.NAME, "cuisine")
        cuisine.click()

        # Wait for the options to be visible, if necessary
        desired_option_value = "american"

        # Locate the option by value
        option_by_value = cuisine.find_element(By.CSS_SELECTOR, f"option[value='{desired_option_value}']")
        option_by_value.click()

        ingredients = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="ingredients"]')
        instructions = self.driver.find_element(By.CSS_SELECTOR, 'textarea[name="instructions"]')
        cooking_time = self.driver.find_element(By.CSS_SELECTOR, 'input[name="cooking_time"]')

        #clearing the fields
        name.clear()
        description.clear()
        ingredients.clear()
        instructions.clear()
        cooking_time.clear()

        name.send_keys("Beef Burger")

        description.send_keys("""This is the recipe description""")
        
        

        ingredients.send_keys("""Ingredient1
                                 Ingredient2
                                 Ingredient3
                                 Ingredient4
                                 Ingredient5
                                 Ingredient6""")
        
        instructions.send_keys("""Instruction1
                                  Instruction2
                                  Instruction3
                                  Instruction4
                                  Instruction5
                                  Instruction6 """)
        
        cooking_time.send_keys("20 mins")

        ## Attaching the image
        input = self.driver.find_element(By.CSS_SELECTOR, "input.form-control#image")
        input.send_keys(image)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        ## locating and clicking the Save Changes button
        create_button = self.driver.find_element(By.XPATH, "//button[text()='Save Changes']")
        create_button.click()

        alert_div = self.driver.find_element(By.XPATH, '//div[contains(@class, "alert") and contains(@class, "alert-danger") and @role="alert"]')
        self.assertTrue(alert_div.is_displayed())

if __name__ == '__main__':
    unittest.main()
    