import os
import requests
import time
import json

# Configuration
API_KEY = os.getenv("RUNWAY_API_KEY")
if not API_KEY:
    raise ValueError("Please set the RUNWAY_API_KEY environment variable.")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

BASE_URL = "https://api.runwayml.com/v1"

# The Ultra-Realistic Prompt
PROMPT = """
Cinematic documentary shot, 8K ultra photorealistic. A confident young man in a modern casual black outfit walks naturally towards the camera on a narrow countryside dirt road, talking casually with realistic lip-sync and expressive hand gestures, slight smile, direct eye contact. 
Environment: Breathtaking village surrounded by lush green rice fields, colorful wildflowers, tall coconut trees, bamboo groves, traditional wooden houses with tin roofs. A peaceful river flows beside the road with swimming ducks, grazing cows, and children playing in the distance. 
Atmosphere: Gentle breeze moving grass, leaves, clothes, and hair physically accurately. Birds flying, butterflies fluttering. Warm golden morning sunlight, soft volumetric rays through trees, subtle lens flare, bright blue sky.
Camera & Tech: Smooth cinematic backward tracking shot (gimbal stabilized), medium framing, shallow depth of field (subject sharp, background bokeh). Natural human walking animation, realistic body mechanics, perfect lip synchronization, highly detailed skin, realistic clothing simulation. HDR lighting, global illumination, ray-traced reflections, soft ambient shadows. 24fps, no jitter, no artifacts, National Geographic style masterpiece.
"""

def create_generation():
    print("Submitting video generation request...")
    
    payload = {
        "model": "gen3-alpha-turbo", # Or 'gen3-alpha' depending on availability
        "promptText": PROMPT,
        "durationSeconds": 5,
        "ratio": "16:9",
        "resolution": "1080p" # Upscale to 4K/8K usually done in post or via specific upscale endpoint
    }

    response = requests.post(f"{BASE_URL}/image_to_video", headers=HEADERS, json=payload) # Note: Text-to-video endpoint might vary, check latest docs. Using generic structure.
    
    # Correction: Runway's T2V endpoint structure
    response = requests.post(f"{BASE_URL}/videos/generate", headers=HEADERS, json=payload)

    if response.status_code != 200:
        print(f"Error submitting request: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    task_id = data.get("id")
    print(f"Task submitted successfully. Task ID: {task_id}")
    return task_id

def check_status(task_id):
    print(f"Checking status for task {task_id}...")
    while True:
        response = requests.get(f"{BASE_URL}/videos/{task_id}", headers=HEADERS)
        if response.status_code != 200:
            print(f"Error checking status: {response.text}")
            break
        
        data = response.json()
        status = data.get("status")
        print(f"Current Status: {status}")
        
        if status == "SUCCEEDED":
            video_url = data.get("output", {}).get("url")
            print(f"Generation complete! Download URL: {video_url}")
            return video_url
        elif status == "FAILED":
            print("Generation failed.")
            return None
        elif status in ["QUEUED", "PROCESSING"]:
            time.sleep(10) # Wait before polling again
        else:
            time.sleep(5)

if __name__ == "__main__":
    task_id = create_generation()
    if task_id:
        check_status(task_id)
