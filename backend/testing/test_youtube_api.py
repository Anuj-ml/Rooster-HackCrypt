# Test script to check YouTube API
import sys
sys.path.insert(0, '../')

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    
    print("Successfully imported YouTubeTranscriptApi")
    print("\nAvailable methods:")
    methods = [m for m in dir(YouTubeTranscriptApi) if not m.startswith('_')]
    for method in methods:
        print(f"  - {method}")
    
    print("\n" + "="*60)
    print("Testing with video ID: aircAruvnKk")
    print("="*60)
    
    # Try different approaches
    video_id = "aircAruvnKk"
    
    # Approach 1: Direct call
    print("\nAttempt 1: Direct get_transcript call")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print(f"  ✓ Success! Got {len(transcript)} segments")
    except AttributeError as e:
        print(f"  ✗ AttributeError: {e}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Approach 2: Instance method
    print("\nAttempt 2: Instance-based approach")
    try:
        api = YouTubeTranscriptApi()
        if hasattr(api, 'get_transcript'):
            transcript = api.get_transcript(video_id)
            print(f"  ✓ Success! Got {len(transcript)} segments")
        else:
            print(f"  ✗ Instance doesn't have get_transcript method")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Approach 3: Check for fetch method
    print("\nAttempt 3: Using fetch method")
    try:
        if hasattr(YouTubeTranscriptApi, 'fetch'):
            result = YouTubeTranscriptApi.fetch(video_id)
            print(f"  ✓ Success with fetch!")
        else:
            print(f"  ✗ No fetch method available")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Approach 4: Using list method
    print("\nAttempt 4: Using list method")
    try:
        if hasattr(YouTubeTranscriptApi, 'list'):
            api = YouTubeTranscriptApi()
            result = api.list(video_id)
            print(f"  ✓ Success with list!")
            print(f"  Type: {type(result)}")
        else:
            print(f"  ✗ No list method available")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        
except ImportError as e:
    print(f"Failed to import: {e}")
