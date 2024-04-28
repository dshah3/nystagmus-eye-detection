import cv2
import numpy as np
import argparse

def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    filtered_gray = gray[np.logical_and((gray < 250), (gray > 10))]
    binary_threshold = np.min(filtered_gray) * 1 + np.median(filtered_gray) * 0.1
    _, thresh = cv2.threshold(gray, int(binary_threshold), 255, cv2.THRESH_BINARY)
    return thresh

def process_video(input_video_path, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height), isColor=False)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = process_frame(frame)
        out.write(processed_frame)

    cap.release()
    out.release()
    print("Processing complete. Output saved to:", output_video_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-iv', '--input_video_path', type=str, help="input video", default=None)
    parser.add_argument('-ov', '--output_video_path', type=str, help="output video", default=None)
    args = parser.parse_args()

    process_video(args.input_video_path, args.output_video_path)

if __name__ == "__main__":
    main()
    
