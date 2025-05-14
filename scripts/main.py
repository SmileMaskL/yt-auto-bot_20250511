import os
import sys
import logging
from .content_generator import ContentGenerator, OpenAIKeyManager
from .create_video import create_video_from_audio_and_text  # Assuming this function exists in create_video.py
from .notifier import send_notification  # Assuming notifier is properly configured

# --- Configuration ---
LOG_FILE_PATH = "automation_main.log"

# Setting up logging to both console and file with proper encoding and format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# OpenAI setup
# Create an instance of OpenAIKeyManager to manage the OpenAI API keys from GitHub secrets
openai_key_manager = OpenAIKeyManager(env_var_name="OPENAI_API_KEYS_BASE64")
content_gen = ContentGenerator(key_manager=openai_key_manager, model="gpt-4-turbo")

# Function to generate the YouTube script from a given topic
def generate_youtube_script(topic: str) -> str:
    """Generates a YouTube script for a given topic."""
    system_prompt = (
        "Create a YouTube shorts script that is concise, engaging, and informative. "
        "Make sure it is structured in short, impactful sentences, and ends with punctuation."
    )
    user_prompt = f"Create a YouTube shorts script about the following topic: '{topic}'"
    
    try:
        # Generate the script text using the content generator
        script_text = content_gen.generate_text(prompt=user_prompt, system_message=system_prompt)
        logger.info(f"📜 Script generated successfully (length: {len(script_text)}).")
        return script_text
    except Exception as e:
        logger.error(f"❌ Script generation failed: {e}")
        raise

# Function to create a video from the generated script and audio file
def create_video_from_script_and_audio(script_text: str, audio_file_path: str) -> str:
    """Generates a YouTube video from a script and audio file."""
    logger.info(f"🎬 Creating video from script and audio: {audio_file_path}")
    
    # Define the output video file path
    video_output_path = "output_video.mp4"  # Static output path
    
    try:
        # Call the external function to create video from the script and audio
        create_video_from_audio_and_text(script_text, audio_file_path, video_output_path)
        logger.info(f"✅ Video created successfully at {video_output_path}")
        return video_output_path
    except Exception as e:
        logger.error(f"❌ Video creation failed: {e}")
        raise

# Main function to control the complete workflow from script generation to video creation
def main():
    """Main function to control the workflow."""
    topic = "The Benefits of Artificial Intelligence"  # You can change the topic dynamically
    logger.info(f"🚀 Starting automation for topic: '{topic}'")
    
    try:
        # Generate the YouTube script for the topic
        script_text = generate_youtube_script(topic)
        
        # Path to the pre-generated audio file (you could integrate text-to-speech here)
        audio_file_path = "audio_output.mp3"
        
        # Ensure the audio file exists before proceeding
        if not os.path.exists(audio_file_path):
            logger.error(f"❌ Audio file not found: {audio_file_path}")
            raise FileNotFoundError(f"Audio file not found at {audio_file_path}")
        
        # Create the video from the script and audio
        video_output_path = create_video_from_script_and_audio(script_text, audio_file_path)
        
        # Log the successful video creation
        logger.info(f"✅ Video creation completed. Output: {video_output_path}")
    
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        
        # If send_notification is available, send an alert notification
        if send_notification:
            send_notification(f"🚨 Automation failed: {e}")
        
        # Exit with a failure code
        sys.exit(1)

# Ensure the script runs only when executed directly (not imported)
if __name__ == "__main__":
    main()
