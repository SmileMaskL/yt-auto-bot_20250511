# scripts/main.py
import os
import sys
import json
import requests # Keep for potential future use, though not directly used now
import subprocess
import wave
import logging
import base64
import random
import binascii # For Base64 validation
from datetime import datetime, timezone
from contextlib import closing

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from openai import OpenAI, OpenAIError

# Import from other modules in the 'scripts' package
try:
    from .notifier import send_notification
except ImportError:
    send_notification = None # Will be handled gracefully
    # logging.info is not configured yet, so print for now if critical
    print("Warning: Notifier module could not be imported. Notifications will be disabled.", file=sys.stderr)


try:
    from .content_generator import ContentGenerator, OpenAIKeyManager
except ImportError as e:
    print(f"FATAL: Could not import ContentGenerator or OpenAIKeyManager: {e}. Exiting.", file=sys.stderr)
    sys.exit(1)


# --- Global Configuration & Logging Setup ---
LOG_FILE_PATH = "automation_main.log" # Specific log for main.py
# Configure root logger if not already configured by other modules at import time
# This setup aims to be robust.
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout) # Also log to console
        ]
    )
# Get a logger specific to this module
logger = logging.getLogger(__name__)


# --- Environment Variable Loading and Validation (Early Check) ---
# Most detailed validation is in validate_env.py, but some key ones can be checked here too.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN")


# --- OpenAI Configuration ---
try:
    # Initialize key manager once
    openai_key_manager = OpenAIKeyManager(env_var_name="OPENAI_API_KEYS_BASE64")
    # Initialize content generator
    content_gen = ContentGenerator(key_manager=openai_key_manager, model="gpt-4-turbo-preview") # Or your preferred model
except (EnvironmentError, ValueError) as e:
    logger.critical(f"🚨 Failed to initialize OpenAI components: {e}. This is a fatal error.")
    if send_notification:
        send_notification(f"🚨 AUTOMATION FAILED (FATAL): OpenAI setup error: {e}")
    sys.exit(1)


def get_openai_client() -> OpenAI:
    """Returns an OpenAI client with a randomly chosen key."""
    return OpenAI(api_key=openai_key_manager.get_random_key(), timeout=60.0)


# --- Text & Script Generation ---
def generate_youtube_script(topic: str) -> str:
    """Generates a YouTube script for a given topic."""
    logger.info(f"🖋️ Generating YouTube script for topic: '{topic}'")
    system_prompt = (
        "You are an AI assistant tasked with creating a concise, engaging, and informative YouTube shorts script. "
        "The script should be structured in short, impactful sentences. "
        "Ensure the content is factual and easy to understand for a general audience. "
        "The output should be the raw script text, suitable for text-to-speech conversion. "
        "Do not include any meta-instructions like '(Pause)' or '[Scene change]' in the final script. "
        "The script should be around 150-250 words to fit a ~60 second short."
        "The script must end with a proper punctuation mark."
    )
    user_prompt = (
        f"Create a YouTube shorts script about the following topic: '{topic}'. "
        "Summarize the key aspects in 2-3 main points. "
        "Make it interesting and suitable for a voice-over."
    )
    try:
        script_text = content_gen.generate_text(prompt=user_prompt, system_message=system_prompt)
        if not script_text or len(script_text) < 50: # Arbitrary minimum length
            logger.error("🚨 Generated script content is too short or empty.")
            raise ValueError("Generated script content is insufficient.")
        logger.info(f"📜 Script generated successfully (length: {len(script_text)}). Preview: '{script_text[:100]}...'")
        return script_text
    except Exception as e:
        logger.error(f"❌ Failed to generate script: {e}")
        raise


