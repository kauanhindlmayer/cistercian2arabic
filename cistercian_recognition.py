import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def preprocess_image(image):
    """
    Preprocess the image for better feature extraction.
    
    Args:
        image: Input image (color or grayscale)
        
    Returns:
        Preprocessed binary image
    """
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = cv2.resize(image, (300, 400))

    logger.debug(f"Resized image shape: {image.shape}")

    normalized = cv2.normalize(image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    blurred = cv2.GaussianBlur(normalized, (5, 5), 0)

    _, binary_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    binary_adaptive = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )

    binary = cv2.bitwise_or(binary_otsu, binary_adaptive)
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    binary = cv2.dilate(binary, kernel, iterations=1)

    non_zero = np.count_nonzero(binary)
    total_pixels = binary.shape[0] * binary.shape[1]
    logger.debug(f"Binary image has {non_zero} non-zero pixels out of {total_pixels} ({non_zero/total_pixels:.2%})")

    return binary

def find_stem_and_quadrants(binary_image):
    """
    Find the main vertical stem of the Cistercian numeral and divide into quadrants.
    
    Args:
        binary_image: Preprocessed binary image
        
    Returns:
        Dictionary with stem coordinates and quadrant boundaries
    """
    height, width = binary_image.shape
    logger.debug(f"Image dimensions: {width}x{height}")

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours or len(contours) == 0:
        logger.warning("No contours found in the image, using default quadrants")
        x, y = 0, 0
        w, h = width, height
    else:
        logger.debug(f"Found {len(contours)} contours")
        all_points = np.concatenate([cnt for cnt in contours])
        x, y, w, h = cv2.boundingRect(all_points)
        logger.debug(f"Bounding rectangle: x={x}, y={y}, width={w}, height={h}")
        if w < 20 or h < 20:
            logger.warning(f"Contour too small (w={w}, h={h}), using default quadrants")
            x, y = 0, 0
            w, h = width, height

    center_x = x + w // 2
    center_y = y + h // 2
    logger.debug(f"Center point: ({center_x}, {center_y})")

    stem_x = center_x
    stem_top = y
    stem_bottom = y + h

    quadrants = {
        'top-left': (int(x), int(y), int(stem_x), int(center_y)),
        'top-right': (int(stem_x), int(y), int(x + w), int(center_y)),
        'bottom-left': (int(x), int(center_y), int(stem_x), int(y + h)),
        'bottom-right': (int(stem_x), int(center_y), int(x + w), int(y + h))
    }

    for name, coords in quadrants.items():
        logger.debug(f"Quadrant {name}: {coords}")

    visual_debug = cv2.cvtColor(binary_image.copy(), cv2.COLOR_GRAY2BGR)
    cv2.line(visual_debug, (stem_x, stem_top), (stem_x, stem_bottom), (0, 255, 0), 2)
    cv2.line(visual_debug, (x, center_y), (x + w, center_y), (0, 255, 0), 2)

    return {
        'stem': (stem_x, stem_top, stem_x, stem_bottom),
        'quadrants': quadrants
    }

def detect_features_in_quadrant(binary_image, quadrant_coords):
    """
    Detect features in a specific quadrant to determine the digit.
    
    Args:
        binary_image: Preprocessed binary image
        quadrant_coords: (x1, y1, x2, y2) coordinates of the quadrant
        
    Returns:
        Estimated digit for the quadrant
    """
    x1, y1, x2, y2 = map(int, quadrant_coords)

    height, width = binary_image.shape
    x1 = max(0, min(x1, width-1))
    x2 = max(0, min(x2, width))
    y1 = max(0, min(y1, height-1))
    y2 = max(0, min(y2, height))

    if x2 <= x1 or y2 <= y1:
        return 0

    quadrant_img = binary_image[y1:y2, x1:x2]

    if np.sum(quadrant_img) < 100:
        return 0

    contours, _ = cv2.findContours(quadrant_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return 0

    num_contours = len(contours)
    horizontal_lines = 0
    vertical_lines = 0
    diagonal_lines = 0
    rectangles = 0

    q_height, q_width = quadrant_img.shape
    quadrant_area = q_height * q_width
    filled_area = np.sum(quadrant_img > 0)
    fill_ratio = filled_area / quadrant_area if quadrant_area > 0 else 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        area = cv2.contourArea(contour)

        if aspect_ratio > 2.5:
            horizontal_lines += 1
        elif aspect_ratio < 0.4:
            vertical_lines += 1
        elif 0.8 < aspect_ratio < 1.2 and area > 0.1 * quadrant_area:
            rectangles += 1

        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 2:
            pt1, pt2 = approx[0][0], approx[1][0]
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]

            if dx == 0:
                continue

            angle = abs(np.arctan2(dy, dx) * 180 / np.pi)
            if 30 < angle < 60 or 120 < angle < 150:
                diagonal_lines += 1

    logger.debug(f"Quadrant features: horiz={horizontal_lines}, vert={vertical_lines}, diag={diagonal_lines}, rect={rectangles}, contours={num_contours}, fill_ratio={fill_ratio:.2f}")

    quadrant_name = "unknown"
    logger.debug(f"Processing quadrant: {quadrant_name}")

    if fill_ratio < 0.02 or num_contours == 0:
        logger.debug(f"Quadrant {quadrant_name} is mostly empty, returning 0")
        return 0

    if horizontal_lines >= 1 and vertical_lines == 0 and diagonal_lines == 0 and num_contours <= 2:
        logger.debug(f"Detected digit 1 in {quadrant_name}")
        return 1
    if horizontal_lines >= 1 and vertical_lines >= 1 and fill_ratio < 0.2:
        logger.debug(f"Detected digit 2 in {quadrant_name}")
        return 2
    if diagonal_lines >= 1 and horizontal_lines == 0 and vertical_lines == 0:
        logger.debug(f"Detected digit 3 in {quadrant_name}")
        return 3
    if diagonal_lines >= 1 and horizontal_lines >= 1:
        logger.debug(f"Detected digit 4 in {quadrant_name}")
        return 4
    if horizontal_lines >= 1 and vertical_lines >= 1 and fill_ratio > 0.15:
        logger.debug(f"Detected digit 5 in {quadrant_name}")
        return 5
    if vertical_lines >= 1 and horizontal_lines == 0 and diagonal_lines == 0:
        logger.debug(f"Detected digit 6 in {quadrant_name}")
        return 6
    if vertical_lines >= 1 and horizontal_lines >= 1 and num_contours <= 3:
        logger.debug(f"Detected digit 7 in {quadrant_name}")
        return 7
    if horizontal_lines >= 1 and vertical_lines >= 1 and num_contours >= 2:
        logger.debug(f"Detected digit 8 in {quadrant_name}")
        return 8
    if rectangles >= 1 or (fill_ratio > 0.25 and num_contours >= 3):
        logger.debug(f"Detected digit 9 in {quadrant_name}")
        return 9

    if vertical_lines >= 1:
        return 1
    elif diagonal_lines >= 1:
        return 2
    elif horizontal_lines >= 1:
        return 1
    elif fill_ratio > 0.1:
        return 5
    if np.sum(quadrant_img) > 0:
        logger.debug(f"Fallback: Detected digit 1 in {quadrant_name}")
        return 1

    logger.debug(f"No digit detected in {quadrant_name}")
    return 0

