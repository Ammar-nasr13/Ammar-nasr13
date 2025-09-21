#!/usr/bin/env python3
"""
Script to generate programming language usage percentage chart without Token
"""

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import requests
import os
import collections
import time
from urllib.request import urlopen
from io import BytesIO
import numpy as np

# Appropriate colors for each programming language (colored according to each language's official logo)
LANGUAGE_COLORS = {
    'Python': ['#3776AB', '#FFD43B'],  # Blue with yellow
    'JavaScript': ['#F7DF1E', '#000000'],  # Yellow with black
    'Java': ['#007396', '#ED8B00'],  # Blue with orange
    'HTML': ['#E34F26', '#FFFFFF'],  # Orange with white
    'CSS': ['#1572B6', '#EBEBEB'],  # Blue with gray
    'TypeScript': ['#3178C6', '#FFFFFF'],  # Blue with white
    'C++': ['#00599C', '#004482'],  # Blue shades
    'C': ['#A8B9CC', '#555555'],  # Gray with dark gray
    'PHP': ['#777BB4', '#8993BE'],  # Purple
    'Ruby': ['#CC342D', '#A40E11'],  # Red
    'Go': ['#00ADD8', '#007D9C'],  # Light blue
    'Rust': ['#000000', '#DEA584'],  # Black with beige
    'Kotlin': ['#7F52FF', '#FF7FBC'],  # Purple with pink
    'Swift': ['#FA7343', '#FDAD40'],  # Orange
    'Dart': ['#0175C2', '#02569B'],  # Blue
    'Shell': ['#89E051', '#4EAA25'],  # Green
    'Vue': ['#4FC08D', '#34495E'],  # Green with gray
    'React': ['#61DAFB', '#00D8FF'],  # Light blue
    'Angular': ['#DD0031', '#C3002F'],  # Red
    'Node.js': ['#339933', '#026E00'],  # Green
    'Other': ['#888888', '#555555']  # Gray for other languages
}

# Language icon links (from devicon website)
LANGUAGE_ICONS = {
    'Python': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg',
    'JavaScript': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg',
    'Java': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg',
    'HTML': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg',
    'CSS': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg',
    'TypeScript': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg',
    'C++': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg',
    'C': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/c/c-original.svg',
    'PHP': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/php/php-original.svg',
    'Ruby': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ruby/ruby-original.svg',
    'Go': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/go/go-original.svg',
    'Rust': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/rust/rust-plain.svg',
    'Kotlin': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/kotlin/kotlin-original.svg',
    'Swift': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/swift/swift-original.svg',
    'Dart': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/dart/dart-original.svg',
    'Shell': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bash/bash-original.svg',
    'Vue': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vuejs/vuejs-original.svg',
    'React': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg',
    'Angular': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg',
    'Node.js': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg',
    'Other': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/codeigniter/codeigniter-plain.svg'
}

def get_image_from_url(url, size=40):
    """Fetch image from URL and resize it"""
    try:
        response = urlopen(url)
        img_data = response.read()
        img = plt.imread(BytesIO(img_data), format='svg')
        
        # If the image has transparency, make background white
        if img.shape[2] == 4:  # If there's an alpha channel
            alpha = img[:, :, 3:]
            img = img[:, :, :3]
            img = np.where(alpha > 0.1, img, 1.0)  # Replace transparency with white
        
        return img
    except Exception as e:
        print(f"Error loading image from {url}: {e}")
        # Return a blank image if loading fails
        return np.ones((size, size, 3))

def get_languages_data_no_token(username):
    """
    Fetch language data without using Token (using GitHub REST API)
    """
    languages_data = collections.Counter()
    page = 1
    per_page = 100
    
    try:
        while True:
            # Fetch a page of repositories
            url = f"https://api.github.com/users/{username}/repos?page={page}&per_page={per_page}"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Error fetching data: {response.status_code}")
                break
                
            repos = response.json()
            if not repos:
                break
                
            # Process each repository
            for repo in repos:
                if not repo.get('fork', False):  # Ignore forked repositories
                    if repo.get('languages_url'):
                        lang_response = requests.get(repo['languages_url'])
                        if lang_response.status_code == 200:
                            repo_langs = lang_response.json()
                            for lang, bytes_count in repo_langs.items():
                                languages_data[lang] += bytes_count
                        # Wait a bit between requests to avoid rate limits
                        time.sleep(0.1)
            
            page += 1
            if len(repos) < per_page:
                break
                
    except Exception as e:
        print(f"Error: {e}")
        return {}
    
    # Convert to percentages
    total_bytes = sum(languages_data.values())
    if total_bytes == 0:
        return {}
        
    languages_percent = {lang: (bytes_count / total_bytes) * 100 
                        for lang, bytes_count in languages_data.items()}
    
    return dict(sorted(languages_percent.items(), key=lambda x: x[1], reverse=True))

