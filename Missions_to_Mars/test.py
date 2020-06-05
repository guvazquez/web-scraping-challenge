
import pymongo
import pandas as pd
import os
from bs4 import BeautifulSoup as bs
from splinter import Browser
import traceback
from time import sleep
from flask import Flask, render_template, redirect


conn = 'mongodb://localhost:27017'

path = os.path.join('..', 'ChromeDriver', 'chromedriver.exe')
executable_path = {'executable_path':path}

#Creating Browser object
browser = Browser('chrome', **executable_path, headless=True)

#Dictionary with all information
mars_data = {}