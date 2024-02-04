import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def main():
    global df

    # Create an empty DataFrame to store the data
    df = pd.DataFrame(columns=['Year', 'Brand', 'Model', 'Mileage','Bodystyle','Dealer','Exterior Color','Interior Color',\
                            'Drivetrain','MPG', 'Fuel Type','Transmission', 'Engine',  'Price'])
    
    # Getting data from Cars.com
    page = 1
    loop_url(page)


# Extract Year 
def extract_year(info):
    pattern = r'"model_year":"(.*?)"'
    matches = re.search(pattern, str(info))

    if matches:
        year = matches.group(1)
        return year
    else:
        return 'N/A'


# Extract Brand 
def extract_brand(info):
    pattern = r'"make":"(.*?)"'
    matches = re.search(pattern, str(info))

    if matches:
        brand = matches.group(1)
        return brand
    else:
        return 'N/A'


def extract_model(info):
    
    pattern = r'"model":"(.*?)"'
    matches = re.search(pattern, str(info))

    if matches:
        model = matches.group(1)
        return model
    else:
        return 'N/A'

        
def extract_bodystyle(info):
    pattern = r'"bodystyle":"(.*?)"'
    matches = re.search(pattern, str(info))

    if matches:
        bodystyle = matches.group(1)
        return bodystyle
    else:
        return 'N/A'


def extract_price(info):
    price_info = info.find('span', class_='primary-price')
    price = price_info.text.strip() if price_info else 'N/A'
    price = re.findall(r'\d+', price)
    price = ''.join(price)
    return price


def extract_mileage(info):
    mileage_info = info.find('div', class_='mileage')
    mileage = mileage_info.text.strip() if mileage_info else 'N/A'
    mileage = re.findall(r'\d+', mileage)
    mileage = ''.join(mileage)
    return mileage


def extract_dealer(info):
    dealer_info = info.find(class_='dealer-name')
    dealer = dealer_info.text.strip() if dealer_info else 'N/A'
    return dealer


def extract_details(info):
    exterior_color = 'N/A'
    interior_color = 'N/A'
    drivetrain = 'N/A'
    mpg = 'N/A'
    fuel_type = 'N/A'
    transmission = 'N/A'
    engine = 'N/A'
    
    all_links = info.find_all('a', href=True)
    filtered_links = [link['href'] for link in all_links if "vehicledetail" in link['href']][0]
    
    link = 'https://www.cars.com' + str(filtered_links)
    response = requests.get(link)
        
    # parse the response.
    sub_soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the HTML element that contains the car information.
    sub_elements = sub_soup.find_all('dl', class_='fancy-description-list')

    for dl_element in sub_elements:
        try:
            dt_elements = dl_element.find_all('dt', limit=7)
            dd_elements = dl_element.find_all('dd', limit=7)
            
            
            if dt_elements and dt_elements[0].text.strip() == 'Exterior color':
                exterior_color = dd_elements[0].text.strip()
    
            if dt_elements and dt_elements[1].text.strip() == 'Interior color':
                interior_color = dd_elements[1].text.strip()
    
            if dt_elements and dt_elements[2].text.strip() == 'Drivetrain':
                drivetrain = dd_elements[2].text.strip().split()[0]
    
            if dt_elements and dt_elements[3].text.strip() == 'MPG':
                mpg = dd_elements[3].text.strip()
    
            if dt_elements and dt_elements[4].text.strip() == 'Fuel type':
                fuel_type = dd_elements[4].text.strip()
    
            if dt_elements and dt_elements[5].text.strip() == 'Transmission':
                transmission = dd_elements[5].text.strip()
    
            if dt_elements and dt_elements[6].text.strip() == 'Engine':
                engine = dd_elements[6].text.strip()
        except:
            pass

    return exterior_color, interior_color, drivetrain, mpg, fuel_type, transmission, engine


def loop_url(pages):
    for page in range(1, int(pages)+1):     
        url = 'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max\
        =&list_price_min=&makes[]=&maximum_distance=500&mileage_max=&monthly_payment=&page='+str(page)+\
        '&page_size=20&sort=best_match_desc&stock_type=used&year_max=&year_min=&zip=22030'

        # Send a request to a webpage and receive a response.
        response = requests.get(url)
        
        # parse the response.
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the HTML element that contains the car information.
        car_elements = soup.find_all('div', class_='vehicle-card')
        scrape_car_info(car_elements)
    
    
def scrape_car_info(car_elements):
    global df

    try:
        for info in car_elements:  
    
            year = extract_year(info)
            brand = extract_brand(info)
            model = extract_model(info)
            price = extract_price(info)
            mileage = extract_mileage(info)
            bodystyle = extract_bodystyle(info)
            dealer = extract_dealer(info)
            exterior_color, interior_color, drivetrain, mpg, fuel_type, transmission, engine = extract_details(info)
            
            
            # Create a DataFrame to store the data you want to append
            data_to_append = pd.DataFrame({
                'Year': [year],
                'Brand': [brand],
                'Model': [model],
                'Mileage': [mileage],
                'Bodystyle': [bodystyle],
                'Dealer': [dealer],
                'Exterior Color': [exterior_color],
                'Interior Color': [interior_color],
                'Drivetrain': [drivetrain],
                'MPG': [mpg],
                'Fuel Type': [fuel_type],
                'Transmission': [transmission],
                'Engine': [engine],
                'Price': [price]
            })

            # Concatenate the DataFrame with the existing 'df' DataFrame
            df = pd.concat([df, data_to_append], ignore_index=True)   
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None
        

if __name__ == "__main__":
    main()
    print(df)