# --- Voice Generation (using OpenAI TTS) ---
def generate_audio_openai(text_to_speak: str, output_audio_path: str) -> bool:
    """Generates audio from text using OpenAI TTS and saves it."""
    logger.info(f"🗣️ Generating audio for text (first 50 chars): '{text_to_speak[:50]}...'")
    client = get_openai_client()
    try:
        response = client.audio.speech.create(
            model="tts-1-hd", # High quality
            voice="nova",     # Choose a voice: alloy, echo, fable, onyx, nova, shimmer
            input=text_to_speak,
            response_format="mp3" # Also supports opus, aac, flac
        )
        response.stream_to_file(output_audio_path)
        logger.info(f"✅ Audio file saved successfully: '{output_audio_path}'")
        return True
    except OpenAIError as e:
        logger.error(f"❌ OpenAI TTS API error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate or save audio file: {e}")
        raise
    return False


# --- Audio Processing ---
def get_audio_duration_ffmpeg(audio_path: str) -> float:
    """Gets audio duration using ffprobe (more reliable for various formats)."""
    if not os.path.exists(audio_path):
        logger.error(f"🚨 Audio file not found at '{audio_path}' for duration check.")
        raise FileNotFoundError(f"Audio file '{audio_path}' not found.")
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        duration = float(result.stdout.strip())
        logger.info(f"⏱️ Audio duration via ffprobe: {duration:.2f} seconds for '{audio_path}'.")
        return duration
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ ffprobe failed to get duration for '{audio_path}'. Error: {e.stderr}")
        raise
    except ValueError as e:
        logger.error(f"❌ Could not parse ffprobe duration output for '{audio_path}'. Output: '{result.stdout if 'result' in locals() else 'N/A'}'. Error: {e}")
        raise
    except Exception as e: # Catch other potential errors like ffprobe not found
        logger.error(f"❌ An unexpected error occurred while getting audio duration with ffprobe for '{audio_path}': {e}")
        raise


# --- Subtitle Generation (Simple SRT) ---
def generate_srt_subtitles(script_text: str, total_duration_seconds: float, output_srt_path: str, segments: int = 10):
    """Generates a simple SRT subtitle file by dividing text and duration into segments."""
    logger.info(f"📝 Generating SRT subtitles for '{output_srt_path}'. Total duration: {total_duration_seconds:.2f}s, Segments: {segments}")
    if total_duration_seconds <= 0:
        logger.error("🚨 Total duration must be positive to generate subtitles.")
        raise ValueError("Total duration for subtitles must be positive.")
    if segments <= 0:
        logger.error("🚨 Number of segments must be positive.")
        segments = 1 # Fallback to at least one segment

    lines = [line.strip() for line in script_text.split('.') if line.strip()]
    if not lines: # If splitting by '.' yields nothing, use the whole text as one line.
        lines = [script_text.strip()]
        logger.warning("⚠️ Script text could not be split by periods for subtitles; using the whole text as one segment.")
        segments = 1 # Override segments if we only have one line.
    
    # Distribute lines among segments more evenly if lines < segments
    num_actual_segments = min(len(lines), segments)
    if num_actual_segments == 0: # Should not happen if lines has content
        logger.error("🚨 No text lines available for subtitle generation.")
        # Create an empty or minimal SRT to avoid downstream errors
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:00,000 --> 00:00:01,000\n(No subtitle content)\n\n")
        return

    time_per_segment = total_duration_seconds / num_actual_segments

    try:
        with open(output_srt_path, 'w', encoding='utf-8') as srt_file:
            current_line_index = 0
            for i in range(num_actual_segments):
                start_time_s = i * time_per_segment
                end_time_s = (i + 1) * time_per_segment
                if i == num_actual_segments - 1: # Ensure last segment ends at total duration
                    end_time_s = total_duration_seconds
                
                # Prevent end time from being less than start time (e.g. if total_duration_seconds is very small)
                if end_time_s <= start_time_s:
                    end_time_s = start_time_s + 0.1 # Min 100ms duration

                start_time_str = format_time_srt(start_time_s)
                end_time_str = format_time_srt(end_time_s)
                
                # Assign lines to this segment
                # This logic tries to distribute lines somewhat evenly if len(lines) > num_actual_segments
                lines_for_this_segment_count = (len(lines) + num_actual_segments - 1) // num_actual_segments if i == 0 else \
                                               len(lines) // num_actual_segments 
                
                # A simpler distribution:
                start_idx = (i * len(lines)) // num_actual_segments
                end_idx = ((i + 1) * len(lines)) // num_actual_segments
                segment_text_lines = lines[start_idx:end_idx]
                
                segment_text = " ".join(segment_text_lines).strip()
                if not segment_text: # Handle case where a segment might get no text
                    segment_text = "(...)"


                srt_file.write(f"{i + 1}\n")
                srt_file.write(f"{start_time_str} --> {end_time_str}\n")
                srt_file.write(f"{segment_text}\n\n")
        logger.info(f"✅ SRT subtitles generated successfully: '{output_srt_path}'")
    except Exception as e:
        logger.error(f"❌ Failed to generate SRT subtitles: {e}")
        raise

