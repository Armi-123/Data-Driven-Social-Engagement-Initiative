import pandas as pd
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID") or "xyz"  # fallback if not in .env

if not API_KEY:
    raise ValueError("❌ YOUTUBE_API_KEY not found in .env file")

youtube = build("youtube", "v3", developerKey=API_KEY)

def fetch_video_data(max_videos=1000):
    videos = []
    next_page_token = None

    while len(videos) < max_videos:
        request = youtube.search().list(
            part="snippet",
            channelId=CHANNEL_ID,
            maxResults=50,  # max allowed by API per request
            order="date",
            type="video",
            pageToken=next_page_token
        )

        response = request.execute()

        for item in response["items"]:
            video_id = item["id"]["videoId"]

            stats = youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()

            statistics = stats["items"][0]["statistics"]

            videos.append({
                "video_id": video_id,
                "title": item["snippet"]["title"],
                "views": statistics.get("viewCount", 0),
                "likes": statistics.get("likeCount", 0),
                "comments": statistics.get("commentCount", 0),
                "publish_date": item["snippet"]["publishedAt"]
            })

            if len(videos) >= max_videos:
                break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break  # No more videos

    return pd.DataFrame(videos)


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    output_file = os.path.join(RAW_DATA_DIR, "raw_social_data.csv")

    # Load existing CSV if it exists
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file)
    else:
        existing_df = pd.DataFrame()

    # Fetch new videos
    df_new = fetch_video_data(max_videos=1000)

    # Combine and remove duplicates
    df_combined = pd.concat([existing_df, df_new])
    df_combined.drop_duplicates(subset="video_id", inplace=True)


    # Save updated CSV
    df_combined.to_csv(output_file, index=False)

    print("Raw data updated successfully!")
    print(f"Total videos now: {len(df_combined)}")
    print(f"Saved at: {output_file}")
