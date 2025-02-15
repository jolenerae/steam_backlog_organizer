import bs4
import csv
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Steam:
    def __init__(self, driver, write_header_count):
        """Declare values needed for the class.

        Args:
            driver (class): Firefox webdriver
        """
        self.driver = driver
        self.game_dict = {}
        self.write_header_count = write_header_count

        # Replace with your own profile link
        user_url = "https://steamdb.info/calculator/76561198061704008/?cc=us&all_games"
        self.driver.get(user_url)
        print("Acquiring url data...")

        # get page to display every game
        wait = WebDriverWait(self.driver, 10)
        page_dropdown = wait.until(EC.presence_of_element_located((By.ID, "dt-length-0")))
        page_dropdown.click()
        all_games = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/select/option[8]")))
        all_games.click()

        self.soup = bs4.BeautifulSoup(self.driver.page_source, "lxml")

    def write(self):
        """Opens and writes the data to the csv file."""
        with open("steam_backlog.csv", "a", newline="", encoding="utf-8") as steam_file:
            fieldnames = [
                "Game Title",
                "Hours Played",
            ]

            csv_writer = csv.DictWriter(steam_file, fieldnames=fieldnames)

            # Checks if the header row has already been written
            if self.write_header_count == 0:
                csv_writer.writeheader()

            csv_writer.writerow(self.game_dict)

            # Checks if there is a game being written to the file
            if "Game Title" in self.game_dict:
                print(f"Writing {self.game_dict['Game Title']} to file")

def main():
    write_header_count = 0
    print("Initializing webdriver...")

    # Make the webdriver run in headless mode
    options = webdriver.FirefoxOptions()
    options.headless = True

    # Replace the executable path with the path to your webdriver download
    service = FirefoxService(executable_path=r"C:\Users\14698\Documents\GitHub\steam_backlog_organizer\geckodriver.exe")
    driver = webdriver.Firefox(
        service=service, options=options
    )

    # Make a new profile object
    profile = Steam(driver, write_header_count)

    # get a list of all game entries
    tbody = driver.find_element(By.XPATH, "/html/body/div[4]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/table/tbody")
    game_entries = tbody.find_elements(By.CLASS_NAME, "app")

    # Keep looping for every game in the users library
    for entry in (game_entries):
        game_name = entry.find_element(By.CLASS_NAME, "text-left").text

        columns = entry.find_elements(By.CLASS_NAME, "dt-type-numeric")
        # hours is always at index 2 under the dt-type-numeric class
        hours_played = columns[2].text

        # writing info into dictionary
        if game_name is not None:
            profile.game_dict["Game Title"] = game_name

        if hours_played is not None:
            profile.game_dict["Hours Played"] = hours_played

        # Write to the file
        profile.write()
        write_header_count += 1

        # Wait two seconds so the server doesn't get bombarded with requests
        time.sleep(2)

    print("Process complete")
    # Exit the firefox webdriver
    driver.quit()


if __name__ == "__main__":
    main()

