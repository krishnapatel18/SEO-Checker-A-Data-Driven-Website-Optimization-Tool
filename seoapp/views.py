import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout, authenticate, login
from .models import Signin, Signup, Home, Profile, ChangePassword, Project, User, Website, SEOAnalysis, CrawlResult
from django.contrib.auth.forms import AuthenticationForm
from bs4 import BeautifulSoup
import time
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.db import OperationalError

@require_http_methods(["GET", "POST"])
def signin_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # messages.success(request, 'Successfully logged in!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    form = AuthenticationForm()
    return render(request, 'signin.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, 'Registration done successfully!')
            return redirect('signin')
        else:
            messages.error(request, 'Passwords do not match!')
    return render(request, 'signup.html')

def home_view(request):
    projects = CrawlResult.objects.all().order_by('-crawled_at')
    return render(request, 'home.html', {
        'username': request.user.username,
        'projects': projects
    })

def profile_view(request):
    active_tab = request.GET.get('tab', 'account')
    context = {
        'active_tab': active_tab,
    }

    return render(request, 'profile.html', context)

def logout_view(request):
    logout(request)
    return redirect('signin')

def update_profile(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        company = request.POST.get('company')

        profile_instance = Profile(full_name=full_name, email=email, phone=phone, company=company)
        profile_instance.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'update_profile.html')

def change_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            changepw_instance = ChangePassword(email=email, new_password=new_password, confirm_password=confirm_password)
            changepw_instance.save()

            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'change_password.html')

def update_settings(request):
    if request.method == 'POST':
        messages.success(request, 'Settings updated successfully!')
    return redirect('profile')

