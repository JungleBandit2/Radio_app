import subprocess
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea,
    QFrame, QToolButton, QGridLayout, QSizePolicy, QStackedLayout,
    QLabel, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
import sys, os
import socket


# Check for internet
def check_internet_connection(host="1.1.1.1", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


ffplay_process = None


# Parse CSV file for radio stations
def parse_csv_file(csv_path):
    stations = []

    with open(csv_path, "r", encoding="windows-1252") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            name = row.get("Station", "Unknown")
            image_filename = row.get("Image", "")
            stream_url = row.get("Stream URL", "")

            if stream_url:
                stations.append({
                    "name": name,
                    "image_filename": image_filename,
                    "stream_url": stream_url
                })
            else:
                print(f"Skipping station '{name}' because stream URL is missing.")

    return stations


def stop_ffplay():
    global ffplay_process
    if ffplay_process and ffplay_process.poll() is None:
        ffplay_process.terminate()


def stop_and_return():
    stop_ffplay()
    frame_layout.setCurrentWidget(scroll_area)


# Load station image or placeholder
def load_station_pixmap(image_filename, size):
    image_path = os.path.join(script_dir, "files", "station_icons", image_filename)

    if not image_filename or not os.path.exists(image_path):
        image_path = os.path.join(script_dir, "files", "placeholder.svg")

    pixmap = QPixmap(image_path)
    return pixmap.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )


# Start the locally installed ffplay instance
def start_ffplay(station):
    global ffplay_process
    if not check_internet_connection():
        QMessageBox.critical(None, "No Internet", "You must be connected to the internet.")
        return

    station_name_label.setText(station["name"])

    # Load image or placeholder
    pixmap = load_station_pixmap(station["image_filename"], 120)
    station_icon_label.setPixmap(pixmap)

    frame_layout.setCurrentWidget(now_playing)
    stream_url = station["stream_url"]
    title = station["name"]

    ffplay_path = os.path.join(script_dir, "ffplay", "ffplay.exe")
    command = [
        ffplay_path,
        "-nodisp",
        "-autoexit",
        stream_url
    ]

    print(f"Starting ffplay for station '{title}' with URL '{stream_url}'")
    try:
        ffplay_process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )


    except Exception as e:
        print(f"Failed to launch ffplay: {e}")


# Set variables for the script
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()

icon_path = os.path.join(script_dir, "files", "icon.svg")
csv_file = os.path.join(script_dir, "files", "Radio Stations.csv")
stations = parse_csv_file(csv_file)

# Initialise Qt window
app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Radio Player")
window.resize(620, 400)
window.setStyleSheet("background-color: #3b3b3b;")
window.setWindowIcon(QIcon(icon_path))

# Initialise Qt frame
frame = QWidget()
frame.setStyleSheet("background-color: #3b3b3b;")
frame_layout = QStackedLayout()
frame_layout.setContentsMargins(0, 0, 0, 0)
frame.setLayout(frame_layout)

# Initialise Now Playing screen
now_playing = QWidget()
now_playing_layout = QVBoxLayout()
now_playing.setLayout(now_playing_layout)

# Add the station icon
station_icon_label = QLabel()
station_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Add the station label
station_name_label = QLabel()
station_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
station_name_label.setStyleSheet("""
    QLabel {
        color: #fefefe;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
""")

# Add the Stop button
stop_button = QToolButton()
stop_button.setFixedSize(120, 120)
stop_icon = QIcon(QPixmap(os.path.join(script_dir, "files", "stop.svg")))
stop_button.setIcon(stop_icon)
stop_button.setIconSize(QSize(100, 100))
stop_button.setStyleSheet("""
    QToolButton {
        background-color: #3b3b3b;
        color: #fefefe;
        padding: 10px;
        border-radius: 12px;
    }
    QToolButton:hover {
        background-color: #444;
    }
""")
stop_button.clicked.connect(lambda: stop_and_return())

# Add widgets to Now Playing screen
now_playing_layout.addWidget(station_icon_label)
now_playing_layout.addWidget(station_name_label)
now_playing_layout.addWidget(stop_button, alignment=Qt.AlignmentFlag.AlignCenter)
now_playing_layout.insertStretch(0)
now_playing_layout.addStretch()

# Initialise scrolling and scrollbar styling
scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
app.setStyle("Fusion")
scroll_area.setStyleSheet("""
    /* === VERTICAL SCROLLBAR === */
    QScrollBar:vertical {
        background: #3b3b3b;
        width: 12px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background: #888;
        min-height: 20px;
        border-radius: 6px;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::up-arrow:vertical,
    QScrollBar::down-arrow:vertical {
        height: 0;
        width: 0;
        background: none;
        border: none;
    }

    /* === HORIZONTAL SCROLLBAR === */
    QScrollBar:horizontal {
        background: #3b3b3b;
        height: 12px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background: #888;
        min-width: 20px;
        border-radius: 6px;
    }

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal,
    QScrollBar::left-arrow:horizontal,
    QScrollBar::right-arrow:horizontal {
        height: 0;
        width: 0;
        background: none;
        border: none;
    }
""")

# Set the area to scroll in
scrollable_frame = QFrame()
scrollable_frame.setStyleSheet("background-color: #3b3b3b;")
scroll_area.setWidget(scrollable_frame)
scrollable_frame.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

# Add the scroll area widget to the ui
frame_layout.addWidget(scroll_area)
frame_layout.addWidget(now_playing)

# Set grid to render buttons
button_size = 150
grid_layout = QGridLayout()
scrollable_frame.setLayout(grid_layout)

buttons = []

# Set the button icons and labels to CSV data
for i, station in enumerate(stations):
    image_filename = station.get("image_filename")

    # Check whether the image referenced in CSV file exists or whether to use placeholder
    pixmap = load_station_pixmap(image_filename, button_size)

    # Set the button icon, size and style for each station
    button = QToolButton()
    button.setIcon(QIcon(pixmap))

    icon_scale = 0.95
    icon_size = int(button_size * icon_scale)
    button.setIconSize(QSize(icon_size, icon_size))

    button.setText(station["name"])
    button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

    button.setStyleSheet("""
        QToolButton {
            background-color: #3b3b3b;
            color: #fefefe;
            padding: 10px;
            border-radius: 12px;
        }
        QToolButton:hover {
            background-color: #444;
        }
    """)
    button.setFixedSize(button_size + 20, button_size + 40)
    button.clicked.connect(lambda checked, st=station: start_ffplay(st))

    # Set button grid size
    row = i // 3
    column = i % 3
    grid_layout.addWidget(button, row, column, Qt.AlignmentFlag.AlignCenter)
    buttons.append(button)

print(buttons)

# Run the Qt window
window.setCentralWidget(frame)
window.show()
app.aboutToQuit.connect(stop_ffplay)

try:
    sys.exit(app.exec())
finally:
    stop_ffplay()
