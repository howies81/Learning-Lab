import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
from pyzbar.pyzbar import decode

class BarcodeProcessor(VideoProcessorBase):
    def __init__(self):
        self.found_barcode = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        barcodes = decode(img)

        for barcode in barcodes:
            self.found_barcode = barcode.data.decode("utf-8")
            #print(f"!!! ENGINE FOUND BARCODE: {self.found_barcode} !!!")
            # Draw visual feedback
            (x, y, w, h) = barcode.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return frame.from_ndarray(img, format="bgr24")

def run_barcode_scanner(key="scanner"):
    """
    This function can be called from ANY other file.
    It returns the barcode string if found, otherwise None.
    """
    ctx = webrtc_streamer(
        key=key,
        video_processor_factory=BarcodeProcessor,
        # THIS SECTION BELOW CONTROLS THE CAMERA
        media_stream_constraints={
            "video": {
                "facingMode": "environment", # Tells phones to use the BACK camera
                "width": {"ideal": 640},     # Keeps the "spreadsheet" size manageable
                "height": {"ideal": 480}
            },
            "audio": False # We don't need audio for barcodes
        },
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    if ctx:
        return ctx
    return None

def get_barcode_from_scanner():
    """
    Triggers the scanner and attempts to capture a barcode.
    Returns the barcode string if found, otherwise None.
    """
    # 1. Call the engine
    barcode_result = run_barcode_scanner()

    # 2. Extract the data if the engine is 'live'
    if barcode_result and barcode_result.video_processor:
        barcode_found = barcode_result.video_processor.found_barcode
        if barcode_found:
            return barcode_found
            
    return None