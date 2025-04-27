import streamlit as st
import openai  # Using older version syntax (0.28.0)
import requests
from PIL import Image, ImageDraw
import io
import base64
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="Inspirational Mandala Generator",
    page_icon="🔮",
    layout="wide",
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        background-color: #4c6eaf;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1a365d;
    }
    .frame-option {
        cursor: pointer;
        transition: transform 0.2s;
    }
    .frame-option:hover {
        transform: scale(1.05);
    }
    h1, h2, h3 {
        color: #1a365d;
    }
</style>
""", unsafe_allow_html=True)

# Function to generate mandala prompt for DALL-E
def create_mandala_prompt(inspiration):
    prompt = f"""
    Create a beautiful, detailed mandala art inspired by the word '{inspiration}'. 
    The mandala should be centered, symmetrical, and intricate with a circular pattern.
    Use EXACTLY 3 shades of blue ({', '.join(['dark blue', 'medium blue', 'light blue'])}) 
    and 3 shades of gray ({', '.join(['dark gray', 'medium gray', 'light gray'])}) only.
    The design should be spiritual and meditative with intricate patterns.
    Include subtle elements that relate to '{inspiration}' in the mandala pattern.
    Make it high-contrast against a white background so all details are clearly visible.
    The mandala should be centered in the image with balanced composition.
    """
    return prompt.strip()

# Function to generate the mandala image using DALL-E 3
def generate_mandala_image(api_key, prompt):
    # Set the API key
    openai.api_key = api_key
    
    try:
        # Generate image with DALL-E 3
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get the image URL
        image_url = response['data'][0]['url']
        
        # Download the image
        image_response = requests.get(image_url)
        img = Image.open(io.BytesIO(image_response.content))
        
        return img
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# Function to add frame to the image
def add_frame(image, frame_style):
    frames = {
        "Classic Wood": {"color": "#8B4513", "width": 40},
        "Modern Black": {"color": "#1a1a1a", "width": 30},
        "Silver Metal": {"color": "#C0C0C0", "width": 35}
    }
    
    # Make a copy of the image
    framed_image = image.copy()
    
    # Get frame properties
    frame = frames[frame_style]
    width = frame["width"]
    color = frame["color"]
    
    # Create a draw object
    draw = ImageDraw.Draw(framed_image)
    
    # Draw the frame
    img_width, img_height = framed_image.size
    draw.rectangle((0, 0, img_width-1, width), fill=color)  # Top
    draw.rectangle((0, img_height-width, img_width-1, img_height-1), fill=color)  # Bottom
    draw.rectangle((0, 0, width, img_height-1), fill=color)  # Left
    draw.rectangle((img_width-width, 0, img_width-1, img_height-1), fill=color)  # Right
    
    return framed_image

# Function to get download link for image
def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}"><button style="background-color: #4c6eaf; color: white; padding: 0.5rem 1rem; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">{text}</button></a>'
    return href

# Initialize session state for storing the generated image
if 'mandala_image' not in st.session_state:
    st.session_state.mandala_image = None
if 'framed_images' not in st.session_state:
    st.session_state.framed_images = {}
if 'selected_frame' not in st.session_state:
    st.session_state.selected_frame = "Classic Wood"

# Title and description
st.title("✨ Inspirational Mandala Generator")
st.markdown("""
Generate beautiful Mandala art based on a single word inspiration using DALL-E 3.
The mandala will use exactly 3 shades each of blue and gray, creating a harmonious and balanced design.
""")

# Sidebar for API key and input
with st.sidebar:
    st.header("Settings")
    
    # OpenAI API Key input
    api_key = st.text_input("Enter your OpenAI API key", type="password", help="Your API key is required to use DALL-E 3")
    
    # Input for the inspiration word
    inspiration = st.text_input("Enter a word for inspiration:", placeholder="love, wisdom, harmony, etc.")
    
    # Generate button
    generate_button = st.button("Generate Mandala")
    
    if generate_button and inspiration and api_key:
        with st.spinner("Generating your mandala art..."):
            # Create prompt for DALL-E
            prompt = create_mandala_prompt(inspiration)
            
            # Generate the image
            image = generate_mandala_image(api_key, prompt)
            
            if image:
                st.session_state.mandala_image = image
                
                # Generate all frame options at once
                st.session_state.framed_images = {
                    frame: add_frame(image, frame) 
                    for frame in ["Classic Wood", "Modern Black", "Silver Metal"]
                }
                
                st.success("Mandala generated successfully!")

# Main content area
if st.session_state.mandala_image is not None:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display the framed image
        st.image(
            st.session_state.framed_images[st.session_state.selected_frame],
            caption=f'"{inspiration}" Mandala with {st.session_state.selected_frame} frame',
            use_column_width=True
        )
    
    with col2:
        st.header("Select Frame")
        
        # Create columns for frame options
        frame_cols = st.columns(3)
        frame_options = ["Classic Wood", "Modern Black", "Silver Metal"]
        frame_colors = ["#8B4513", "#1a1a1a", "#C0C0C0"]
        
        for i, (frame, color) in enumerate(zip(frame_options, frame_colors)):
            with frame_cols[i]:
                # Display frame thumbnail (simplified version)
                st.markdown(
                    f"""
                    <div style="
                        background-color: {color}; 
                        padding: 5px; 
                        border-radius: 5px;
                        text-align: center;
                        color: {'white' if color != '#C0C0C0' else 'black'};
                        margin-bottom: 5px;"
                        class="frame-option">
                        {frame}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                # Button to select frame
                if st.button(f"Select", key=f"frame_{i}"):
                    st.session_state.selected_frame = frame
                    st.rerun()
        
        # Download button
        st.markdown("### Download Options")
        st.markdown(
            get_image_download_link(
                st.session_state.framed_images[st.session_state.selected_frame],
                f"mandala_{inspiration}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "Download Mandala"
            ),
            unsafe_allow_html=True
        )
        
        # Display inspiration details
        st.markdown("### Inspiration Details")
        st.markdown(f"**Word:** {inspiration}")
        st.markdown("**Colors Used:** 3 shades of blue and 3 shades of gray")

else:
    # Display placeholder or instructions when no image is generated yet
    st.markdown("""
    ## How to Generate Your Mandala:
    1. Enter your OpenAI API key in the sidebar
    2. Type a single word for inspiration
    3. Click "Generate Mandala"
    4. Choose from three frame options
    5. Download your creation
    
    The mandala will be unique to your inspiration word and will use exactly 3 shades each of blue and gray.
    """)
    
    # Display a sample image or placeholder
    st.image("https://via.placeholder.com/800x800?text=Your+Mandala+Will+Appear+Here", caption="Example mandala placeholder")

# Footer
st.markdown("---")
st.markdown("© 2025 Inspirational Mandala Generator | Created with Streamlit and DALL-E 3")