# Software-Engineering-Tools-Lab
Image Blending and Morphing

This is my ECE 364 project. 
Created a GUI with Python that takes in 2 images and creates a morphed image, using the numpy, scipy, imageio and Pillow modules.
First we derived different affine transformation matrices for different sections of the image, based on point correspondences between source and target images that we obtain from the user. The points of interest passed, of either the source or the destination, are used to identify the triangles in both images using the Delaunay triangulation. Then we apply the obtained transformations between the images, and blend two images to have a visually appealing result. The image selection and output is done through a simple GUI application, implemented using PySide and the Qt Framework. The user can select corresponding points on the images that allows for a neatly blended image. These points will then be used to display the result of blending the two images.
 
 Morphing.py:
    a) Affine class that calculates an affine transformation matrix, and applies that transformation over a given region of interest.
    b) Blender class that performs the blending of two images to obtain a single image, or a morph sequence.
    
 MorphingApp.py:
    GUI functions
 
 MorphingGUI.py:
    GUI setup
