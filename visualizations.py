import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import re
from pathlib import Path
from collections import Counter

def extract_numbers(text):
    """Extract numerical values from text."""
    # Improved regex to better match Indian currency format
    matches = re.findall(r'Rs\.?\s*([\d,]+(?:\.\d{2})?)|(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
    numbers = []
    for match in matches:
        # Take the non-empty group from the match
        num_str = match[0] if match[0] else match[1]
        # Remove commas and convert to float
        try:
            num = float(num_str.replace(',', ''))
            if num > 0:  # Only include positive numbers
                numbers.append(num)
        except ValueError:
            continue
    return sorted(numbers, reverse=True)  # Sort in descending order

def clean_text(text):
    """Clean and preprocess text."""
    # Remove special characters and normalize whitespace
    text = re.sub(r'[^\w\s\.]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def count_keywords(text, keywords):
    """Count occurrences of keywords in text with improved accuracy."""
    text = clean_text(text.lower())
    counts = {}
    for keyword in keywords:
        # Use word boundaries to ensure we're matching whole words
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        counts[keyword] = len(re.findall(pattern, text))
    return counts

def create_coverage_chart(numbers):
    """Create an interactive chart for coverage amounts."""
    if not numbers:
        print("No valid numbers found for coverage chart")
        return
    
    # Take top 5 numbers for better visualization
    top_numbers = numbers[:5]
    total = sum(top_numbers)
    
    df = pd.DataFrame({
        'Coverage Type': [f'Coverage {i+1}' for i in range(len(top_numbers))],
        'Amount (Rs.)': top_numbers,
        'Percentage': [n/total*100 for n in top_numbers]
    })
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=df['Coverage Type'],
            y=df['Amount (Rs.)'],
            name="Coverage Amount",
            marker_color='rgba(67, 97, 238, 0.7)',
            hovertemplate="<b>%{x}</b><br>" +
                         "Amount: ₹%{y:,.2f}<br>" +
                         "<extra></extra>"
        ),
        secondary_y=False,
    )
    
    # Add line chart for percentage
    fig.add_trace(
        go.Scatter(
            x=df['Coverage Type'],
            y=df['Percentage'],
            name="Percentage of Total",
            line=dict(color='rgba(247, 37, 133, 0.8)', width=3),
            mode='lines+markers',
            hovertemplate="<b>%{x}</b><br>" +
                         "Percentage: %{y:.1f}%<br>" +
                         "<extra></extra>"
        ),
        secondary_y=True,
    )
    
    fig.update_layout(
        title={
            'text': f'Policy Coverage Distribution (Total: ₹{total:,.2f})',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.8)'
        ),
        hoverlabel=dict(bgcolor="white"),
        margin=dict(t=100, l=50, r=50, b=50)
    )
    
    fig.update_yaxes(
        title_text="Amount (₹)", 
        secondary_y=False, 
        gridcolor='lightgray',
        tickformat=',.'
    )
    fig.update_yaxes(
        title_text="Percentage of Total", 
        secondary_y=True,
        tickformat='.1f'
    )
    
    fig.write_html('static/coverage_chart.html', include_plotlyjs='cdn')