def create_languages_chart(username, output_path="charts/languages_chart.png"):
    """
    Create programming language usage percentage chart with professional design
    """
    # Fetch language data without Token
    print("Fetching language data from GitHub...")
    languages_data = get_languages_data_no_token(username)
    
    if not languages_data:
        print("Using sample data because data fetching failed")
        # Sample data for display
        languages_data = {
            'Python': 45, 
            'JavaScript': 25, 
            'HTML': 15, 
            'CSS': 8, 
            'Java': 7
        }
    
    # Group small languages into "Other" category
    main_languages = {}
    other_percent = 0
    
    for lang, percent in languages_data.items():
        if percent >= 1.5:  # Languages representing more than 1.5%
            main_languages[lang] = percent
        else:
            other_percent += percent
    
    if other_percent > 0:
        main_languages['Other'] = other_percent
    
    # Prepare data for chart
    labels = list(main_languages.keys())
    sizes = list(main_languages.values())
    
    # Select appropriate colors for each language
    colors = []
    for lang in labels:
        if lang in LANGUAGE_COLORS:
            colors.append(LANGUAGE_COLORS[lang][0])  # Main color
        else:
            colors.append(LANGUAGE_COLORS['Other'][0])  # Default color
    
    # Create figure with transparent background
    fig, ax = plt.subplots(figsize=(16, 12), facecolor='none')
    ax.set_facecolor('none')
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=None,  # Don't show traditional labels
        colors=colors, 
        autopct='%1.1f%%',
        startangle=90, 
        shadow=True, 
        explode=[0.03] * len(labels),
        textprops={
            'color': 'white', 
            'fontsize': 14,
            'fontweight': 'bold',
            'path_effects': [path_effects.withStroke(linewidth=3, foreground="black")]
        }
    )
    
    # Improve text (percentages)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(13)
        autotext.set_fontweight('bold')
        autotext.set_path_effects([path_effects.withStroke(linewidth=2, foreground="black")])
    
    # Add chart title
    title = ax.set_title('Programming Languages', 
                        color='#2c3e50', 
                        fontsize=24, 
                        fontweight='bold', 
                        pad=30,
                        fontfamily='DejaVu Sans')
    title.set_path_effects([path_effects.withStroke(linewidth=3, foreground="white")])
    
    # Add language icons
    for i, (wedge, lang) in enumerate(zip(wedges, labels)):
        # Calculate icon position
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))
        
        # Get appropriate icon
        icon_url = LANGUAGE_ICONS.get(lang, LANGUAGE_ICONS['Other'])
        img = get_image_from_url(icon_url, size=30)
        
        # Add icon
        imagebox = OffsetImage(img, zoom=0.4)
        ab = AnnotationBbox(imagebox, (x * 0.7, y * 0.7), frameon=False)
        ax.add_artist(ab)
        
        # Add language name
        text_x = x * 1.25
        text_y = y * 1.25
        lang_text = ax.text(text_x, text_y, lang, 
                           ha='center', va='center',
                           fontsize=11, fontweight='bold',
                           color='#2c3e50')
        lang_text.set_path_effects([path_effects.withStroke(linewidth=2, foreground="white")])
    
    # Add center hole
    centre_circle = plt.Circle((0,0), 0.50, fc='white', alpha=0.8)
    fig.gca().add_artist(centre_circle)
    
    # Add total percentage in center
    center_text = fig.text(0.5, 0.5, f'Total\n{sum(sizes):.0f}%', 
                          ha='center', va='center', 
                          fontsize=20, fontweight='bold',
                          color='#2c3e50',
                          linespacing=1.5)
    center_text.set_path_effects([path_effects.withStroke(linewidth=3, foreground="white")])
    
    # Ensure the chart is a perfect circle
    ax.axis('equal')
    
    # Improve overall appearance
    plt.tight_layout()
    
    # Save chart
    plt.savefig(output_path, bbox_inches='tight', transparent=True, dpi=120, 
                facecolor='none', edgecolor='none')
    plt.close()
    
    print("Chart created successfully with professional design!")
    print("Language percentages:")
    for lang, percent in main_languages.items():
        print(f"   {lang}: {percent:.2f}%")
    
    return True

if __name__ == "__main__":
    # Get username from environment variables or use default
    username = os.environ.get("GITHUB_USERNAME", "Ammar-nasr13")
    
    # Create charts folder if it doesn't exist
    os.makedirs("charts", exist_ok=True)
    
    # Create chart
    success = create_languages_chart(username)
    
    if not success:
        exit(1)