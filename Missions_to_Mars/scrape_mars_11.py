#Import dependencies
import pymongo
import pandas as pd
import os
from bs4 import BeautifulSoup as bs
from splinter import Browser
import traceback
from time import sleep
from flask import Flask, render_template, redirect

mars_data = {}
conn = 'mongodb://localhost:27017'

#Method for scraping mars data
def scrape():
    #Executable path for chromedriver
    path = os.path.join('ChromeDriver', 'chromedriver.exe')
    executable_path = {'executable_path':'chromedriver.exe'}

    #Creating Browser object
    browser = Browser('chrome', **executable_path, headless=True)

    #Dictionary with all information
    mars_data = {}

    #NASA Mars new
    #URL 
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)

    html = browser.html
    soup = bs(html, 'html.parser')

    #collect the latest News Title and Paragraph Text.
    result = soup.find('div', class_='list_text')


    #title
    title_content = result.find('div', class_='content_title')
    news_title = title_content.find('a').text

    #paragraph
    news_p = result.find('div', class_='article_teaser_body').text

    mars_data['news_title'] = news_title
    mars_data['news_p'] = news_p

    #JPL Mars Space Images
    #URL
    ftImg_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    base_url = 'https://www.jpl.nasa.gov'
    browser.visit(ftImg_url)
    #Get the featured image full size url.
    try:
        browser.click_link_by_partial_text('FULL IMAGE')
        sleep(1)
        html = browser.html
        soup = bs(html, 'html.parser')
        result = soup.find('img', class_='fancybox-image')
        fullSize_url = result['src']
        featured_image_url = base_url + fullSize_url
        print(featured_image_url)

    except:
        traceback.print_exc()

    mars_data['featured_image_url'] = featured_image_url

    #Mars Weather
    #URL 
    tweet_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(tweet_url)
    
    try:
        sleep(1) 
        html = browser.html
        soup = bs(html, 'html.parser')
        result = soup.find('article')
        mars_weather = result.find('div', attrs={'lang':True}).text
        
        print(mars_weather)
        
    except:
        print("Exception throw")
        traceback.print_exc()

    mars_data['weather'] = mars_weather

    #Mars Facts
    #URL 
    facts_url = 'https://space-facts.com/mars'
    facts_df = pd.read_html(facts_url)

    #Formatting pandas dataframe to an html table
    table_string = facts_df[0].to_html(header=False, index=False)

    mars_data['facts'] = table_string

    #Mars Hemisphere 
    #URL 
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)

    hemisphere_image_urls = []
    try:
        sleep(1)
        html = browser.html
        soup = bs(html, 'html.parser')


        results = soup.find_all('div', class_="item")
        for result in results:
            title = result.find('h3')
            browser.click_link_by_partial_text(title.text)
            html = browser.html
            soup = bs(html, 'html.parser')
            url = soup.find('a', string='Sample')
            url = url['href']      
            browser.back()
            img_dict = {'title':title.text, 'url':url}
            hemisphere_image_urls.append(img_dict)
            
    except:
        print("Exception throw")
        traceback.print_exc()

    for url in hemisphere_image_urls:
        print(url)

    mars_data['hemispheres'] = hemisphere_image_urls
    
    return mars_data



app = Flask(__name__)

@app.route('/')
def home():
    client = pymongo.MongoClient(conn)
    db = client.scraping_db
    mars = db.mars

    data = mars.find_one()
    
    return render_template('index.html', mars_data=data)

@app.route('/scrape')
def scrapeInfo():
    client = pymongo.MongoClient(conn)
    db = client.scraping_db
    mars = db.mars

    new_data = scrape()
    mars.update({}, new_data)

    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)