def format_time_srt(seconds: float) -> str:
    """Converts seconds to HH:MM:SS,mmm format for SRT."""
    delta = datetime.fromtimestamp(seconds, tz=timezone.utc) - datetime.fromtimestamp(0, tz=timezone.utc)
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds_full = divmod(remainder, 60)
    sec = int(seconds_full)
    ms = int((seconds_full - sec) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{sec:02d},{ms:03d}"


# --- Video Creation (FFmpeg) ---
def create_video_with_ffmpeg(
    audio_path: str,
    subtitle_path: str,
    background_image_path: str, # e.g., "background.jpg" in root
    font_file_path: str,      # e.g., "fonts/NotoSansCJKkr-Regular.otf"
    output_video_path: str,
    video_duration_seconds: float,
    resolution: str = "1080x1920" # Portrait for Shorts
):
    """Creates a video with background, audio, and styled subtitles using FFmpeg."""
    logger.info(f"🎬 Creating video '{output_video_path}' with duration {video_duration_seconds:.2f}s.")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not os.path.exists(subtitle_path):
        raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
    if not os.path.exists(font_file_path):
        # This might not be fatal if FFmpeg can find the font by name, but direct path is safer
        logger.warning(f"⚠️ Font file not found at '{font_file_path}'. FFmpeg might try system fonts.")
        # For subtitles filter, FontName might be better if font is installed system-wide
        # However, force_style with FontFile is more explicit for CI/CD
    
    use_background_image = True
    if not os.path.exists(background_image_path):
        logger.warning(f"⚠️ Background image '{background_image_path}' not found. Using a default blue color background.")
        use_background_image = False

    # FFmpeg requires path escaping for subtitles filter, especially on Windows for ':'
    # For Linux/macOS, direct paths are usually fine unless they contain special characters.
    # A robust way is to ensure paths are simple or use fontconfig FontName if available.
    # Escaping colon for Windows in filter: 'C\:/path/to/font' -> 'C\\:/path/to/font' or 'C\\:\\\\path\\\\to\\\\font'
    # For this purpose, we assume font_file_path is either a system font name recognized by fontconfig,
    # or a path that ffmpeg can directly access (e.g., relative path in build env, or correctly escaped absolute path).
    # Using FontName is often more portable if the font is installed.
    # Using FontFile needs careful path handling.
    
    # Let's assume font_file_path is the direct path to the .otf file for FontFile
    # The 'subtitles' filter syntax for font file needs careful path escaping
    # On Linux/macOS, often just the path works. On Windows, it's tricky.
    # A simpler approach is to ensure the font is findable by FontName (e.g., by fontconfig)
    # Example: force_style='FontName=Noto Sans CJK KR Regular,FontSize=...'
    # If using FontFile: force_style='FontFile=/path/to/your/font.otf,FontSize=...'
    # Path for subtitle filter needs to be correctly escaped.
    # For a file in "fonts/NotoSansCJKkr-Regular.otf"
    # ffmpeg_subtitle_font_path = 'fonts/NotoSansCJKkr-Regular.otf' # If running from project root.
    # Or it could be an absolute path.
    
    # Subtitle filter:
    # Use 'force_style' for consistent styling.
    # PrimaryColour: &H00FFFFFF (White). Alpha (00) first, then BBGGRR.
    # OutlineColour: &H00000000 (Black).
    # Alignment: 2 (bottom center for ASS/SSA style, often used by libass)
    subtitle_style = f"FontName=Noto Sans CJK KR,FontSize=48,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=0.5,Alignment=2,MarginV=50"
    # If using font file directly (ensure path is correct and escaped for FFmpeg if needed):
    # subtitle_style = f"FontFile='{font_file_path}',FontSize=48,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Shadow=0.5,Alignment=2,MarginV=50"

    # Use colon escaping for subtitles path only if it's absolute and on Windows.
    # For relative paths like 'subtitles.srt', it's usually not needed.
    escaped_subtitle_path = subtitle_path.replace('\\', '/') # Normalize to forward slashes

    vf_options = [f"subtitles='{escaped_subtitle_path}':force_style='{subtitle_style}'"]
    
    # Add scaling to ensure output is 1080x1920 for shorts
    # Scale the background input first, then overlay subtitles.
    # If background is an image, it will be looped. If color, it's generated.
    # Example: scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2

    ffmpeg_cmd = []
    if use_background_image:
        ffmpeg_cmd.extend([
            "ffmpeg", "-y",
            "-loop", "1", "-i", background_image_path, # Loop background image
            "-i", audio_path,                          # Audio input
            "-vf", f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2,format=yuv420p,{','.join(vf_options)}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(video_duration_seconds),
            output_video_path
        ])
    else: # Default color background
         ffmpeg_cmd.extend([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=blue:s={resolution}:d={video_duration_seconds}", # Blue background
            "-i", audio_path,                          # Audio input
            "-vf", f"format=yuv420p,{','.join(vf_options)}", # Add subtitles to the color input
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            # No -t needed here as color duration already sets it for the primary video stream
            output_video_path
        ])


    logger.info(f"Executing FFmpeg command: {' '.join(ffmpeg_cmd)}")
    try:
        process = subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"✅ Video created successfully: '{output_video_path}'")
        if process.stdout: logger.debug(f"FFmpeg STDOUT:\n{process.stdout}")
        if process.stderr: logger.debug(f"FFmpeg STDERR (might contain useful info even on success):\n{process.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg video creation failed. Return code: {e.returncode}")
        logger.error(f"FFmpeg STDERR:\n{e.stderr}")
        logger.error(f"FFmpeg STDOUT:\n{e.stdout}")
        raise
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during video creation: {e}")
        raise

