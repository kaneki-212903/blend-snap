import cv2
import mediapipe as mp
import numpy as np
import streamlit as st 
from PIL import Image 
from skimage.metrics import structural_similarity as ssim
from random import randrange
import os
import glob

class FaceAverager:
    def __init__(self, target_size=(800, 1000)):  # Increased target size
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
        self.images = []
        self.landmarks_list = []
        self.average_landmarks = None
        self.target_size = target_size
        self.original_images = []

    def _get_face_bounds(self, landmarks, image_shape):
        # Get face bounding box with larger margins
        x_coords = [lm[0] for lm in landmarks]
        y_coords = [lm[1] for lm in landmarks]
        
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        
        # Increase margins significantly
        left = max(0, int(min(x_coords) - 0.5 * width))
        right = min(image_shape[1], int(max(x_coords) + 0.5 * width))
        top = max(0, int(min(y_coords) - 0.7 * height))  # More margin on top for forehead
        bottom = min(image_shape[0], int(max(y_coords) + 0.4 * height))  # More margin for chin
        
        return left, top, right, bottom

    def _resize_image(self, image, landmarks):
        # Get face bounds with larger margins
        left, top, right, bottom = self._get_face_bounds(landmarks, image.shape)
        face_img = image[top:bottom, left:right]
        
        # Resize while maintaining aspect ratio
        target_w, target_h = self.target_size
        h, w = face_img.shape[:2]
        scale = min(target_w/w, target_h/h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(face_img, (new_w, new_h))
        
        # Create canvas and center the face
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        # Adjust landmarks to new coordinates
        adjusted_landmarks = []
        for (x, y) in landmarks:
            new_x = ((x - left) * new_w / (right - left)) + x_offset
            new_y = ((y - top) * new_h / (bottom - top)) + y_offset
            adjusted_landmarks.append((int(new_x), int(new_y)))
        
        return canvas, adjusted_landmarks

    def load_images(self, image_paths):
        for path in image_paths:
            img = cv2.imread(path)
            if img is None:
                print(f"Failed to load image: {path}")
                continue
            
            self.original_images.append(img)
            landmarks = self._get_landmarks(img)
            
            if landmarks:
                resized_img, adjusted_landmarks = self._resize_image(img, landmarks)
                self.images.append(resized_img)
                self.landmarks_list.append(adjusted_landmarks)
                print(f"Successfully processed: {path}")
            else:
                print(f"No face detected in: {path}")

    def _get_landmarks(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        if not results.multi_face_landmarks:
            return None

        landmarks = []
        for lm in results.multi_face_landmarks[0].landmark:
            x, y = int(lm.x * image.shape[1]), int(lm.y * image.shape[0])
            landmarks.append((x, y))
        return landmarks

    def compute_average_shape(self):
        if not self.landmarks_list:
            raise ValueError("No landmarks detected in images")
        self.average_landmarks = np.mean(self.landmarks_list, axis=0).astype(np.int32)
        return self.average_landmarks

    def _find_landmark_index(self, point, landmarks):
        point = np.array(point)
        landmarks = np.array(landmarks)
        distances = np.linalg.norm(landmarks - point, axis=1)
        return np.argmin(distances)

    def warp_to_average(self, image, landmarks):
        rect = (0, 0, self.target_size[0], self.target_size[1])
        subdiv = cv2.Subdiv2D(rect)
        
        # Use more landmarks for better coverage of the entire face
        key_landmarks_indices = [
            # Forehead
            10, 108, 297, 332,
            # Eyes
            33, 133, 362, 263,
            # Nose
            61, 291, 199,
            # Mouth
            0, 17, 267, 397,
            # Jaw
            132, 58, 172, 136, 150, 149, 176, 148, 152,
            # Eyebrows
            70, 63, 105, 66, 107,
            336, 296, 334, 293, 300,
            # Cheeks
            447, 350, 349, 348, 347, 346, 345, 344,
            127, 234, 127, 137, 177, 215, 138, 135,
            # Extra points for better coverage
            168, 197, 5, 4, 75, 97, 2, 326, 305, 33, 246, 161, 160, 159, 158, 157, 173
        ]
        
        points = np.array(self.average_landmarks)[key_landmarks_indices]
        
        for pt in points:
            subdiv.insert((int(pt[0]), int(pt[1])))

        triangles = subdiv.getTriangleList()
        warped_image = np.zeros_like(image)
        
        for triangle in triangles:
            x1, y1, x2, y2, x3, y3 = triangle
            
            idx1 = self._find_landmark_index((x1, y1), self.average_landmarks)
            idx2 = self._find_landmark_index((x2, y2), self.average_landmarks)
            idx3 = self._find_landmark_index((x3, y3), self.average_landmarks)
            
            pts1 = np.float32([
                landmarks[idx1],
                landmarks[idx2],
                landmarks[idx3]
            ])
            
            pts2 = np.float32([
                self.average_landmarks[idx1],
                self.average_landmarks[idx2],
                self.average_landmarks[idx3]
            ])
            
            warp_mat = cv2.getAffineTransform(pts1, pts2)
            mask = np.zeros_like(image)
            cv2.fillConvexPoly(mask, pts2.astype(np.int32), (1, 1, 1))
            warped_triangle = cv2.warpAffine(image, warp_mat, (image.shape[1], image.shape[0]))
            warped_image += warped_triangle * mask

        return warped_image

    def create_average_face(self):
        if not self.images or not self.landmarks_list:
            raise ValueError("No images or landmarks loaded")
            
        warped_images = []
        for img, lm in zip(self.images, self.landmarks_list):
            warped = self.warp_to_average(img, lm)
            warped_images.append(warped)
            
        warped_array = np.array(warped_images)
        avg_face = np.mean(warped_array, axis=0).astype(np.uint8)
        return avg_face

    def create_visualization(self, average_face):
        # Larger display size for better visibility
        display_size = (150, 250)  # Increased size for each image in the grid
        resized_inputs = []
        
        for img in self.images:
            resized = cv2.resize(img, display_size)
            resized_inputs.append(resized)
        
        resized_avg = cv2.resize(average_face, display_size)
        
        n_images = len(resized_inputs) + 1
        n_cols = 3
        n_rows = (n_images + n_cols - 1) // n_cols
        
        canvas = np.zeros((n_rows * display_size[1], n_cols * display_size[0], 3), dtype=np.uint8)
        
        # Add labels to the images
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        
        # Place input images with labels
        for idx, img in enumerate(resized_inputs):
            row = idx // n_cols
            col = idx % n_cols
            y = row * display_size[1]
            x = col * display_size[0]
            canvas[y:y+display_size[1], x:x+display_size[0]] = img
            
            # Add label
            label = f"Face {idx + 1}"
            cv2.putText(canvas, label, (x + 10, y + 30), font, font_scale, (255, 255, 255), font_thickness)
        
        # Place average face with label
        last_idx = len(resized_inputs)
        row = last_idx // n_cols
        col = last_idx % n_cols
        y = row * display_size[1]
        x = col * display_size[0]
        canvas[y:y+display_size[1], x:x+display_size[0]] = resized_avg
        cv2.putText(canvas, "Average Face", (x + 10, y + 30), font, font_scale, (255, 255, 255), font_thickness)
        
        return canvas

    def save_visualization(self, visualization, output_path="output_image.png"):
        cv2.imwrite(output_path, visualization)
        print(f"Visualization saved as {output_path}")

    def display_image(self, image, window_name="Image"):
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def calculate_handsomeness_index(self, image_path):
        img = cv2.imread(image_path)
        landmarks = self._get_landmarks(img)
        if landmarks is None:
            raise ValueError("No face detected in the image")

        warped_image= self.warp_to_average(img, landmarks)
        avg_face_resized=cv2.resize(self.create_average_face(), (warped_image.shape[1], warped_image.shape[0]))

        min_dim=min(warped_image.shape[0],warped_image.shape[1])
        if min_dim<7:
            raise ValueError("Image is too small to calculate SSIM")

        
        win_size=min(7,min_dim-(min_dim%2==0))
        win_size=max(3,win_size)
        try:
            handsomeness_score,_=ssim(avg_face_resized,
                                    warped_image,
                                    win_size=win_size, 
                                    channel_axis=2,
                                    full=True)
        except ValueError as e:
            raise ValueError("Unable to calculate the similiarity score: {str(e)}")
        handsomeness_index=int(handsomeness_score*100)
        return handsomeness_index

'''if not os.path.exists("images"):
    os.makedirs("images")

#st.title("Upload and save multiple images")

#uploaded_files = st.file_uploader("Choose images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

#if uploaded_files:
#    for i, uploaded_file in enumerate(uploaded_files):
#        img = Image.open(uploaded_file)  # Open the image with PIL
#        
#        # Save image to the "images" folder with a unique name
#        img_path = os.path.join("images", f"uploaded_image_{i}.png")
#        img.save(img_path)
        
#        # Display each uploaded image
#        st.image(img, caption=f"Uploaded Image {i+1}", use_column_width=True)
#        st.write(f"Image {i+1} saved at: {img_path}")

#    st.write(f"Total images uploaded and saved: {len(uploaded_files)}")
    
# Example Usage
image_paths = glob.glob("images/*.png")
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
    face_to_be_checked=[0,1,2,3,4,5,6,7]
    print("Yeh wali dikhani h :",face_to_be_checked)
    scores=[]
    for i in face_to_be_checked:
        score=face_averager.calculate_handsomeness_index(image_paths[i])
        scores.append(score)
    print("Itne sundar hooo tum: ")
    for i in scores:
        print("Yeh score h {scores.index}",i)

    #Delete images after processing
#    for path in image_paths:
#        os.remove(path)

#    st.write("Images deleted after processing")'''