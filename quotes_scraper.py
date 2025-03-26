# 1. Import the libraries we need
import requests
from bs4 import BeautifulSoup
import csv # Added for saving to CSV

# 2. Define the URL of the page we want to scrape
url = "http://quotes.toscrape.com/"

# 3. Send a request to get the HTML content
print(f"Fetching URL: {url}")
try:
    # Adding a User-Agent header to mimic a browser slightly
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers, timeout=10) # timeout is good practice
    # Check if the request was successful (status code 200)
    response.raise_for_status()
    print("Successfully fetched the page.")

    # 4. Parse the HTML content using BeautifulSoup
    # 'html.parser' is a built-in Python HTML parser
    soup = BeautifulSoup(response.text, 'html.parser')

    # 5. Find all the quote blocks
    # Based on inspection, each quote is in a <div class="quote">
    quote_elements = soup.find_all('div', class_='quote')
    print(f"Found {len(quote_elements)} quotes on the page.")

    # 6. Loop through each quote block and extract the data
    scraped_quotes = [] # Create an empty list to store our results

    for quote_element in quote_elements:
        # Inside each 'div.quote', find the elements we need:
        # - Text: <span class="text">
        # - Author: <small class="author">
        # - Tags: <a> tags inside <div class="tags">

        # Use .find() because we expect only one text and author per quote block
        text_element = quote_element.find('span', class_='text')
        author_element = quote_element.find('small', class_='author')

        # Find the container for tags first
        tags_container = quote_element.find('div', class_='tags')
        # Then find all 'a' tags within that container
        tag_elements = tags_container.find_all('a', class_='tag') if tags_container else [] # Handle if no tags div

        # Extract the actual text content using .text and clean it with .strip()
        # Also check if the element was found before trying to get .text
        quote_text = text_element.text.strip() if text_element else "N/A"
        author_name = author_element.text.strip() if author_element else "N/A"

        # For tags, get the text of each tag and store them in a list
        tags = [tag.text.strip() for tag in tag_elements]

        # Store the extracted data in a dictionary
        quote_data = {
            "text": quote_text,
            "author": author_name,
            "tags": tags # This will be a list of strings
        }
        # Add the dictionary to our list
        scraped_quotes.append(quote_data)

    # 7. Save the results to a CSV file
    if scraped_quotes: # Only save if we actually scraped something
        # Define the name of the output file
        output_filename = "scraped_quotes.csv"
        print(f"\nSaving data to {output_filename}...")

        # Define the header row (column names) - based on keys in our dictionary
        # IMPORTANT: Convert the list of tags to a string BEFORE writing headers/rows
        headers = ["text", "author", "tags_string"] # Use a different name for the string version

        try:
            with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Create a CSV writer object
                writer = csv.DictWriter(csvfile, fieldnames=headers)

                # Write the header row
                writer.writeheader()

                # Write the data rows
                for quote in scraped_quotes:
                    # Prepare a dictionary with the correct headers for writing
                    row_to_write = {
                        "text": quote["text"],
                        "author": quote["author"],
                        "tags_string": ', '.join(quote['tags']) # Join list into a single string
                    }
                    writer.writerow(row_to_write)

            print(f"Successfully saved {len(scraped_quotes)} quotes to {output_filename}")

        except IOError as e:
            print(f"Error writing to CSV file: {e}")
        except Exception as e:
            print(f"An error occurred during CSV writing: {e}")
    else:
        print("\nNo quotes were scraped, nothing to save.")


except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
except Exception as e:
    # Catch other potential errors during parsing
    print(f"An error occurred: {e}")