# --- YouTube API Interaction ---
def get_youtube_credentials() -> Credentials | None:
    """Authenticates with Google API using environment variables for OAuth."""
    logger.info("🔐 Authenticating with Google for YouTube API access...")
    if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN]):
        logger.error("🚨 Google OAuth environment variables (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN) are not fully set.")
        return None
    try:
        creds = Credentials(
            None, # No access token initially
            refresh_token=GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
        # Check if token needs refresh and refresh it.
        # The google-auth library typically handles refresh automatically when a request is made if creds.valid is False.
        # Explicit refresh can be done if needed:
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                logger.info("Google credentials expired, attempting to refresh...")
                try:
                    creds.refresh(GoogleAuthRequest())
                    logger.info("✅ Google credentials refreshed successfully.")
                except Exception as e:
                    logger.error(f"❌ Failed to refresh Google credentials: {e}")
                    return None
            else: # No refresh token or not expired but invalid for other reasons
                logger.error("🚨 Google credentials are not valid and cannot be refreshed (missing refresh token or other issue).")
                return None
        
        logger.info("✅ Google API authentication successful (or token is ready for refresh on use).")
        return creds
    except Exception as e:
        logger.error(f"❌ Error during Google authentication setup: {e}")
        return None

def upload_video_to_youtube(
    video_file_path: str,
    title: str,
    description: str,
    tags: list[str] = None,
    category_id: str = "28", # 28 = Science & Technology, 22 = People & Blogs, 25 = News & Politics
    privacy_status: str = "private" # "private", "public", "unlisted"
) -> str | None:
    """Uploads a video to YouTube."""
    logger.info(f"⬆️ Preparing to upload video: '{video_file_path}'")
    if not os.path.exists(video_file_path):
        logger.error(f"🚨 Video file for upload not found: '{video_file_path}'")
        return None

    credentials = get_youtube_credentials()
    if not credentials:
        logger.error("Aborting YouTube upload due to authentication failure.")
        return None

    try:
        youtube_service = build("youtube", "v3", credentials=credentials, static_discovery=False)
        
        request_body = {
            "snippet": {
                "title": title[:100], # YouTube title limit
                "description": description[:5000], # YouTube description limit
                "tags": tags if tags else ["AI", "Automation", "Python", "YouTubeShorts"],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False # Important for compliance
            }
        }

        logger.info(f"📤 Starting YouTube upload for '{title}'...")
        media_file = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)
        
        response_upload = youtube_service.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        ).execute()

        video_id = response_upload.get("id")
        if not video_id:
            logger.error(f"❌ YouTube upload response did not contain a video ID. Response: {response_upload}")
            return None

        video_url = f"https://www.youtube.com/watch?v={video_id}" # Or https://www.youtube.com/watch?v={video_id}
        logger.info(f"✅ Video uploaded successfully! URL: {video_url}")
        return video_url

    except HttpError as e:
        logger.error(f"❌ Google API HTTP error during YouTube upload: {e.resp.status} {e.content}")
        # Detailed error parsing
        try:
            error_details = json.loads(e.content.decode())
            logger.error(f"Error details: {json.dumps(error_details, indent=2)}")
        except:
            logger.error(f"Raw error content: {e.content.decode(errors='ignore')}")
        return None
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during YouTube upload: {e}", exc_info=True)
        return None


