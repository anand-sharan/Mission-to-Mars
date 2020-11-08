# Dependencies
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from pprint import pprint
import time

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    time.sleep(5)
    browser = init_browser()
    mars_info = {}

    # visit mars news url
    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)

    time.sleep(5)

    # Create BeautifulSoup object; parse with 'html.parser'
    news_html = browser.html
    news_soup = BeautifulSoup(news_html,"html.parser")

    # Retrive the latest news from the list
    news_title = news_soup.find_all('div', class_='content_title')[1].text
    news_p = news_soup.find('div', class_='article_teaser_body').text

    # Store the data into dictionary

    mars_info["news_title"] = news_title
    mars_info["news_paragraph"] = news_p
    
    # visit JPL Featured Space Image URL
    jpl_url = "https://jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)
    time.sleep(5)
    # Scraping JPL Mars site for featured image
    jpl_html = browser.html
    jpl_soup = BeautifulSoup(jpl_html, "html.parser")

    main_jpl_url = "https://www.jpl.nasa.gov"
    image_url = jpl_soup.find('a', class_="button fancybox")["data-fancybox-href"]
    featured_image_url = f"{main_jpl_url}{image_url}"

    #/spaceimages/images/wallpaper/PIA19113-1920x1200.jpg
    image_name = image_url.split('/')[4]

    featured_full_size_url = main_jpl_url + \
                '/' + image_url.split('/')[1] + \
                '/' + image_url.split('/')[2] + \
                '/wallpaper/' + image_name.split('_')[0] + '-1920x1200.jpg'


    # Store the data into dictionary
    mars_info["featured_image_url"] = featured_image_url

    # Store the data into dictionary
    mars_info["featured_full_size_url"] = featured_full_size_url

    # Mars facts url
    mars_facts_url = "https://space-facts.com/mars/"
    table = pd.read_html(mars_facts_url)
    df = table[0]

    df.columns = ['Parameter', 'Values']
    mars_facts = df.to_html(index = False)

    mars_info['mars_facts'] = mars_facts

    #Visit USGS Astrogeology site 
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)
    time.sleep(5)

    # Create BeautifulSoup object; parse with 'html.parser'
    hemi_html = browser.html
    hemi_soup = BeautifulSoup(hemi_html,"html.parser")

    # find all items that contain image urls
    div_items = hemi_soup.find_all('div', class_="item")

    # Create a list to store hemisphere image urls
    hemisphere_image_urls = []

    # Hemisphere url
    main_url = "https://astrogeology.usgs.gov"

    # Loop through all the items to find the titles and urls
    for item in div_items:
        title = item.find('h3').text
        img_url = item.find('a', class_='itemLink product-item')['href']
        
        
        # Create a full url to the image link
        full_image_url = main_url+img_url
        
        # click on the full url link
        browser.visit(full_image_url)
        time.sleep(5)
        
        # Create BeautifulSoup object; parse with 'html.parser'
        img_html = browser.html
        img_soup = BeautifulSoup( img_html, 'html.parser')
        
        # image url
        hemi_img_url = img_soup.find('img', class_='wide-image')['src']
        
        # Final full resolution image url
        full_res_img_url = main_url+hemi_img_url
        
        hemisphere_image_urls.append({"title" : title, "img_url" : full_res_img_url})

    mars_info['hemisphere_image'] = hemisphere_image_urls

    # Quit the browser after scraping
    browser.quit()

    # Return results
    return mars_info
