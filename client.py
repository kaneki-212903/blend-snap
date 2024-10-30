from main import FaceAverager
import os
import streamlit as st 
from PIL import Image
import glob

if not os.path.exists("images"):
    os.makedirs("images")

'''st.title("Upload and save multiple images")

uploaded_files = st.file_uploader("Choose images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        img = Image.open(uploaded_file)  # Open the image with PIL
        
        # Save image to the "images" folder with a unique name
        img_path = os.path.join("images", f"uploaded_image_{i}.png")
        img.save(img_path)
        
        # Display each uploaded image
        st.image(img, caption=f"Uploaded Image {i+1}", use_column_width=True)
        st.write(f"Image {i+1} saved at: {img_path}")

    st.write(f"Total images uploaded and saved: {len(uploaded_files)}")'''
    
# Example Usage
image_paths = glob.glob("images/*.png") + glob.glob("images/*.jpg")
for i in range(len(image_paths)):
    image_paths[i] = image_paths[i].replace("\\", "/")
print(image_paths)
no_paths=len(image_paths)
# Create FaceAverager instance with larger target size
if image_paths:
    
    face_averager = FaceAverager(target_size=(800, 1000))  # Increased size
    face_averager.load_images(image_paths)
    face_averager.compute_average_shape()
    average_face = face_averager.create_average_face()

    # Create and display visualization
    visualization = face_averager.create_visualization(average_face)
    face_averager.display_image(visualization, window_name="Average Face and Input Images")

    # Display visualization in Streamlit
    #st.image(visualization, caption="Average Face and Input Images", use_column_width=True)

    #face_to_be_checked=randrange(no_paths)
    # Dynamically set face_to_be_checked based on the number of images
    face_to_be_checked = list(range(len(image_paths)))
    print("Yeh wali dikhani h :", face_to_be_checked)

    scores = []
    for i in face_to_be_checked:
        score = face_averager.calculate_handsomeness_index(image_paths[i])
        scores.append(score)

    print("Itne sundar hooo tum: ")
    for i, score in enumerate(scores):
        print(f"Yeh score h {i}: {score}")

    #Delete images after processing
    for path in image_paths:
        os.remove(path)

    #st.write("Images deleted after processing")