# --- Main Workflow Orchestration ---
def run_automation_workflow():
    """Main function to run the complete automation workflow."""
    logger.info("🚀🚀🚀 Starting YouTube Shorts Automation Workflow 🚀🚀🚀")
    
    # Define output file names
    output_dir = "outputs" # Store all generated files here
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    script_topic = f"Amazing AI facts for {datetime.now().strftime('%B %Y')}" # Dynamic topic example
    
    generated_script_path = os.path.join(output_dir, f"script_{timestamp_str}.txt")
    audio_file_path = os.path.join(output_dir, f"audio_{timestamp_str}.mp3")
    subtitle_file_path = os.path.join(output_dir, f"subtitles_{timestamp_str}.srt")
    final_video_path = os.path.join(output_dir, f"final_video_{timestamp_str}.mp4")
    
    # --- File paths for static assets ---
    # Assuming main.py is in 'scripts/' and assets are in project root or 'fonts/' in root.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Goes up one level from 'scripts'
    background_img_path = os.path.join(project_root, "background.jpg")
    font_file_for_ffmpeg = os.path.join(project_root, "fonts", "NotoSansCJKkr-Regular.otf")


    try:
        # 1. Generate Script
        script_text = generate_youtube_script(topic=script_topic)
        with open(generated_script_path, "w", encoding="utf-8") as f:
            f.write(script_text)
        logger.info(f"✅ Script saved to '{generated_script_path}'")

        # 2. Generate Voice from Script
        generate_audio_openai(script_text, audio_file_path)

        # 3. Get Audio Duration
        audio_duration_sec = get_audio_duration_ffmpeg(audio_file_path)
        
        # Optional: Check for Shorts duration (max 60s, ideally ~58s)
        if audio_duration_sec > 59:
            logger.warning(f"⚠️ Generated audio ({audio_duration_sec:.2f}s) is longer than typical YouTube Shorts length.")
            # Potentially truncate or re-generate script/audio here if strict length is needed.

        # 4. Generate Subtitles
        generate_srt_subtitles(script_text, audio_duration_sec, subtitle_file_path, segments=10)

        # 5. Create Video
        create_video_with_ffmpeg(
            audio_path=audio_file_path,
            subtitle_path=subtitle_file_path,
            background_image_path=background_img_path,
            font_file_path=font_file_for_ffmpeg, # This is for direct FontFile use in ffmpeg if configured
            output_video_path=final_video_path,
            video_duration_seconds=audio_duration_sec,
            resolution="1080x1920" # Portrait for Shorts
        )

        # 6. Upload to YouTube
        video_title = f"AI Fun Facts: {datetime.now().strftime('%b %d, %Y')} #shorts"
        video_description = (
            f"Check out these amazing AI fun facts for {datetime.now().strftime('%B %Y')}!\n\n"
            f"Content generated by AI.\n\n"
            f"#AIShorts #FunFacts #Tech #ArtificialIntelligence #Automation\n\n"
            f"Original script:\n{script_text[:300]}..." # Include part of script
        )
        
        uploaded_video_url = upload_video_to_youtube(
            video_file_path=final_video_path,
            title=video_title,
            description=video_description,
            category_id="28", # Science & Technology
            privacy_status="public"  # Change to "private" for testing
        )

        if uploaded_video_url:
            success_message = f"✅🎉 Automation workflow COMPLETED successfully! Video uploaded: {uploaded_video_url}"
            logger.info(success_message)
            if send_notification:
                send_notification(success_message)
        else:
            error_message = "⚠️ Automation workflow completed, but YouTube upload FAILED or returned no URL."
            logger.error(error_message)
            if send_notification:
                send_notification(error_message)

    except FileNotFoundError as e: # Specific handling for missing critical files
        logger.critical(f"🚨 CRITICAL FILE NOT FOUND: {e}. Workflow cannot continue.", exc_info=True)
        if send_notification:
            send_notification(f"🚨 AUTOMATION FAILED (FATAL): Critical file missing: {e}")
    except OpenAIError as e:
        logger.critical(f"🚨 OpenAI API related error: {e}. Workflow halted.", exc_info=True)
        if send_notification:
            send_notification(f"🚨 AUTOMATION FAILED (FATAL): OpenAI API error: {e}")
    except HttpError as e: # Google API HTTP errors
        logger.critical(f"🚨 Google API HTTP error: {e.resp.status} - {e.content}. Workflow halted.", exc_info=True)
        if send_notification:
            send_notification(f"🚨 AUTOMATION FAILED (FATAL): Google API HTTP error: {e.resp.status}")
    except Exception as e:
        logger.critical(f"❌ An unexpected error occurred in the main workflow: {e}", exc_info=True)
        if send_notification:
            send_notification(f"🚨 AUTOMATION FAILED (UNEXPECTED): {e}")
    finally:
        logger.info("🏁🏁🏁 YouTube Shorts Automation Workflow Finished 🏁🏁🏁")


if __name__ == "__main__":
    # Perform initial environment validation using the separate script (optional, good for CI)
    # In a CI environment, this might be a separate step. Here, we can call it too.
    logger.info("Running initial environment validation via subprocess...")
    validation_process = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "validate_env.py")],
        capture_output=True, text=True
    )
    if validation_process.returncode != 0:
        logger.error(f"🚨 Environment validation script FAILED. Output:\n{validation_process.stdout}\n{validation_process.stderr}")
        logger.error("Halting main.py due to environment validation failure.")
        if send_notification:
             send_notification("🚨 AUTOMATION HALTED: Environment validation FAILED. Check logs.")
        sys.exit(1)
    else:
        logger.info(f"✅ Environment validation script PASSED. Output:\n{validation_process.stdout}")
    
    run_automation_workflow()
