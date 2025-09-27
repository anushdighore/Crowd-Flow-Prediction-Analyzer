# main.py
import cv2
from models.vmamba_tmtb import load_tmtb_model
from utils.preprocess import preprocess_frame
from utils.postprocess import get_count_from_density
from config.settings import FRAME_SIZE, DEVICE

def run_inference(video_source=0):
    model = load_tmtb_model("checkpoints/jhu_5.pth").to(DEVICE)
    model.eval()

    cap = cv2.VideoCapture(video_source)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"▶️  Video FPS: {fps:.1f} | Press 'q' to quit")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess frame → model input
        input_tensor = preprocess_frame(frame, target_size=FRAME_SIZE).to(DEVICE)

        # Inference
        with torch.no_grad():
            density_map = model(input_tensor.unsqueeze(0))  # Shape: [1, 1, H, W]

        # Post-process → count
        count = get_count_from_density(density_map.squeeze().cpu().numpy())
        print(f"👥 Crowd Count: {int(count)}")

        # Optional: Display frame with count
        cv2.putText(frame, f"Count: {int(count)}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Crowd Counter", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import torch
    run_inference(0)  # Webcam. Use "path/to/video.mp4" for file.