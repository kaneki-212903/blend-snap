import os
import streamlit as st
from PIL import Image
import glob
from main import FaceAverager

# Ensure the images directory exists
if not os.path.exists("images"):
    os.makedirs("images")

# Streamlit UI for image upload
st.title("Upload Images for Average Face Generation")

# File uploader for multiple image files
uploaded_files = st.file_uploader("Choose images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    # Save uploaded images to 'images' folder
    for i, uploaded_file in enumerate(uploaded_files):
        img = Image.open(uploaded_file)
        img_path = os.path.join("images", f"uploaded_image_{i}.png")
        img.save(img_path)
        st.image(img, caption=f"Uploaded Image {i+1}", use_column_width=True)
    
    st.write(f"Total images uploaded: {len(uploaded_files)}")

    # Gather image paths
    image_paths = glob.glob("images/*.png") + glob.glob("images/*.jpg")
    for i in range(len(image_paths)):
        image_paths[i] = image_paths[i].replace("\\", "/")
    
    # Process images if they exist
    if image_paths:
        st.write("Processing images...")

        face_averager = FaceAverager(target_size=(800, 1000))  # Adjust target size as needed
        face_averager.load_images(image_paths)
        face_averager.compute_average_shape()
        average_face = face_averager.create_average_face()

        # Display the average face
        st.image(average_face, caption="Average Face", use_column_width=True)

        # Calculate handsomeness scores
        face_to_be_checked = list(range(len(image_paths)))
        scores = []
        for i in face_to_be_checked:
            score = face_averager.calculate_handsomeness_index(image_paths[i])
            scores.append(score)

        st.write("Scores for each face:")
        for i, score in enumerate(scores):
            st.write(f"Image {i+1}: Handsomeness Score: {score}")

        # Optionally, delete the images after processing
        for path in image_paths:
            os.remove(path)
        st.write("Images deleted after processing.")
