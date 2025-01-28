import streamlit as st
from PIL import Image
import random
import base64
from openai import OpenAI
from streamlit_geolocation import streamlit_geolocation

# Streamlit App
st.title("Ontario Fishing Companion")

# Get GPS location and Camera input
st.header("Identify Your Catch and Location")
location = streamlit_geolocation()

uploaded_image = st.camera_input("Take a picture of your fish")

if location and "latitude" in location and "longitude" in location and uploaded_image is not None:
    latitude = location["latitude"]
    longitude = location["longitude"]
    st.write(f"Your location: Latitude {latitude}, Longitude {longitude}")

    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Encode the image in Base64
    image_bytes = uploaded_image.getvalue()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    if "OpenAI_key" in st.secrets:
        openai_api_key = st.secrets["OpenAI_key"]
        client = OpenAI(api_key=openai_api_key)

        try:
            # Step 1: Use Vision API to identify the fish
            vision_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What is the fish type in this image? Can you provide the description?"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                        ],
                    }
                ],
                max_tokens=300,
            )

            fish_info = vision_response.choices[0].message.content
            st.subheader("Fish Identification")
            st.write(fish_info)

            # Extract fish type from the response (mock example for processing response)
            fish_type = "Northern Pike"  # Replace with logic to extract fish type from fish_info

            # Step 2: Upload PDF file to OpenAI API (only once)
            pdf_file_path = "2025fishingregulationssummary.pdf"
            if not st.session_state.get("file_id"):
                with open(pdf_file_path, "rb") as pdf_file:
                    uploaded_file = client.files.create(
                        file=pdf_file,
                        purpose="assistants"
                    )
                file_id = uploaded_file.id
                st.session_state["file_id"] = file_id
                st.write(f"File uploaded successfully! File ID: {file_id}")
            else:
                file_id = st.session_state["file_id"]
                st.write(f"Using previously uploaded file. File ID: {file_id}")

            # Step 3: Retrieve PDF content and use it for regulation lookup
            regulation_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Based on the GPS coordinates Latitude {latitude} and Longitude {longitude}, identify the closest fishing zone in Ontario, Canada then Using the uploaded PDF file (ID: {file_id}) and the identified fish type ({fish_type}), determine the opening season and limit to keep in that zone."
                    }
                ],
                max_tokens=700,
            )

            regulation_info = regulation_response.choices[0].message.content
            st.subheader("Fishing Zone and Regulations")
            st.write(regulation_info)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("OpenAI API key not found in secrets.")

# Knowledge-sharing section
st.header("Learn Ontario Fishing Regulations")
try:
    with open("tips.txt", "r") as tips_file:
        tips = tips_file.readlines()
        if tips:
            random_tip = random.choice(tips).strip()
            st.info(f"**Fishing Tip:** {random_tip}")
        else:
            st.error("No tips available in the tips file.")
except FileNotFoundError:
    st.error("The tips.txt file was not found. Please ensure it exists in the directory.")

# Footer
st.markdown("---")
st.markdown("Developed to make your fishing trips enjoyable and compliant with Ontario's fishing laws.")
