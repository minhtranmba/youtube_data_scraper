#!/usr/bin/env python
# coding: utf-8

# # Youtube Data Scraper

# ## Modules
# Below are modules needed to communicate with youtube API and export data to csv files:

# In[1]:


pip install --upgrade google-api-python-client


# In[2]:


import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
import csv


# ## Search for the most watched videos
# `get_videos_id` returns search results for IDs of approximately 200 videos which have the most views in the US in a given year

# In[5]:


api_key = 'your_API_key'
api_service_name = "youtube"
api_version = "v3"
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = api_key)


# In[6]:


def get_videos_id(youtube, year):
    video_list =[]
    next_page_token = None
    count = 1
    request = youtube.search().list(
        part = "snippet",
        publishedAfter = str(year) + "-01-01T00:00:00Z",
        publishedBefore = str(year) + "-12-31T23:59:59Z",
        regionCode="US",
        order = "viewCount",
        maxResults = 50, # Google allows a maximum of 50 results per page
        pageToken = next_page_token, #each page has a token to retrieve data
        type = "video")
    response = request.execute()
    
    for i in range(len(response['items'])):
        video_data = dict(video_title = response['items'][i]['snippet']['title'],
                          video_id = response['items'][i]['id']['videoId'],
                          publish_date = response['items'][i]['snippet']['publishedAt'])
        
        video_list.append(video_data)
    
    count += 1
    while count <= 4: 
        
        next_page_token = response['nextPageToken']
        request = youtube.search().list(
            part = "snippet",
            publishedAfter = str(year) + "-01-01T00:00:00Z",
            publishedBefore = str(year) + "-12-31T23:59:59Z",
            regionCode="US",
            order = "viewCount",
            pageToken = next_page_token,
            maxResults = 50,
            type = "video")
        response = request.execute()
    
        for i in range(len(response['items'])):
            video_data = dict(video_title = response['items'][i]['snippet']['title'],
                              video_id = response['items'][i]['id']['videoId'],
                              publish_date = response['items'][i]['snippet']['publishedAt'])
            video_list.append(video_data)
        count += 1
        
    return video_list


# In[7]:


#------------Store results---------#
years = [2018,2019,2020,2021,2022]
results = []
for year in years:
    results.extend(get_videos_id(youtube, year))


# In[8]:


#------------Export results---------#
file = "YouTube.csv"
def writeCSV(results, filename):
    for i in range(len(results)):
        headers = ['video_title', 'video_id', 'publish_date']
    with open(filename, "w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames = headers)
        writer.writeheader()
        for i in range(len(results)):
            writer.writerow(results[i])
writeCSV(results, file)


# Read the search data above and display the first few rows 

# In[9]:


df = pd.read_csv("YouTube.csv")
df.head(3) 


# ## Get details of the most watched videos
# Search function has its limitation that it can return only video IDs, not their details. To get video details, we need another function, `get_videos`, which takes the above ID list as inputs and returns the respective videos' data. This function allows us to define which information we want to gather. In this project, we will get data of the following:
# <ul>
#     <li>Video Title</li>
#     <li>Video ID</li>
#     <li>Publish Date</li>
#     <li>Channel Title</li>
#     <li>Channel ID</li>
#     <li>Video Category</li>
#     <li>Video Duration</li>
#     <li>Number of Views</li>
#     <li>Number of Likes</li>
#     <li>Number of Comments</li>
# </ul>

# In[1]:


def get_videos(youtube, video_id):
     
    request = youtube.videos().list(
        part = "snippet,contentDetails,statistics",
        id = video_id)
    response = request.execute()
    
    video_data = dict(vid_title = response['items'][0]['snippet']['title'],
                      vid_id = video_id,
                      publish_date = response['items'][0]['snippet']['publishedAt'],
                      channel_title = response['items'][0]['snippet']['channelTitle'],
                      channel_id = response['items'][0]['snippet']['channelId'],
                      category_id = response['items'][0]['snippet']['categoryId'],
                      duration = response['items'][0]['contentDetails']['duration'])
    
    # Some videos are made private though having high views:
    if 'viewCount' in response['items'][0]['statistics'].keys():
        video_data['views'] = response['items'][0]['statistics']['viewCount']
    else:
        video_data['views'] = 'Private'
        
    # Not every video has likes/dislikes enabled
    if 'likeCount' in response['items'][0]['statistics'].keys():
        video_data['likes'] = response['items'][0]['statistics']['likeCount']
    else:
        video_data['likes'] = 'Disabled'
    
    # Not every video has comments enabled    
    if 'commentCount' in response['items'][0]['statistics'].keys():
        video_data['comments'] = response['items'][0]['statistics']['commentCount']
    else:
        video_data['comments'] = 'Disabled'
        
    return video_data


# In[11]:


#------------Store video data---------#
video_list = []
for video_id in df['video_id']:
    video_list.append(get_videos(youtube, video_id))


# In[12]:


#------------Export data---------#
file = "Youtube_video_data.csv"
def writeCSV(results, filename):
    for i in range(len(video_list)):
        headers = ['vid_title', 'vid_id', 'publish_date', 'channel_title','channel_id','category_id','duration','views','likes','comments']
    with open(filename, "w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames = headers)
        writer.writeheader()
        for i in range(len(video_list)):
            writer.writerow(video_list[i])
writeCSV(results, file)


# Read the data above and display the first few rows 

# In[13]:


df_1 = pd.read_csv("Youtube_video_data.csv")
df_1.head(3) 


# ## Get video category list
# The above data contain category IDs but not their names. `video_categories` function returns a list of dictionaries mapping category IDs and their respective names.

# In[14]:


def video_categories(youtube, region_code):
    categories = []
    request = youtube.videoCategories().list(
        part = "snippet",
        regionCode = region_code)
    response = request.execute()
    for i in range(len(response['items'])):
        category_info = dict(category_id = response['items'][i]['id'],
                             category_name = response['items'][i]['snippet']['title'])
        categories.append(category_info)
    return categories


# In[16]:


categories_us = video_categories(youtube, 'US')


# In[17]:


#------------Export data---------#
file = "Video_Categories.csv"
def writeCSV(categories_us, filename):
    for i in range(len(categories_us)):
        headers = ['category_id', 'category_name']
    with open(filename, "w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames = headers)
        writer.writeheader()
        for i in range(len(categories_us)):
            writer.writerow(categories_us[i])
writeCSV(categories_us, file)


# Read the data above and display the first few rows

# In[18]:


df_2 = pd.read_csv("Video_Categories.csv")
df_2.head(3) 

