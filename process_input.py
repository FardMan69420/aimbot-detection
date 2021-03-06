from typing import List, Tuple
import cv2
import os
import math
import random

# remove frames to get an fps of 20
def downsample_frames(clip_name: str, target_file: str, target_fps = 20.0):
  clip = cv2.VideoCapture(clip_name)
  fps = clip.get(cv2.CAP_PROP_FPS)
  length = clip.get(cv2.CAP_PROP_FRAME_COUNT)
  width  = int(clip.get(cv2.CAP_PROP_FRAME_WIDTH))   # float `width`
  height = int(clip.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`

  # Define the codec and create VideoWriter object
  fourcc = cv2.VideoWriter_fourcc(*'mp4v')
  # specify last param for greyscale
  out = cv2.VideoWriter(target_file, fourcc, target_fps, (width,  height))

  frame_count = 0
  while clip.isOpened():
    ret, frame = clip.read()
    if not ret:
      # print("Can't receive frame (stream end?). Exiting ...")
      break

    if length < fps:
      out.write(frame)
    else:
      if fps < 31 and frame_count % 3 == 2:
        out.write(frame)
      elif fps < 61 and frame_count % 2 == 1:
        out.write(frame)
    frame_count += 1

  clip.release()
  out.release()

# create a grayscale version of the video
def toGrayscale(clip_name: str, target_file: str):
  clip = cv2.VideoCapture(clip_name)
  fps = clip.get(cv2.CAP_PROP_FPS)
  length = clip.get(cv2.CAP_PROP_FRAME_COUNT)
  width  = int(clip.get(cv2.CAP_PROP_FRAME_WIDTH))   # float `width`
  height = int(clip.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`

  # Define the codec and create VideoWriter object
  fourcc = cv2.VideoWriter_fourcc(*'mp4v')
  # specify last param for greyscale
  out = cv2.VideoWriter(target_file, fourcc, fps, (width,  height), 0)

  while clip.isOpened():
    ret, frame = clip.read()
    if not ret:
      # print("Can't receive frame (stream end?). Exiting ...")
      break
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    out.write(frame)

  clip.release()
  out.release()

# create context stream
def resize(clip_name: str, size: Tuple[int], target_file: str):
  clip = cv2.VideoCapture(clip_name)
  fps = clip.get(cv2.CAP_PROP_FPS)

  # Define the codec and create VideoWriter object
  fourcc = cv2.VideoWriter_fourcc(*'mp4v')
  # specify last param for greyscale
  out = cv2.VideoWriter(target_file, fourcc, fps, size)

  while clip.isOpened():
    ret, frame = clip.read()
    if not ret:
      # print("Can't receive frame (stream end?). Exiting ...")
      break
    
    frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    out.write(frame)

  clip.release()
  out.release()

# create fovea stream
def crop(clip_name: str, size: Tuple[int], target_file: str):
  clip = cv2.VideoCapture(clip_name)
  fps = clip.get(cv2.CAP_PROP_FPS)
  width = size[0]
  height = size[1]

  # Define the codec and create VideoWriter object
  fourcc = cv2.VideoWriter_fourcc(*'mp4v')
  # specify last param for greyscale
  out = cv2.VideoWriter(target_file, fourcc, fps, size)

  while clip.isOpened():
    ret, frame = clip.read()
    if not ret:
      # print("Can't receive frame (stream end?). Exiting ...")
      break
    
    frame_height, frame_width = frame.shape[0], frame.shape[1]
    crop_width = width if width < frame_width else frame_width
    crop_height = height if height < frame_height else frame_height
    mid_x, mid_y = int(frame_width/2), int(frame_height/2)
    cw2, ch2 = int(crop_width/2), int(crop_height/2) 
    frame = frame[mid_y-ch2:mid_y+ch2, mid_x-cw2:mid_x+cw2]
    out.write(frame)

  clip.release()
  out.release()

# input dir path
input_dataset_path = "./dataset/"
# output dir path
output_path = "./dataset_processed"
# traverse the input dir
cheater_clips = os.listdir(input_dataset_path + "cheating")
not_cheater_clips = os.listdir(input_dataset_path + "not_cheating/very-good-players")
# randomly select test data
cheater_percentage = len(cheater_clips) * 20 / 100
test_cheater_clips = random.sample(cheater_clips, math.floor(cheater_percentage))
not_cheater_percentage = len(not_cheater_clips) * 20 / 100
test_not_cheater_clips = random.sample(not_cheater_clips, math.floor(not_cheater_percentage))

train_cheater_clips = [clip for clip in cheater_clips if clip not in test_cheater_clips]
train_not_cheater_clips = [clip for clip in not_cheater_clips if clip not in test_not_cheater_clips]

# create output dir or throw error if already exists
if os.path.exists(output_path) is False:
  os.mkdir(output_path)
if len(os.listdir(output_path)) > 0:
  raise FileExistsError("Provide a clean output directory")

def process_input(input_path, out_path, clips: List[str]):
  for index, clip in enumerate(clips):
    print("{0} video: {1}/{2}".format(clip, index + 1, len(clips)))
    new_clip = out_path + clip
    downsample_frames("{0}{1}".format(input_path, clip), new_clip)
    crop_center_clip = "{0}{1}-center.{2}".format(out_path, clip.split(".")[0], clip.split(".")[1])
    crop(new_clip, (500, 500), crop_center_clip)
    grayscale_clip = "{0}{1}-gray.{2}".format(out_path, clip.split(".")[0], clip.split(".")[1])
    toGrayscale(crop_center_clip, grayscale_clip)
    context_clip = "{0}{1}-context.{2}".format(out_path, clip.split(".")[0], clip.split(".")[1])
    resize(grayscale_clip, (89, 89), context_clip)
    fovea_clip = "{0}{1}-fovea.{2}".format(out_path, clip.split(".")[0], clip.split(".")[1])
    crop(grayscale_clip, (89, 89), fovea_clip)
    os.remove(new_clip)
    os.remove(crop_center_clip)
    os.remove(grayscale_clip)

os.mkdir(output_path + "/test")
process_input(input_dataset_path + "cheating/", output_path + "/test/", test_cheater_clips)
process_input(input_dataset_path + "not_cheating/very-good-players/", output_path + "/test/", test_not_cheater_clips)

print("Create test dataset with {0} clips with cheaters and {1} clips with players. Total: {2}"
      .format(
        len(test_cheater_clips),
        len(test_not_cheater_clips),
        len(test_cheater_clips) + len(test_not_cheater_clips)
      ))

os.mkdir(output_path + "/train")
process_input(input_dataset_path + "cheating/", output_path + "/train/", train_cheater_clips)
process_input(input_dataset_path + "not_cheating/very-good-players/", output_path + "/train/", train_not_cheater_clips)

print("Create train dataset with {0} clips with cheaters and {1} clips with players. Total: {2}"
      .format(
        len(train_cheater_clips),
        len(train_not_cheater_clips),
        len(train_cheater_clips) + len(train_not_cheater_clips)
      ))

# augument the dataset by flipping all data
