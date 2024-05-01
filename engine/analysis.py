import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse

def process_frame(frame, max_gray, min_gray):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    filtered_gray = gray[np.logical_and((gray < int(max_gray)), (gray > int(min_gray)))]
    binary_threshold = np.min(filtered_gray) * 1 + np.median(filtered_gray) * 0.1
    _, thresh = cv2.threshold(gray, int(binary_threshold), 255, cv2.THRESH_BINARY)
    return thresh

def calculate_average_centroid(contours):
    centroids = []
    for c in contours:
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroids.append((cx, cy))
    if centroids:
        avg_x = sum([c[0] for c in centroids]) / len(centroids)
        avg_y = sum([c[1] for c in centroids]) / len(centroids)
        return (avg_x, avg_y)
    else:
        return None
    
def process_half(frame, side, centroids_x, centroids_y, min_contour_area, max_contour_area, max_gray, min_gray):
    processed_frame = process_frame(frame, max_gray, min_gray)
    blur = cv2.GaussianBlur(processed_frame, (5, 5), 0)
    ret, thresh_img = cv2.threshold(blur, 91, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = [c for c in contours if min_contour_area < cv2.contourArea(c) < max_contour_area]
    avg_centroid = calculate_average_centroid(filtered_contours)
    if avg_centroid:
        centroids_x.append(avg_centroid[0])
        centroids_y.append(avg_centroid[1])
    for c in filtered_contours:
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 3)
    
def process_video_with_contours(
        input_video_path,
        output_video_path,
        left_tolerance,
        right_tolerance,
        eye_height_min,
        eye_height_max,
        min_contour_area,
        max_contour_area,
        max_gray,
        min_gray
    ):
    left_centroids_x, left_centroids_y = [], []
    right_centroids_x, right_centroids_y = [], []
    time_steps = []

    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Error: Could not open video")
        return
    
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        time_steps.append(frame_count)
        frame_count += 1
        print(f"Processing frame {frame_count}")

        height, width = frame.shape[:2]
        start_row, end_row = int(height * eye_height_min), int(height * eye_height_max) 
        cropped_frame = frame[start_row:end_row, :]
        cropped_height, cropped_width = cropped_frame.shape[:2]
        left_half = cropped_frame[:, int(cropped_width * left_tolerance):int(cropped_width * 0.50)]
        right_half = cropped_frame[:, int(cropped_width * 0.50):int(cropped_width * right_tolerance)]

        process_half(left_half, "Left", left_centroids_x, left_centroids_y, min_contour_area, max_contour_area, max_gray, min_gray)
        process_half(right_half, "Right", right_centroids_x, right_centroids_y, min_contour_area, max_contour_area, max_gray, min_gray)

        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()

    plt.figure(figsize=(10, 5))
    time_left = np.arange(1, len(left_centroids_x) + 1)
    time_right = np.arange(1, len(right_centroids_x) + 1)

    def high_pass_filter(data, cutoff_frequency, fs):
        from scipy.signal import butter, filtfilt
        
        nyq = 0.5 * fs
        normal_cutoff = cutoff_frequency / nyq
        
        b, a = butter(1, normal_cutoff, btype='high', analog=False)
        filtered_data = filtfilt(b, a, data)
        
        return filtered_data

    def low_pass_filter(data, cutoff_frequency, fs):
        from scipy.signal import butter, filtfilt
        
        nyq = 0.5 * fs
        normal_cutoff = cutoff_frequency / nyq
        
        b, a = butter(1, normal_cutoff, btype='low', analog=False)
        filtered_data = filtfilt(b, a, data)
        
        return filtered_data
    
    fs = fps
    print(fps)
    
    low_cutoff_frequency = fs * 0.05
    high_cutoff_frequency = 1
    

    highpassed_left_centroids_x = high_pass_filter(left_centroids_x, high_cutoff_frequency, fs)
    highpassed_right_centroids_x = high_pass_filter(right_centroids_x, high_cutoff_frequency, fs)
    
    time_left = time_left/fps
    time_right = time_right/fps
    
    
    print(highpassed_left_centroids_x[1000:1100])
    print(highpassed_left_centroids_x.shape)
    rms_left = np.sqrt(np.mean(highpassed_left_centroids_x[int(fps*5):]**2))
    rms_right = np.sqrt(np.mean(highpassed_right_centroids_x[int(fps*5):]**2))
    
    rms = np.array([rms_left, rms_right])
    np.save("../rms.npy", rms)
    
    plt.subplot(211)
    plt.plot(time_left, left_centroids_x, c='red', label='Left Half Centroids')
    plt.plot(time_right, right_centroids_x, c='blue', label='Right Half Centroids')
    plt.title("Centroids Movement Over Time")
    plt.ylabel("X Coordinate")
    plt.legend()
    
    plt.subplot(212)
    plt.plot(time_left, highpassed_left_centroids_x, c='red', label='Highpassed Left Half Centroids')
    plt.plot(time_right, highpassed_right_centroids_x, c='blue', label='Highpassed Right Half Centroids')
    plt.xlabel("Time (s)")
    plt.ylim(-100, 100)
    plt.legend()
    
    
    
    print(rms_left)
    print(rms_right)
    
    
    
    plt.tight_layout()

    plt.savefig("../output_graphs/test.png")



    print("Processing complete. Output saved")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-iv', '--input_video_path', type=str, required=True, help="input video path")
    parser.add_argument('-ov', '--output_video_path', type=str, required=True, help="output video path")
    parser.add_argument('-lt', '--left_tolerance', type=float, default=0.1, help="left half tolerance")
    parser.add_argument('-rt', '--right_tolerance', type=float, default=1.0, help="right half tolerance")
    parser.add_argument('-ehmin', '--eye_height_min', type=float, default=0.15, help="minimum eye height")
    parser.add_argument('-ehmax', '--eye_height_max', type=float, default=0.5, help="maximum eye height")
    parser.add_argument('-mca', '--min_contour_area', type=float, default=5, help="minimum contour area")
    parser.add_argument('-Mca', '--max_contour_area', type=float, default=2000, help="maximum contour area")
    parser.add_argument('-mg', '--max_gray', type=float, default=190, help="maximum gray value for thresholding")
    parser.add_argument('-ming', '--min_gray', type=float, default=40, help="minimum gray value for thresholding")
    
    args = parser.parse_args()

    process_video_with_contours(
        args.input_video_path,
        args.output_video_path,
        args.left_tolerance,
        args.right_tolerance,
        args.eye_height_min,
        args.eye_height_max,
        args.min_contour_area,
        args.max_contour_area,
        args.max_gray,
        args.min_gray
    )

if __name__ == "__main__":
    main()