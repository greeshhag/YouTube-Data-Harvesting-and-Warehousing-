import streamlit as st
import pandas as pd
import pymongo
import sqlite3
import googleapiclient.discovery
import mysql.connector as sql

# Function to retrieve channel details using YouTube API
def get_channel_details(channel_id):
    # Implement code to retrieve channel details using YouTube API
    # For example, using the googleapiclient.discovery library
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey="AIzaSyCVbNyH-gqlP-jQiN4HgUuPeTt0QCxo23E" )
    request = youtube.channels().list(part='snippet,statistics', id=channel_id)
    response = request.execute()
    channel_data = response['items'][0]
    return channel_data

# Function to migrate selected channels to SQL Database
def migrate_to_sql_database(selected_channels):
    # Implement code to migrate selected channels to SQL Database
    # Establish a connection to the SQL Database
    mydb = sql.connect(
    host="localhost",
    user="root",
    password="",)
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("USE yt")
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    for channel_id in selected_channels:
        channel_data = get_channel_details(channel_id)
        # Create tables and insert data into the SQL Database
        cursor.execute('CREATE TABLE IF NOT EXISTS channels (channel_id TEXT, channel_name TEXT, subscribers INTEGER)')
        cursor.execute('INSERT INTO channels (channel_id, channel_name, subscribers) VALUES (?, ?, ?)',
                       (channel_data['id'], channel_data['snippet']['title'], int(channel_data['statistics']['subscriberCount'])))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to migrate selected channels to MongoDB Database
def migrate_to_mongodb(selected_channels):
    # Implement code to migrate selected channels to MongoDB Database
    # Establish a connection to the MongoDB Database
    client = pymongo.MongoClient("mongodb+srv://sujenthiran08:12345AB@cluster0.u1h6hh6.mongodb.net/?retryWrites=true&w=majority")
    db = client['YT']
  
    for channel_id in selected_channels:
        channel_data = get_channel_details(channel_id)
        # Insert data into the MongoDB Database
        db.channels.insert_one({
            'channel_id': channel_data['id'],
            'channel_name': channel_data['snippet']['title'],
            'subscribers': int(channel_data['statistics']['subscriberCount'])
        })

    # Close the connection
    client.close()



"""Streamlit App connection"""

# Streamlit app
def main():
    # Set Streamlit app title
    st.title("YouTube Channel Data Migration")

    # Add input field for YouTube channel ID
    channel_id = st.text_input("Enter YouTube Channel ID")

    # Retrieve channel details using YouTube API
    if st.button("Get Channel Details"):
        channel_data = get_channel_details(channel_id)
        if channel_data:
            st.subheader("Channel Details")
            st.write("Channel ID:", channel_data['id'])
            st.write("Channel Name:", channel_data['snippet']['title'])
            st.write("Subscribers:", channel_data['statistics']['subscriberCount'])
        else:
            st.write("Unable to retrieve channel details. Please check the channel ID.")

    # Add checkbox to select channels for migration
    selected_channels = st.multiselect("Select Channels for Migration", [channel_id])

    # Add button to initiate migration to SQL Database
    if st.button("Migrate to SQL Database"):
        migrate_to_sql_database(selected_channels)
        st.write("Migration to SQL Database successful!")

    # Add button to initiate migration to MongoDB Database
    if st.button("Migrate to MongoDB"):
        migrate_to_mongodb(selected_channels)
        st.write("Migration to MongoDB successful!")

# Run the Streamlit app
if __name__ == '__main__':
    main()
