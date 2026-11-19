#---------------import libraries------------------------------------------
import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import pandas as pd
import matplotlib.pyplot as plt
import math

#---------------set spotify api credentials------------------------------------

login=spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='67d9a0d08e554343a0d71d3688fdee7f',
    client_secret='acb11a3000b44fa0a30fda562c6ccfba'
))

#---------------mysql credentials for congfiguration---------------------------
db_config={
    'host':'localhost',
    'user':'root',
    'password':'root',
    'database':'spotify_tracks'
}

#---------------connect mysql db & cursor------------------------------------
connection = mysql.connector.connect(**db_config)
Curser = connection.cursor()

#----------------get spotify track url by read the track urls from file---------------------------------------
file_path="track_urls.txt"
with open(file_path, 'r') as files:
    track_urls = files.readlines( )
    
all_tracks = []

# process each url
for track_url in track_urls:
    track_url=track_url.strip()#to remove unwanted extra space from both leading/tailing part
    if not track_url: #skip the empty lines
        continue
    try:
        #get unique id of the track by using regex searchh pattern
        track_id = re.search(r'track/([a-zA-Z0-9]+)', track_url).group(1)#get all details about the specified track in json format
        track = login.track(track_id)

        #----------------meta data filiteration---------------------------------------
        track_data = {
            'Track name': track['name'],
            'Artist': track['artists'] [0] ['name'],
            'Album': track['album'] ['name'],
            'Total tracks': track['album'] ['total_tracks'],
            'Duration (min)': track['duration_ms'] / 60000
        }

        #----------------------------make a insert query to insert responsive values to db---------------------------------------
        insert_query=""" insert into tracks (track_name, artist, album, total_tracks, duration_minute) values (%s,%s,%s,%s,%s) """

        #execute the query 
        Curser.execute(insert_query, (
            track_data['Track name'],
            track_data['Artist'],
            track_data['Album'],
            track_data['Total tracks'],
            track_data['Duration (min)']
        ))

        #commit the action
        connection.commit()
        
        all_tracks.append(track_data)

        #disply a message to notify suceesfully data inserted to db
        print(f"\nThe track {track_data['Track name']} by {track_data['Artist']} inserted sucessfully to the db.")
        
    except Exception as e:
        print(f"Error processing url: {track_url}, Error: {e}")


#close the curser & connection
Curser.close()
connection.close()
print(f"\n______________________________________________________________________________________________________________________________________________________")
print(f"\nAll the tracks have been processed and inserted into the db.\n")

#-------------------------------display data as row & column using pandas-------------------------------
row=pd.DataFrame(all_tracks)
print(f"\n_____________________________________________________________________________________________________________________________________________________")
print(row)
print(f"\n_____________________________________________________________________________________________________________________________________________________")
#convert the data to csv file
row.to_csv("Spotify_track_analysis", index=False)

#--------------------make a bar-graph using matplotlib------------------
lenghts = len(all_tracks)
cols = 3
rows = math.ceil(lenghts/cols)

fig, axes = plt.subplots(rows, cols, figsize=(10, 3 * rows)) #fig gives a full screen # axes gives the grid graph boxes
#axes give values like [[a1, a2, a3], [a4,a5,a6], [a7,a8,a9]] its reds only rows error when use it for loop 
axes = axes.flatten()    #flatten gives 1D values [a1,a2,a3,a4,a5,a6,a7,a8,a9] good for use loop
for ax, track_data in zip(axes, all_tracks): #set each track for each grid
    valx=['Total tracks', 'Duration (min)']
    valy=[track_data['Total tracks'], track_data['Duration (min)']]
    ax.bar(valx, valy, color='red', edgecolor='black')
    ax.set_title(track_data['Track name'], fontsize=9)
    ax.set_ylabel('Values')

for ax in axes[lenghts:]:
    ax.axis('off')
    
fig.suptitle("Spotify Track Analysis", fontsize=9)
plt.tight_layout() #automatically adjust spaces around grid remove labels overlaps
plt.show() 