def get_segment_positions(binary_image, quadrant_coords, digit):
    """
    Extract positions of segments that make up a digit.

    Args:
        binary_image: Preprocessed binary image
        quadrant_coords: Coordinates of the quadrant
        digit: The recognized digit

    Returns:
        List of segment positions (coordinates)
    """
    if digit == 0:
        return []

    x1, y1, x2, y2 = map(int, quadrant_coords)
    height, width = binary_image.shape
    x1 = max(0, min(x1, width-1))
    x2 = max(0, min(x2, width))
    y1 = max(0, min(y1, height-1))
    y2 = max(0, min(y2, height))

    if x2 <= x1 or y2 <= y1:
        return []

    quadrant_img = binary_image[y1:y2, x1:x2]
    contours, _ = cv2.findContours(quadrant_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return []

    segments = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"]) + x1
            cy = int(M["m01"] / M["m00"]) + y1
            x, y, w, h = cv2.boundingRect(contour)
            x += x1
            y += y1
            segments.append({
                "center": (cx, cy),
                "bbox": (x, y, w, h),
                "area": cv2.contourArea(contour)
            })

    segments.sort(key=lambda s: s["area"], reverse=True)
    return segments[:3]

def recognize_cistercian_numeral(image):
    """
    Recognize a Cistercian numeral in the image and return the corresponding number with metadata.

    Args:
        image: Input image containing a Cistercian numeral

    Returns:
        Dictionary containing:
        - number: Recognized number (0-9999)
        - segments: Detected segment positions for each digit
    """
    try:
        binary_image = preprocess_image(image)
        structure = find_stem_and_quadrants(binary_image)

        if not structure:
            logger.warning("Could not identify structure in the image")
            return {
                "number": 0,
                "confidence": {"units": 0.0, "tens": 0.0, "hundreds": 0.0, "thousands": 0.0},
                "segments": {"units": [], "tens": [], "hundreds": [], "thousands": []}
            }

        quadrants = structure['quadrants']
        logger.debug(f"Quadrant coordinates: {quadrants}")

        units_digit = detect_features_in_quadrant(binary_image, quadrants['top-right'])
        tens_digit = detect_features_in_quadrant(binary_image, quadrants['top-left'])
        hundreds_digit = detect_features_in_quadrant(binary_image, quadrants['bottom-right'])
        thousands_digit = detect_features_in_quadrant(binary_image, quadrants['bottom-left'])

        logger.debug(f"Detected digits: units={units_digit}, tens={tens_digit}, hundreds={hundreds_digit}, thousands={thousands_digit}")

        segments = {
            "units": get_segment_positions(binary_image, quadrants['top-right'], units_digit),
            "tens": get_segment_positions(binary_image, quadrants['top-left'], tens_digit),
            "hundreds": get_segment_positions(binary_image, quadrants['bottom-right'], hundreds_digit),
            "thousands": get_segment_positions(binary_image, quadrants['bottom-left'], thousands_digit)
        }

        stem = structure['stem']
        segments["stem"] = [(stem[0], stem[1]), (stem[2], stem[3])]

        number = (
            thousands_digit * 1000 +
            hundreds_digit * 100 +
            tens_digit * 10 +
            units_digit
        )

        return {
            "number": number,
            "segments": segments
        }

    except Exception as e:
        logger.error(f"Error in Cistercian numeral recognition: {str(e)}")
        return {
            "number": 0,
            "segments": {"units": [], "tens": [], "hundreds": [], "thousands": []}
        }