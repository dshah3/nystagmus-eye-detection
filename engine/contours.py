import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse

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
    
def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def process_half(frame, side, centroids_x, centroids_y):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh_img = cv2.threshold(blur, 91, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = [c for c in contours if 5 < cv2.contourArea(c) < 200]
    avg_centroid = calculate_average_centroid(filtered_contours)
    if avg_centroid:
        centroids_x.append(avg_centroid[0])
        centroids_y.append(avg_centroid[1])
    for c in filtered_contours:
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 3)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--binary_video_path', type=str, help="binary video path", default=None)
    parser.add_argument('-f', '--figure_save_path', type=str, help="figure saving path", default=None)
    args = parser.parse_args()

    left_centroids_x, left_centroids_y = [], []
    right_centroids_x, right_centroids_y = [], []
    time_steps = []

    cap = cv2.VideoCapture(args.binary_video_path)

    frame_count = 0
    while(True):
        ret, frame = cap.read()
        if not ret:
            break

        time_steps.append(frame_count)
        frame_count += 1

        height = frame.shape[0]
        cropped_frame = frame[height//2:, :]
        width = cropped_frame.shape[1]
        left_half = cropped_frame[:, :width//2]
        right_half = cropped_frame[:, width//2:]

        process_half(left_half, "Left", left_centroids_x, left_centroids_y)
        process_half(right_half, "Right", right_centroids_x, right_centroids_y)

        # Display the original frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    window_size = 5
    filtered_left_x = moving_average(left_centroids_x, window_size)
    filtered_right_x = moving_average(right_centroids_x, window_size)
    filtered_time_steps = moving_average(time_steps, window_size)

    plt.figure(figsize=(10, 5))
    time_left = np.arange(1, len(left_centroids_x) + 1)
    time_right = np.arange(1, len(right_centroids_x) + 1)

    plt.plot(time_left, left_centroids_x, c='red', label='Left Half Centroids')
    plt.plot(time_right, right_centroids_x, c='blue', label='Right Half Centroids')
    plt.title("Centroids Movement Over Time")
    plt.xlabel("Time")
    plt.ylabel("X Coordinate")
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()