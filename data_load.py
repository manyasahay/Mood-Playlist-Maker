import pandas as pd
import spotipy

'''Combining the two streaming history files and making one combined csv, dropped the endtime column'''

data= pd.read_json(r'C:\Users\msaha\OneDrive\Desktop\music_Rec\Spotify Account Data\StreamingHistory_music_0.json')
# df = data.to_csv('history.csv')
df_h1 = pd.read_csv(r'C:\Users\msaha\OneDrive\Desktop\music_Rec\history.csv')
df_h1=df_h1.drop('endTime',axis='columns')

data1 = pd.read_json(r'C:\Users\msaha\OneDrive\Desktop\music_Rec\Spotify Account Data\StreamingHistory_music_1.json')
# df1 = data1.to_csv('history1.csv')
df1_h1=pd.read_csv(r'C:\Users\msaha\OneDrive\Desktop\music_Rec\history1.csv')
df1_h1=df1_h1.drop('endTime',axis='columns')

history_data = pd.concat([df_h1,df1_h1],ignore_index=True)
# Group by artistName and trackName, and take the maximum msPlayed value for each group
df_cleaned = history_data.groupby(['artistName', 'trackName'], as_index=False).agg({'msPlayed': 'max'})
df_cleaned.to_csv('cleaned_combined_history.csv', index=False)

print("Cleaned CSV file has been saved as 'cleaned_combined_history.csv'")
# history_data.to_csv('combined_history.csv')
# print(history_data.head())

# library = pd.read_json(r'C:\Users\msaha\OneDrive\Desktop\music_Rec\Spotify Account Data\YourLibrary.json')

# for item,data in library():
#     lib_track = data
# print(lib_track)