@login_required
def add_project(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        url = request.POST.get('url')
        try:
            start_time = time.time()
            response = requests.get(url)
            response.raise_for_status()
            response_time = time.time() - start_time
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Website does not exist or could not be reached.'}, status=400)

        if response.status_code == 200:
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
            
            seo_suggestions = []
            if len(title) > 60:
                seo_suggestions.append(f"Your title '{title}' is too long. Consider shortening it to under 60 characters.")
            else:
                seo_suggestions.append(f"Your title '{title}' is of optimal length.")
            
            if len(description) > 160:
                seo_suggestions.append(f"Your description '{description}' is too long. Consider shortening it to under 160 characters.")
            else:
                seo_suggestions.append(f"Your description '{description}' is of optimal length.")
            
            if not keywords:
                seo_suggestions.append("No keywords found. Consider adding relevant keywords to your meta tags.")
            else:
                seo_suggestions.append(f"Consider using the following keywords: {keywords}.")
            
            if not soup.find_all(['h1', 'h2']):
                seo_suggestions.append("No headings (H1, H2) found. Consider adding relevant headings for better SEO.")
            else:
                seo_suggestions.append("Your content includes relevant headings (H1, H2).")
            
            if not soup.find_all('a'):
                seo_suggestions.append("No internal links found. Consider adding internal links to improve navigation.")
            else:
                seo_suggestions.append("Your content includes internal links.")
            
            word_count = len(soup.get_text().split())
            media_files = len(soup.find_all('img'))
            internal_links = len([link for link in soup.find_all('a') if link.get('href') and link.get('href').startswith('/')])
            external_links = len([link for link in soup.find_all('a') if link.get('href') and not link.get('href').startswith('/')])
            file_size = len(response.content) / 1024
            
            try:
                openpagerank_api_key = 's8ogw4skc804w8w8s0o8ssgcc0gc0480g44c0ogc'
                headers = {
                    'API-OPR': openpagerank_api_key
                }
                backlinks_response = requests.get(f'https://openpagerank.com/api/v1.0/getPageRank?domains[]={url}', headers=headers)
                backlinks_response.raise_for_status()
                backlinks_data = backlinks_response.json()
                backlinks = backlinks_data['response'][0].get('page_rank_integer', 'No backlinks found.')
            except requests.exceptions.RequestException as e:
                backlinks = f'Error retrieving backlinks: {e}'

            try:
                psi_response = requests.get(f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key=AIzaSyBbAMUmZPMflaY12sdSUDdETlal7WcUTKo')
                psi_response.raise_for_status()
                psi_data = psi_response.json()
                page_speed_insights = psi_data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 'Error retrieving Page Speed Insights.')
            except requests.exceptions.RequestException as e:
                page_speed_insights = f'Error retrieving Page Speed Insights: {e}' 

            # try:
            #     # Using Datamuse API to get related words
            #     datamuse_url = f'https://api.datamuse.com/words?rel_jjb={url.split("//")[1].split("/")[0].replace("www.", "")}&max=10'
            #     keywords_response = requests.get(datamuse_url)
            #     keywords_response.raise_for_status()
            #     keywords_data = keywords_response.json()
                
            #     # Extract suggested keywords
            #     suggested_keywords = [item.get('word') for item in keywords_data if 'word' in item]
                
            #     # If no keywords found, try another approach with 'means like'
            #     if not suggested_keywords:
            #         datamuse_url = f'https://api.datamuse.com/words?ml={url.split("//")[1].split("/")[0].replace("www.", "")}&max=10'
            #         keywords_response = requests.get(datamuse_url)
            #         keywords_response.raise_for_status()
            #         keywords_data = keywords_response.json()
            #         suggested_keywords = [item.get('word') for item in keywords_data if 'word' in item]
                
            #     if not suggested_keywords:
            #         suggested_keywords = ['No keywords found']
                    
            # except requests.exceptions.RequestException as e:
            #     suggested_keywords = [f'Error retrieving suggested keywords: {e}'] 

            # Improved keyword extraction
            try:
                # Extract keywords from the page content directly
                # Get all text from important elements
                text_elements = []
                
                # Get title
                if soup.title:
                    text_elements.append(soup.title.string)
                
                # Get meta description and keywords
                for meta in soup.find_all('meta'):
                    if 'name' in meta.attrs and meta.attrs['name'].lower() in ['description', 'keywords']:
                        if 'content' in meta.attrs:
                            text_elements.append(meta.attrs['content'])
                
                # Get heading content
                for heading in soup.find_all(['h1', 'h2', 'h3']):
                    text_elements.append(heading.get_text())
                
                # Combine all text
                all_text = ' '.join(text_elements).lower()
                
                # Remove common words and non-alphanumeric characters
                import re
                import string
                
                # Remove punctuation and convert to lowercase
                all_text = re.sub(f'[{string.punctuation}]', ' ', all_text)
                
                # Define stopwords (common words to exclude)
                stopwords = ['a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 
                            'at', 'from', 'by', 'for', 'with', 'about', 'against', 'between',
                            'into', 'through', 'during', 'before', 'after', 'above', 'below',
                            'to', 'of', 'in', 'on', 'has', 'have', 'had', 'is', 'are', 'was',
                            'were', 'be', 'been', 'being', 'do', 'does', 'did', 'will', 'would',
                            'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'that',
                            'this', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                            'who', 'whom', 'whose', 'which', 'what', 'where', 'when', 'why', 'how']
                
                # Split into words, filter stopwords and short words
                words = [word for word in all_text.split() if word not in stopwords and len(word) > 3]
                
                # Count word frequencies
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                
                # Get most common words
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                
                # Extract top 10 keywords
                suggested_keywords = [word for word, count in sorted_words[:10]]
                
                # Add bigrams (two-word phrases) for better keyword phrases
                bigram_freq = {}
                for i in range(len(words) - 1):
                    bigram = f"{words[i]} {words[i+1]}"
                    bigram_freq[bigram] = bigram_freq.get(bigram, 0) + 1
                
                sorted_bigrams = sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)
                bigram_keywords = [bigram for bigram, count in sorted_bigrams[:5]]
                
                # Combine individual words and bigrams
                suggested_keywords = suggested_keywords[:5] + bigram_keywords
                
                if not suggested_keywords:
                    # If still no keywords, extract from all page content as last resort
                    all_page_text = soup.get_text().lower()
                    all_page_text = re.sub(f'[{string.punctuation}]', ' ', all_page_text)
                    page_words = [word for word in all_page_text.split() if word not in stopwords and len(word) > 3]
                    
                    # Count frequencies from all text
                    page_word_freq = {}
                    for word in page_words:
                        page_word_freq[word] = page_word_freq.get(word, 0) + 1
                    
                    sorted_page_words = sorted(page_word_freq.items(), key=lambda x: x[1], reverse=True)
                    suggested_keywords = [word for word, count in sorted_page_words[:10]]
                    
                if not suggested_keywords:
                    suggested_keywords = ['No relevant keywords found']
                    
            except Exception as e:
                suggested_keywords = [f'Error extracting keywords: {str(e)}']

            try:
                # Attempt to save the data to the database
                CrawlResult.objects.create(
                    url=url,
                    status_code=response.status_code,
                    content=response.text,
                    title=title,
                    description=description,
                    keywords=keywords,
                    seo_suggestions='\n'.join(seo_suggestions),
                    response_time=response_time,
                    file_size=file_size,
                    word_count=word_count,
                    media_files=media_files,
                    internal_links=internal_links,
                    external_links=external_links,
                    backlinks=backlinks,
                    page_speed_insights=page_speed_insights,
                    suggested_keywords=suggested_keywords
                )
            except OperationalError as e:
                # Handle the max_allowed_packet error
                return JsonResponse({'error': 'The data is too large to save. Please try a smaller website or increase the database packet size.'}, status=500)

            results_html = render_to_string('add_project_results.html', {
                'url': url,
                'status_code': response.status_code,
                'content': response.text,
                'title': title,
                'description': description,
                'keywords': keywords,
                'seo_suggestions': seo_suggestions,
                'response_time': response_time,
                'file_size': file_size,
                'word_count': word_count,
                'media_files': media_files,
                'internal_links': internal_links,
                'external_links': external_links,
                'backlinks': backlinks,
                'page_speed_insights': page_speed_insights,
                'suggested_keywords': suggested_keywords
            })
            return JsonResponse({'results_html': results_html})
        else:
            return JsonResponse({'error': 'Failed to retrieve the website. Please check the URL and try again.'}, status=400)
    return render(request, 'add_project.html')

def plans_view(request):
    return render(request, 'plans.html')

def view_project(request, id):
    project = CrawlResult.objects.get(id=id)
    seo_suggestions_list = project.seo_suggestions.split('\n')
    return render(request, 'view_project.html', {
        'project': project,
        'seo_suggestions_list': seo_suggestions_list
    })

def reports_view(request):
    projects = CrawlResult.objects.all().order_by('-crawled_at')
    return render(request, 'reports.html', {
        'projects': projects
    })

@login_required
def change_plan(request, plan):
    user = request.user
    user.plan = plan
    user.save()
    messages.success(request, f'Your plan has been changed to {plan}.')
    return redirect('plans')

@login_required
def get_progress(request):
    """Endpoint to fetch the current progress."""
    cache_key = f"progress_{request.user.id}"
    progress = cache.get(cache_key, 0)  # Default to 0% if no progress is set
    return JsonResponse({'progress': progress})