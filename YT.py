from googleapiclient.discovery import build
import pandas as pd
import streamlit as st
import pymongo
import json

#Creating a connection and database
client = pymongo.MongoClient("mongodb://localhost:27017/")  #to connect MONGODB
mydb = client["YOUTUBE_Data"]  # to create database


st.header("_:green[Youtube] :red[Data Harvesting and Warehousing]_")

api_key='AIzaSyA4hFTKAjC8JM8XRstGWovfAA-RF-0vFK8'
channel_ids=["UCnz-ZXXER4jOvuED5trXfEA",# techTFQ
             "UCiT9RITQ9PW6BhXK0y2jaeg",# Keŋ Jee
             "UC2UXDak6o7rBm23k3Vv5dww",# Tina Huang
             "UCz22l7kbce-uFJAoaZqxD1A",#Gaur Gopal Das
             "UCnjX8fylNvSKVSMuyTqshsQ",#Cosmo Coding
             "UCLhLpPmymIUy0JfF3Nkcf_w",# Dharshan and rithika
             "UCLLw7jmFsvfIVaUFsLs8mlQ",# Luke Barousse
             "UC7cs8q-gJRLGwj4A80mCmXg"] # Alex the analyst
youtube = build("youtube", "v3", developerKey=api_key)

#Getting channel stats using ids
def get_channel_stats(youtube, channel_ids):
    data_all = []
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=','.join(channel_ids))

    response = request.execute()

    for i in range(len(response['items'])):
        data = dict(Channel_id=response['items'][i]['id'],
                    Channel_name=response['items'][i]['snippet']['title'],
                    Channel_kind=response['items'][i]['kind'],
                    Subscribers=response['items'][i]['statistics']['subscriberCount'],
                    Views=response['items'][i]['statistics']['viewCount'],
                    Total_videos=response['items'][i]['statistics']['videoCount'],
                    Channel_description=response['items'][i]['snippet']['description'],
                    playlist_ids=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])

        data_all.append(data)

    return data_all

channel_statistics=get_channel_stats(youtube, channel_ids)
channel_data=pd.DataFrame(channel_statistics)


if st.checkbox("Channel_Data"):
    st.table(channel_data)

#To convert pandas dataframe into csv file
def convert_df(df):
    return df.to_csv().encode("utf-8")

col1, col2 = st.columns(2)

#downloading data options
# DOWNLOAD AS CSV
csvCD = convert_df(channel_data)
with col1:
    st.download_button(label= "Download channel_data as CSV", data= csvCD, file_name= "Channel_data.csv",mime= "text/csv",)

# DOWNLOAD AS JSON
json_stringCD = channel_data.to_json(orient= "records")
with col2:
    st.download_button(label= "Download channel_data as JSON", data = json_stringCD, file_name= "channel_data.json",mime= "application/json",)


st.subheader("Select a channel id from the options below to display its Playlists.")
channel_id=st.selectbox("Channel_Ids : ", ("UCnz-ZXXER4jOvuED5trXfEA", # techTFQ
                                            "UCiT9RITQ9PW6BhXK0y2jaeg", # Keŋ Jee
                                            "UC2UXDak6o7rBm23k3Vv5dww", # Tina Huang
                                            "UCz22l7kbce-uFJAoaZqxD1A", #Gaur Gopal Das
                                            "UCnjX8fylNvSKVSMuyTqshsQ", #Cosmo Coding
                                            "UCLhLpPmymIUy0JfF3Nkcf_w", # Dharshan and rithika
                                            "UCLLw7jmFsvfIVaUFsLs8mlQ", # Luke Barousse
                                            "UC7cs8q-gJRLGwj4A80mCmXg")) # Alex the analyst

#Getting playlist id and name for a particular channel using channel id
def get_playlist_stats(youtube, channel_id):
    all_data=[]
    request=youtube.playlists().list(
        part='snippet,contentDetails',
        channelId=channel_id,
        maxResults=50
        )
    response=request.execute()

    for i in range(len(response['items'])):
        data = dict(Playlist_id=response['items'][i]['id'],
                    Playlist_name=response['items'][i]['snippet']['title'])
        all_data.append(data)

    return all_data

