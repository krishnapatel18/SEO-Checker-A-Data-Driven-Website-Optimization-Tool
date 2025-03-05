import requests
from django.shortcuts import render
from .models import CrawlResult
from bs4 import BeautifulSoup

def crawl(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else 'No title found'
        description = ''
        keywords = ''
        
        for meta in soup.find_all('meta'):
            if 'name' in meta.attrs:
                if meta.attrs['name'].lower() == 'description':
                    description = meta.attrs['content']
                elif meta.attrs['name'].lower() == 'keywords':
                    keywords = meta.attrs['content']
        
        seo_suggestions = [
            f"Ensure your title '{title}' is under 60 characters.",
            f"Make sure your meta description '{description}' is under 160 characters.",
            f"Consider using the following keywords: {keywords}.",
            "Check if your content includes relevant headings (H1, H2, etc.) for better SEO.",
            "Ensure your website has a clear call-to-action (CTA) to improve user engagement."
        ]
        
        CrawlResult.objects.create(
            url=url,
            status_code=response.status_code,
            content=response.text
        )
        
        context = {
            'url': url,
            'status_code': response.status_code,
            'content': response.text,
            'title': title,
            'description': description,
            'keywords': keywords,
            'seo_suggestions': seo_suggestions,
            'backlinks': 'No backlinks found.',
            'page_speed_insights': 'Error retrieving Page Speed Insights: API key not valid. Please pass a valid API key.',
            'suggested_keywords': ['jiocinema', 'watch', 'sports', 'movies', 'web']
        }
        
        return render(request, 'webcrawler/crawl.html', context)
    return render(request, 'webcrawler/crawl.html')