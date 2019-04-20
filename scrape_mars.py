from splinter import Browser
import pandas as pd
from bs4 import BeautifulSoup as bs
import re

# Scrapes multiple websites and returns a dictionary of all the data
def scrape():
    # Start headless chrome browser for scraping
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)

    # Initialize empty dictionary for output
    mars_data = {}

    # Scrape the NASA Mars News Site
    # Collect title & brief description of latest news article
    mars_news_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(mars_news_url)
    soup = bs(browser.html, 'html.parser')
    
    latest_news = soup.find('li', class_='slide')
    news_title = latest_news.find('div', class_='content_title').text
    news_p = latest_news.find('div', class_='article_teaser_body').text

    mars_data['news'] = {'title': news_title, 'p': news_p}


    # Scrape the JPL Images Site
    # Find the featured image and save its full-res URL
    jpl_images_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_images_url)
    html = browser.html
    soup = bs(html, 'html.parser')

    img_url_tail = re.search("\('([^)]*)'\)", soup.find('article', class_="carousel_item")['style'])[1]
    featured_image_url = "https://www.jpl.nasa.gov" + img_url_tail
    
    mars_data['featured_image_url'] = featured_image_url


    # Scrape the Mars Weather site
    mars_twitter_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(mars_twitter_url)
    html = browser.html
    soup = bs(html, 'html.parser')

    mars_weather = soup.find('p', class_="tweet-text").a.previousSibling
    mars_data['weather'] = mars_weather


    # Scrape a Mars Facts website for a particular table
    # Render the table in HTML from pandas
    # Apply the .table bootstrap class to the HTML table
    mars_facts_url = "https://space-facts.com/mars/"
    tables = pd.read_html(mars_facts_url)
    df = tables[0]
    mars_data['facts_html'] = df.to_html(classes="table table-sm", header=False, index=False)

    # Obtain high resolution images and names of each of Mars' hemispheres
    # NOTE that these are not the fullest resolution images!
    # The reason we are not pulling those is that the largest images
    # are in .TIFF format, which does not render in most browsers;
    # so, we settle for JPEG.
    # The code which would do this is included in the loop, commented out
    usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(usgs_url)
    html = browser.html
    soup = bs(html, 'html.parser')
    
    full_res_lps = ["https://astrogeology.usgs.gov"+h.parent.get('href') for h in soup.find_all('h3')]
    hemisphere_image_urls = []
    for lp in full_res_lps:
        browser.visit(lp)
        html = browser.html
        soup = bs(html, 'html.parser')
        
        # Get title of hemisphere
        title = re.match('(.+?) Enhanced', soup.find('h2', class_='title').text)[1]

        # Get URL of high-res JPEG sample image
        img_url = soup.find('div', class_='downloads').li.a['href']
        
        # # Get URL of full resolution TIFF image
        # img_url = soup.find('div', class_='downloads').li.find_next_sibling('li').a['href']
        
        # Add to list
        hemisphere_image_urls.append({'title': title, 'img_url': img_url})
    
    mars_data['hemispheres'] = hemisphere_image_urls

    return mars_data