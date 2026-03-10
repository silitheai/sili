import requests
from bs4 import BeautifulSoup
import re

def extract_linkedin_profile_data(profile_url: str) -> str:
    """Extracts public resume data, experience, and skills from a LinkedIn profile URL using public web scraping."""
    try:
        # LinkedIn is extremely aggressive against scraping.
        # This implementation attempts to read the public profile page.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        res = requests.get(profile_url, headers=headers, timeout=15)
        if res.status_code != 200:
            return f"Failed to access LinkedIn profile. Status code: {res.status_code}. LinkedIn usually requires authentication or a premium proxy for frequent access."
            
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # Extract Name
        name_tag = soup.find('h1', class_='top-card-layout__title')
        name = name_tag.text.strip() if name_tag else "Unknown Name"
        
        # Extract Headline
        headline_tag = soup.find('h2', class_='top-card-layout__headline')
        headline = headline_tag.text.strip() if headline_tag else "No Headline"
        
        # Extract About
        about_tag = soup.find('div', class_='about-us__description') or soup.find('p', class_='summary')
        about = about_tag.text.strip() if about_tag else "No About section found"
        
        output = f"💼 --- LINKEDIN PUBLIC PROFILE: {name} ---\n"
        output += f"Headline: {headline}\n\n"
        output += f"[About]\n{about}\n\n"
        
        # Extract Experience
        output += "[Experience]\n"
        exp_items = soup.find_all('li', class_='experience-item')
        if not exp_items:
            output += "Specific experience items could not be parsed without authentication.\n"
        else:
            for item in exp_items[:5]:
                title = item.find('h3').text.strip() if item.find('h3') else "Position"
                company = item.find('h4').text.strip() if item.find('h4') else "Company"
                output += f"- {title} at {company}\n"
                
        return output
        
    except Exception as e:
        return f"Error scraping LinkedIn: {e}"
