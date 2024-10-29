#Face Averaging and Handsomeness index

What is beauty or handsomeness? To answer this question we must look at what human brain perceives as beautiful or handsome.For that 
its stated that more closer someones facial features is closer to average more beautiful or handsome he or she is considered to be,

This project generates an "average face" by combining multiple face images, then calculates a **handsomeness index** for a given input
image by measuring its similarity to the average face. This project uses OpenCV for face detection, dlib for facial landmark detection,
and Structural Similarity Index (SSIM) for similarity scoring.
This project was inspired y these articles:

1)  https://learnopencv.com/average-face-opencv-c-python-tutorial/  
2)  https://learnopencv.com/face-swap-using-opencv-c-python/        
3)  https://learnopencv.com/face-morph-using-opencv-cpp-python/
4)  https://learnopencv.com/delaunay-triangulation-and-voronoi-diagram-using-opencv-c-python/
5)  https://learnopencv.com/facial-landmark-detection/

By Satya Mallick 
These also involve links to actual mathematical papers on how the process work.

## Table of Contents
- [Mathematics of Face Averaging](#mathematics-of-face-averaging)
- [Handsomeness Index Calculation](#handsomeness-index-calculation)
- [Class Structure and Usage](#class-structure-and-usage)
- [Installation](#installation)
- [Usage](#usage)

### Mathematics of Face Averaging

The core of face averaging involves these mathematical steps:

1. **Aligning Faces**: 
   - Each face image is aligned using facial landmarks (e.g., eyes, nose) to standardize orientation and position.
   - The alignment helps avoid distortion and ensures all features align closely for averaging.
   - We use affine transformation based on landmarks to rotate, scale, and translate each face to the same position.

2. **Warping and Blending**:
   - Each aligned face is then warped to a reference shape (often the average of landmarks across all faces).
   - Using Delaunay triangulation, each image is divided into smaller triangular regions, and the corresponding triangles in each face 
     are warped onto the average face.
   - **Blending**: Pixel-wise averaging is applied across all images to create the final average face.

### Handsomeness Index Calculation

The handsomeness index is a score out of 100 that reflects how closely a face resembles the average face created from the group. This
score is calculated using the **Structural Similarity Index (SSIM)**, a method for measuring similarity between two images.

- **SSIM Calculation**:
  - The SSIM score measures similarity based on luminance, contrast, and structure between the input image and the average face.
  - The final score is scaled to fall within a range from 0 to 100.


### Class Structure and Usage

The main class in this project, `FaceAverager`, simplifies all these steps, making the code modular and easy to use. Here’s a breakdown of the key methods and how to use them.

#### Key Methods:
- **`generate_average_face(image_paths)`**:
  - Takes a list of image paths as input.
  - Aligns each face and computes the pixel-wise average to create the final average face.
  - Returns the average face image.

- **`calculate_handsomeness_index(face_image_path)`**:
  - Takes a single face image path to evaluate.
  - Calculates the similarity between the input face and the average face generated previously.
  - Returns a score out of 100.

#### Example Usage

Here’s how to use the `FaceAverager` class to generate the average face and calculate a handsomeness index:

```python
from face_averaging import FaceAverager

# Instantiate the class
face_averager = FaceAverager()

# Step 1: Generate the average face
image_paths = ['path/to/image1.jpg', 'path/to/image2.jpg', 'path/to/image3.jpg']
avg_face = face_averager.generate_average_face(image_paths)

# Step 2: Calculate the handsomeness index for a single image
score = face_averager.calculate_handsomeness_index('path/to/face_to_evaluate.jpg')
print(f"Handsomeness Index: {score}")


### Installation

To run the project on you system:
1) Create a virtualenv
2) Clone the repository in the required folder
3) Run the command pip install -r requirments.txt(They may seem a huge number of files but most of the files it includes will already be
                 in your system so only main 5 or 6 dependencies will be installed)

4) You can go to main.py uncomment the code add some images to images folder and update the indexes in face_to_be_checked variable as number
   will go from 0 to number of images-1.If you face error like image not found use image names as upload_image_0 etc.Now run the main.py script 
   if it runs succesfully then you are ready to go.
5) Go to client.py import FaceAverager from main create nstance of the file and you are good to go.

To see how the functions will be used please refer the commented code in main.py it gives in brief how the class is supposed to be used 
you can also refer to ###Class sructure and usage section of this document.

In the commented part a section of how to use streamlit is also given if interested also uncomment the streamlit part and use the command streamlit run main.py

