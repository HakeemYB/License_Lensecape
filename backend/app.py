import cv2
import os
import datetime
import supervision as sv
import openpyxl
from capture import parse_arguments, start_capture
from object_detection import initialize_yolo_model, perform_object_detection, annotate_frame
from ocr import initialize_computer_vision_client, perform_ocr, save_cropped_image
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Use XCB (X11) platform plugin

# Replace these with your Azure Cognitive Services credentials
subscription_key = '19acc7b9d3ce44cfa252aceda64a0936'
endpoint = 'https://seecs23fyp.cognitiveservices.azure.com/'

def save_log(log_data, sheet):
    timestamp, plate_number, class_id, confidence = log_data

    plate_number = ''.join(char for char in plate_number if char.isprintable())

    sheet.append([timestamp, plate_number, class_id, confidence])

def main():
    args = parse_arguments()
    cap1 = start_capture(args.webcam_resolution, camera_id=0)

    model = initialize_yolo_model("/home/hakym/fyp_nust/model/best .pt")

    computervision_client = initialize_computer_vision_client(subscription_key, endpoint)

    save_folder = 'cropped_images'
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    detected_plates = {}

    try:
        workbook = openpyxl.load_workbook('vehicle_logs.xlsx')
        sheet = workbook.active
    except FileNotFoundError:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["Timestamp", "Plate Number", "Class ID", "Confidence"])

    while True:
        ret, frame = cap1.read()

        result = perform_object_detection(model, frame)
        detections = sv.Detections.from_ultralytics(result)

        labels = []
        for confidence, class_id in zip(detections.confidence, detections.class_id):
            if class_id is not None:
                label = f"{model.model.names[class_id]} {confidence:0.2f}"
                if confidence > 0.7:
                    plate_image = frame[int(detections.xyxy[0][1]):int(detections.xyxy[0][3]),
                                       int(detections.xyxy[0][0]):int(detections.xyxy[0][2])]

                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    image_name = save_cropped_image(plate_image, save_folder, timestamp)

                    recognized_text = perform_ocr(computervision_client, image_name)

                    if recognized_text:
                        label += f" Plate: {recognized_text}"

                        if recognized_text not in detected_plates:
                            image_name = save_cropped_image(plate_image, save_folder, recognized_text)
                            detected_plates[recognized_text] = True

                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_data = [timestamp, recognized_text, model.model.names[class_id], confidence]
                        save_log(log_data, sheet)
                labels.append(label)
            else:
                label = "Unknown"
                labels.append(label)

        frame = annotate_frame(frame, detections, labels)
        cv2.imshow("/home/hakym/fyp_nust/model/best .pt", frame)

        if cv2.waitKey(30) == 27:
            break

    cv2.destroyAllWindows()
    workbook.save('vehicle_logs.xlsx')

if __name__ == "__main__":
    main()
