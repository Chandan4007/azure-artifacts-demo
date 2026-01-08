import requests
from bs4 import BeautifulSoup
import csv
import time
from random import choice

# Function to get latitude and longitude using Google Maps Geocoding API
def get_lat_long(api_key, address):
    try:
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
        response = requests.get(geocode_url)
        response.raise_for_status()  # Ensure the request was successful
        geocode_data = response.json()
        if geocode_data['status'] == 'OK':
            location = geocode_data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding API error: {geocode_data['status']}")
            return None, None
    except requests.RequestException as e:
        print(f"Failed to get geocode data for address {address}. Error: {e}")
        return None, None

def scrape_cng_stations(city_name, city_value, area_name, area_value, writer, api_key):
    try:
        # URL for POST request to fetch station data
        url = "https://www.adanigas.com/cng/cng-locate"

        # Payload for POST request data
        payload = {
            "ddlCity": city_value,
            "ddlArea": area_value
        }

        # Send POST request to fetch station data
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Ensure the request was successful

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table containing the CNG station details
        station_table = soup.find("table", class_="table table-striped")

        # Write station details to CSV
        for row in station_table.find_all("tr")[1:]:  # Skip the header row
            columns = row.find_all("td")
            if len(columns) >= 3:
                station_name = columns[0].text.strip()
                address = columns[1].text.strip()
                contact = columns[2].text.strip()

                # Get latitude and longitude
                lat, lng = get_lat_long(api_key, address)

                writer.writerow([
                    city_name, area_name, station_name, address, contact, lat, lng
                ])
    except requests.RequestException as e:
        print(f"Failed to retrieve data for {area_name}, {city_name}. Error: {e}")
    except Exception as e:
        print(f"An error occurred while processing {area_name}, {city_name}. Error: {e}")

def get_soup_with_retries(url, method="GET", data=None, headers=None, retries=3, delay=5):
    for attempt in range(retries):
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()  # Ensure the request was successful
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed. Error: {e}")
            time.sleep(delay)
    raise Exception(f"Failed to retrieve {url} after {retries} attempts.")

def main():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    ]

    headers = {
        'User-Agent': choice(user_agents)
    }

    api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your Google Maps API key

    try:
        # URL for the main page
        url = "https://www.adanigas.com/cng/cng-locate"

        # Get soup object with retries
        soup = get_soup_with_retries(url, headers=headers)

        # Find the city select dropdown
        city_select = soup.find("select", id="ddlCity")
        if not city_select:
            print("Failed to locate the city dropdown on the page.")
            return

        # Extract city names and values from the dropdown
        cities = [(option.text.strip(), option["value"]) for option in city_select.find_all("option") if option["value"]]

        # Define CSV file
        csv_file = "cng_stations_with_lat_long.csv"
        csv_columns = ["City", "Area", "Station Name", "Address", "Contact", "Latitude", "Longitude"]

        # Write to CSV
        with open(csv_file, mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(csv_columns)

            # Loop through each city and its areas
            for city_name, city_value in cities[:1]:  # Limiting to the first city for demo
                # Send POST request to fetch areas for the current city
                area_url = "https://www.adanigas.com/cng/cng-locate"
                area_soup = get_soup_with_retries(
                    area_url, method="POST", data={"ddlCity": city_value}, headers=headers
                )

                # Parse the HTML content to find areas
                area_select = area_soup.find("select", id="ddlArea")
                if not area_select:
                    print(f"Failed to locate the area dropdown for {city_name}.")
                    continue

                # Extract area names and values from the dropdown
                areas = [
                    (option.text.strip(), option["value"]) for option in area_select.find_all("option") if option["value"]
                ]

                # Loop through each area and scrape station data
                for area_name, area_value in areas[:5]:  # Limiting to 5 areas for demo
                    print(f"Scraping data for area: {area_name} in city: {city_name}")
                    scrape_cng_stations(city_name, city_value, area_name, area_value, writer, api_key)
                    time.sleep(1)  # Adding a delay of 1 second for polite scraping

        print(f"Data has been successfully scraped and saved to {csv_file}.")

    except Exception as e:
        print(f"An error occurred during scraping. Error: {e}")

if __name__ == "__main__":
    main()
