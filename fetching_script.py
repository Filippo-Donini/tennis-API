from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pandas as pd
import datetime
import urllib.request
from bs4 import BeautifulSoup
import re

def load_rankings_to_AWS(df, table_name: str):
    try:
        if not AWS_URL:
            raise ValueError("Database URL not found in environment variables")
                
        engine = create_engine(AWS_URL)
            
        print(f"Uploading to table {table_name}...")
        df.to_sql(
                table_name,
                engine,
                if_exists='append',
                index=False,
                chunksize=50000
        )
            
        print(f"Successfully loaded {len(df)} rows into {table_name}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'engine' in locals():
                engine.dispose()
                
                
                
class CustomURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    
    
def parse_with_split(line):
    try:
        if not line or not isinstance(line, str):
            return None
            
        # Updated rank pattern to handle both formats
        rank_pattern = r'rk">(?:<span[^>]*>)?(\d+)(?:</span>)?<'
        name_pattern = r'pn">([^<]+)<'
        age_pattern = r'pn">[^<]+<td>(\d+)<|sm"[^>]*>(\d+)<'
        country_pattern = r'spr ([a-z]{3})|p="[0-9]+">([A-Z]{3})<'  # Updated to handle p="24"
        points_pattern = r'[A-Z]{3}<td>(\d+)<'
        
        rank = re.search(rank_pattern, line)
        name = re.search(name_pattern, line)
        age_match = re.search(age_pattern, line)
        country_match = re.search(country_pattern, line)
        points = re.search(points_pattern, line)
        
        if all([rank, name, age_match, country_match, points]):
            age = age_match.group(1) if age_match.group(1) else age_match.group(2)
            country = (country_match.group(1) or country_match.group(2)).upper()
            
            return {
                'rank': rank.group(1),
                'name': name.group(1).strip(),
                'age': age,
                'country': country,
                'points': points.group(1)
            }
    except (IndexError, AttributeError):
        return None
    return None

    
opener = CustomURLopener()
response = opener.open('https://live-tennis.eu/en/atp-live-ranking')
response=response.read().decode()

soup = BeautifulSoup(response, 'html.parser')

all_list=soup.find_all('td',class_='rk')

data=[]
for i in all_list:
    line=parse_with_split(str(i))
    data.append(line)
    #print(line)                               #debug

df=pd.DataFrame(data)

df['ranking_date']=datetime.datetime.now().strftime('%Y-%m-%d')
df['ID']=df["ranking_date"].astype(str) + df["rank"].astype(str)

load_dotenv()
AWS_URL=os.getenv("AWS_URL")

load_rankings_to_AWS(df,'atp_rankings_current')


opener = CustomURLopener()
response = opener.open('https://live-tennis.eu/en/wta-live-ranking')
response=response.read().decode()

soup = BeautifulSoup(response, 'html.parser')

all_list=soup.find_all('td',class_='rk')

data=[]
for i in all_list:
    line=parse_with_split(str(i))
    data.append(line)
    #print(line)                                #debug

df=pd.DataFrame(data)

df['ranking_date']=datetime.datetime.now().strftime('%Y-%m-%d')
df['ID']=df["ranking_date"].astype(str) + df["rank"].astype(str)

load_rankings_to_AWS(df,'wta_rankings_current')