def create_benefits_chart(keywords_count):
    """Create an interactive treemap for benefits and requirements."""
    # Enhanced categorization
    categories = {
        'Benefits & Coverage': {
            'Core Benefits': ['covers', 'benefits'],
            'Coverage Details': ['eligible', 'maximum']
        },
        'Requirements & Limitations': {
            'Policy Requirements': ['must', 'required'],
            'Exclusions & Limits': ['exclusions', 'limitations']
        }
    }
    
    # Build hierarchical data with proper nesting
    data = {}
    total_count = 0
    
    for main_cat, subcats in categories.items():
        data[main_cat] = {}
        category_total = 0
        
        for subcat_name, keywords in subcats.items():
            count = sum(keywords_count.get(k, 0) for k in keywords)
            if count > 0:  # Only include non-zero counts
                data[main_cat][subcat_name] = count
                category_total += count
        
        if category_total > 0:
            total_count += category_total
    
    # Prepare data for treemap
    labels = []
    parents = []
    values = []
    colors = []
    
    # Add root
    labels.append('Policy Analysis')
    parents.append('')
    values.append(total_count)
    colors.append('rgba(67, 97, 238, 0.7)')
    
    # Add main categories
    for main_cat in data:
        labels.append(main_cat)
        parents.append('Policy Analysis')
        values.append(sum(data[main_cat].values()))
        colors.append('rgba(67, 97, 238, 0.5)')
        
        # Add subcategories
        for subcat, count in data[main_cat].items():
            labels.append(subcat)
            parents.append(main_cat)
            values.append(count)
            colors.append('rgba(247, 37, 133, 0.7)')
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colors),
        textinfo="label+value+percent parent",
        hovertemplate="<b>%{label}</b><br>" +
                     "Count: %{value}<br>" +
                     "Percentage: %{percentParent:.1%}<br>" +
                     "<extra></extra>"
    ))
    
    fig.update_layout(
        title={
            'text': 'Policy Components Analysis',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        width=800,
        height=600
    )
    
    fig.write_html('static/benefits_chart.html', include_plotlyjs='cdn')

def create_keyword_trends(text):
    """Create an interactive area chart showing keyword trends."""
    # Clean and split text into more meaningful sections
    cleaned_text = clean_text(text)
    # Split into sections of roughly equal length
    total_words = len(cleaned_text.split())
    words_per_section = max(100, total_words // 10)  # Aim for 10 sections
    
    sections = []
    words = cleaned_text.split()
    for i in range(0, len(words), words_per_section):
        section = ' '.join(words[i:i + words_per_section])
        sections.append(section)
    
    keywords = ['benefit', 'cover', 'limit', 'exclude', 'require', 'premium', 'insure']
    
    # Count keywords in each section
    section_counts = []
    for i, section in enumerate(sections):
        counts = {k: len(re.findall(r'\b' + k + r'\b', section.lower())) for k in keywords}
        counts['section'] = i + 1
        section_counts.append(counts)
    
    df = pd.DataFrame(section_counts)
    
    # Create figure
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    
    for i, keyword in enumerate(keywords):
        fig.add_trace(
            go.Scatter(
                x=df['section'],
                y=df[keyword],
                name=keyword.capitalize(),
                fill='tonexty',
                mode='lines+markers',
                line=dict(width=2, color=colors[i]),
                hovertemplate="<b>Section %{x}</b><br>" +
                             f"{keyword.capitalize()}: %{{y}}<br>" +
                             "<extra></extra>"
            )
        )
    
    fig.update_layout(
        title={
            'text': 'Keyword Distribution Across Document',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.8)'
        ),
        plot_bgcolor='white',
        hovermode='x unified',
        xaxis=dict(
            title="Document Section",
            gridcolor='lightgray',
            showgrid=True
        ),
        yaxis=dict(
            title="Keyword Frequency",
            gridcolor='lightgray',
            showgrid=True
        )
    )
    
    fig.write_html('static/keyword_trends.html', include_plotlyjs='cdn')

def create_word_cloud(text):
    """Create an interactive word cloud visualization."""
    # Clean and tokenize text
    cleaned_text = clean_text(text)
    words = re.findall(r'\b\w+\b', cleaned_text.lower())
    
    # Enhanced stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after'
    }
    
    # Count word frequencies
    word_freq = Counter(words)
    word_freq = {
        word: freq for word, freq in word_freq.items() 
        if word not in stop_words and len(word) > 2 and freq > 1  # Only include words that appear more than once
    }
    
    # Create scatter plot that looks like a word cloud
    words_df = pd.DataFrame(list(word_freq.items()), columns=['word', 'frequency'])
    words_df = words_df.nlargest(50, 'frequency')
    
    # Generate positions for words
    np.random.seed(42)
    words_df['x'] = np.random.randn(len(words_df))
    words_df['y'] = np.random.randn(len(words_df))
    
    # Create color scale based on frequency
    max_freq = words_df['frequency'].max()
    min_freq = words_df['frequency'].min()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=words_df['x'],
        y=words_df['y'],
        mode='text',
        text=words_df['word'],
        textfont=dict(
            size=[20 + (freq - min_freq) / (max_freq - min_freq) * 40 for freq in words_df['frequency']],
            color=[f'rgba({np.random.randint(0,255)},{np.random.randint(0,255)},{np.random.randint(0,255)},0.8)' 
                  for _ in range(len(words_df))]
        ),
        hovertemplate="<b>%{text}</b><br>" +
                     "Frequency: %{marker.size}<br>" +
                     "<extra></extra>",
        marker=dict(size=words_df['frequency'])
    ))
    
    fig.update_layout(
        title={
            'text': 'Policy Document Word Cloud',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='white'
    )
    
    fig.write_html('static/word_cloud.html', include_plotlyjs='cdn')

def generate_visualizations():
    """Generate all visualizations from the policy document."""
    # Create static directory if it doesn't exist
    Path('static').mkdir(exist_ok=True)
    
    # Read the simplified text
    try:
        with open('simplified_text.txt', 'r', encoding='utf-8') as f:
            simplified_text = f.read()
            
        if not simplified_text.strip():
            raise ValueError("The simplified text file is empty")
            
        # Extract data
        numbers = extract_numbers(simplified_text)
        if not numbers:
            print("Warning: No valid numbers found in the text")
            
        keywords = count_keywords(simplified_text, [
            'covers', 'benefits', 'exclusions', 'limitations',
            'must', 'required', 'eligible', 'maximum',
            'premium', 'insure', 'policy', 'claim'
        ])
        
        # Generate visualizations
        create_coverage_chart(numbers)
        create_benefits_chart(keywords)
        create_keyword_trends(simplified_text)
        create_word_cloud(simplified_text)
        
        print("Visualizations generated successfully!")
        
    except FileNotFoundError:
        print("Error: simplified_text.txt not found")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error generating visualizations: {str(e)}")

if __name__ == "__main__":
    generate_visualizations() 