playlist_stats=get_playlist_stats(youtube,channel_id)
playlist_data=pd.DataFrame(playlist_stats)


if st.checkbox("Display Playlist"):
    st.table(playlist_data)

col1, col2 = st.columns(2)

#downloading options
# DOWNLOAD AS CSV
csvPD = convert_df(playlist_data)
with col1:st.download_button(label= "Download playlist_data (CSV", data= csvPD, file_name= "Playlist_data.csv",mime= "text/csv",)

# DOWNLOAD AS JSON
json_stringPD = playlist_data.to_json(orient= "records")
with col2: st.download_button(label= "Download playlist_data ( JSON)", data = json_stringPD, file_name= "Playlist_data.json",mime= "application/json",)


st.subheader("Select a Channel to get the video ids from :")
CName=st.selectbox("Channels :", (channel_data['Channel_name']))
word= CName
playlist_id=channel_data.loc[channel_data['Channel_name']==CName, 'playlist_ids'].iloc[0]

#getting video ids
def get_video_ids(youtube, playlist_id):
    video_ids = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=30
    )

    response = request.execute()

    for i in range(len(response["items"])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])

    next_page_token = response.get('nextPageToken')
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token)
            response = request.execute()

            for i in range(len(response["items"])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')

    return video_ids

videoID = get_video_ids(youtube, playlist_id)
video_ids=videoID
video_id_data=pd.DataFrame(videoID)

if st.checkbox("Show Video ID of Channel :"):
    st.table(video_id_data)

col1, col2 = st.columns(2)

#downloading options
# DOWNLOAD AS CSV
csvVI = convert_df(video_id_data)
with col1: st.download_button(label= "Download video_ids as CSV", data= csvVI, file_name= "Video_id_data.csv",mime= "text/csv",)

# DOWNLOAD AS JSON
json_stringVI = video_id_data.to_json(orient= "records")
with col2: st.download_button(label= "Download video_ids as JSON", data = json_stringVI, file_name= "Video_id_data.json",mime= "application/json",)


#getting video details using video ids
def get_video_details(youtube, video_ids):
    all_video_stats = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids[i:i+50]))
        response = request.execute()

        for video in response['items']:

            video_stats=dict ( Title = video['snippet']['title'],
                               Published_date = video['snippet']['publishedAt'],
                               View_Count = video['statistics']['viewCount'],
                               Likes_COunt = video['statistics']['likeCount'],
                               Comments_Count = video['statistics'].get('commentCount', 0),
                               Thumbnail = video['snippet']['thumbnails']['high']['url'],
                               video_description = video['snippet']['description'])
            all_video_stats.append(video_stats)

    return all_video_stats

video_details=get_video_details(youtube, video_ids)
video_data = (pd.DataFrame(video_details))

if st.checkbox("Show Video Details"):
    st.table(video_data)

col1, col2 = st.columns(2)

#downloading options
# DOWNLOAD AS CSV
csvVD = convert_df(video_data)
with col1:st.download_button(label= "Download video_data as CSV", data= csvVD, file_name= "Video_data.csv",mime= "text/csv",)

# DOWNLOAD AS JSON
json_stringVD = video_data.to_json(orient= "records")
with col2:st.download_button(label= "Download video_data as JSON", data = json_stringVD, file_name= "Video_data.json",mime= "application/json",)


#upload data to MONGODB

if st.button('Upload Youtube Data to MONGODB'):
    coll = word
    coll = coll.replace(' ', '_') + '_VideoIds'
    mycoll = mydb[coll]
    dict = video_data.to_dict("records")
    if dict:
        mycoll.insert_many(dict).inserted_ids
        st.success('Successfully uploaded to database', icon="✅")


#Saving Data files in json format
if st. button("Save json files"):
    with open("video_details.json", "w") as outfile1:
        json.dump(video_details, outfile1)
    with open("videoID.json", "w") as outfile2:
        json.dump(videoID, outfile2)
    with open("playlist_stats.json", "w") as outfile3:
        json.dump(playlist_stats, outfile3)
    with open("channel_statistics.json", "w") as outfile4:
        json.dump(channel_statistics, outfile4)
    st.success('Files Saved')