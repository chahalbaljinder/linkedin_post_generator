"""
LinkedIn Post Generator - Content Aggregator Integration

This script extracts content from the README.md file that's been updated by
the gautamkrishnar/blog-post-workflow GitHub Action and formats it for
use in the LinkedIn post generator.
"""

import os
import re
import json
import random
from datetime import datetime
from bs4 import BeautifulSoup

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(BASE_DIR, 'README.md')
HTML_PATH = os.path.join(BASE_DIR, 'index.html')
OUTPUT_DIR = os.path.join(BASE_DIR, 'content')

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_content_from_html():
    """Extract content cards from the HTML file"""
    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            
        content_cards = []
        for card in soup.find_all(class_='content-card'):
            if not card:
                continue
                
            tag = card.find(class_='tag').text if card.find(class_='tag') else ''
            title = card.find('h3').text if card.find('h3') else ''
            link = card.find('a')['href'] if card.find('a') else ''
            description = card.find(class_='desc').text if card.find(class_='desc') else ''
            date = card.find(class_='date').text if card.find(class_='date') else ''
            
            category = None
            if 'tech' in card.get('class', []):
                category = 'Technology'
            elif 'jobs' in card.get('class', []):
                category = 'Jobs'
            elif 'finance' in card.get('class', []):
                category = 'Finance'
            elif 'stocks' in card.get('class', []):
                category = 'Stocks'
            elif 'breaking' in card.get('class', []):
                category = 'Breaking News'
                
            content_cards.append({
                'category': category,
                'tag': tag,
                'title': title,
                'link': link,
                'description': description,
                'date': date
            })
            
        return content_cards
        
    except Exception as e:
        print(f"Error extracting content from HTML: {e}")
        return []

def extract_content_from_readme():
    """Extract content sections from the README.md file"""
    try:
        with open(README_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
            
        sections = {
            'tech': re.search(r'<!-- TECH_NEWS:START -->(.*?)<!-- TECH_NEWS:END -->', content, re.DOTALL),
            'jobs': re.search(r'<!-- TECH_JOBS:START -->(.*?)<!-- TECH_JOBS:END -->', content, re.DOTALL),
            'finance': re.search(r'<!-- FINANCE_NEWS:START -->(.*?)<!-- FINANCE_NEWS:END -->', content, re.DOTALL),
            'stocks': re.search(r'<!-- STOCK_MARKET:START -->(.*?)<!-- STOCK_MARKET:END -->', content, re.DOTALL),
            'breaking': re.search(r'<!-- BREAKING_NEWS:START -->(.*?)<!-- BREAKING_NEWS:END -->', content, re.DOTALL)
        }
        
        content_sections = {}
        for key, section in sections.items():
            if section:
                content_sections[key] = section.group(1).strip()
                
        return content_sections
        
    except Exception as e:
        print(f"Error extracting content from README: {e}")
        return {}

def generate_linkedin_post(content_cards, category=None, count=1):
    """Generate LinkedIn post from content cards"""
    # Filter by category if specified
    if category:
        filtered_cards = [card for card in content_cards if card['category'] == category]
    else:
        filtered_cards = content_cards
        
    # Return if no cards available
    if not filtered_cards:
        return None
        
    # Select random cards if more are available than needed
    selected_cards = random.sample(filtered_cards, min(count, len(filtered_cards)))
    
    # Generate post content
    headline = f"🔍 The Latest in {selected_cards[0]['category']}" if selected_cards else "Latest News Update"
    
    post_content = f"# {headline}\n\n"
    post_content += "Here's what's trending today:\n\n"
    
    for i, card in enumerate(selected_cards, 1):
        post_content += f"## {i}. {card['title']}\n"
        post_content += f"{card['description']}\n"
        post_content += f"Read more: {card['link']}\n\n"
    
    # Add hashtags
    hashtags = []
    if selected_cards:
        category = selected_cards[0]['category']
        hashtags.append(f"#{category.replace(' ', '')}")
    
    hashtags.extend(["#ProfessionalUpdate", "#IndustryInsights", "#LinkedIn", "#CareerGrowth"])
    post_content += ' '.join(hashtags)
    
    # Create post object
    post = {
        "headline": headline,
        "subheadline": f"Curated content on {datetime.now().strftime('%B %d, %Y')}",
        "content": post_content,
        "source_links": [card['link'] for card in selected_cards],
        "category": selected_cards[0]['category'] if selected_cards else "General",
        "created_at": datetime.now().isoformat(),
        "image_suggestions": []
    }
    
    return post

def save_posts_to_file(posts, filename):
    """Save generated posts to a JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(posts, file, indent=2)
    print(f"Saved {len(posts)} posts to {filepath}")

def main():
    """Main function to run the content aggregation"""
    # Extract content
    content_cards = extract_content_from_html()
    
    if not content_cards:
        print("No content cards found. Check if the HTML file has been updated.")
        return
    
    # Generate posts for each category
    categories = ['Technology', 'Jobs', 'Finance', 'Stocks', 'Breaking News']
    all_posts = []
    
    for category in categories:
        # Generate 3 posts per category
        for i in range(3):
            post = generate_linkedin_post(content_cards, category=category, count=random.randint(1, 3))
            if post:
                all_posts.append(post)
    
    # Generate mixed category posts
    for i in range(5):
        post = generate_linkedin_post(content_cards, count=random.randint(3, 5))
        if post:
            all_posts.append(post)
    
    # Save to file
    save_posts_to_file(all_posts, f"linkedin_posts_{datetime.now().strftime('%Y%m%d')}.json")

if __name__ == "__main__":
    main()
