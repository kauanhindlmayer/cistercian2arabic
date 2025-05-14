import cv2
import numpy as np
import base64

def decode_base64_image(base64_str):
    """Decode a base64 image string to a numpy array."""
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    
    img_data = base64.b64decode(base64_str)
    
    nparr = np.frombuffer(img_data, np.uint8)
    
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return img

def encode_image_to_base64(img):
    """Encode a numpy array image to a base64 string."""
    _, buffer = cv2.imencode('.png', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def create_blank_image(width=300, height=400):
    """Create a blank white image with given dimensions."""
    img = np.ones((height, width), np.uint8) * 255
    return img

def draw_cistercian_symbol(img, number):
    """
    Draw a Cistercian numeral on the image for the given number (0-9999).
    
    The Cistercian numeral system uses a vertical stem with different marks
    in four quadrants to represent units, tens, hundreds, and thousands.
    """
    if number < 0 or number > 9999:
        raise ValueError("Number must be between 0 and 9999")
    
    height, width = img.shape
    center_x = width // 2
    center_y = height // 2
    stem_height = int(height // 1.5)
    stem_top = int(center_y - stem_height // 2)
    stem_bottom = int(center_y + stem_height // 2)
    line_thickness = 3
    
    cv2.line(img, (center_x, stem_top), (center_x, stem_bottom), 0, line_thickness)
    
    units = number % 10
    tens = (number // 10) % 10
    hundreds = (number // 100) % 10
    thousands = (number // 1000) % 10
    
    draw_digit(img, units, center_x, stem_top, 'top-right', line_thickness)
    draw_digit(img, tens, center_x, stem_top, 'top-left', line_thickness)
    draw_digit(img, hundreds, center_x, stem_bottom, 'bottom-right', line_thickness)
    draw_digit(img, thousands, center_x, stem_bottom, 'bottom-left', line_thickness)
    
    return img

def draw_digit(img, digit, center_x, y_pos, quadrant, thickness):
    """
    Draw a digit (0-9) in the specified quadrant according to Cistercian numeral system.
    quadrant: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    """
    if digit == 0:
        return
    
    center_x = int(center_x)
    y_pos = int(y_pos)
    
    x_dir = 1 if 'right' in quadrant else -1
    y_dir = 1 if 'bottom' in quadrant else -1
    
    symbol_size = 50
    
    
    if digit == 1:
        end_x = int(center_x + x_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (end_x, y_pos), 0, thickness)
    
    elif digit == 2:
        horiz_end_x = int(center_x + x_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (horiz_end_x, y_pos), 0, thickness)

        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (horiz_end_x, y_pos), (horiz_end_x, vert_end_y), 0, thickness)
    
    elif digit == 3:
        end_x = int(center_x + x_dir * symbol_size)
        end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (end_x, end_y), 0, thickness)
    
    elif digit == 4:
        end_x = int(center_x + x_dir * symbol_size)
        end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (end_x, end_y), 0, thickness)
        cv2.line(img, (end_x, end_y), (end_x, y_pos), 0, thickness)
    
    elif digit == 5:
        end_x = int(center_x + x_dir * symbol_size)
        end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (end_x, end_y), 0, thickness)
        cv2.line(img, (end_x, end_y), (center_x, end_y), 0, thickness)
    
    elif digit == 6:
        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (center_x, vert_end_y), 0, thickness)
    
    elif digit == 7:
        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (center_x, vert_end_y), 0, thickness)
        horiz_end_x = int(center_x + x_dir * symbol_size)
        cv2.line(img, (center_x, vert_end_y), (horiz_end_x, vert_end_y), 0, thickness)
    
    elif digit == 8:
        horiz_end_x = int(center_x + x_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (horiz_end_x, y_pos), 0, thickness)
        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (horiz_end_x, y_pos), (horiz_end_x, vert_end_y), 0, thickness)
    
    elif digit == 9:
        horiz_end_x = int(center_x + x_dir * symbol_size)
        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (horiz_end_x, y_pos), 0, thickness)
        cv2.line(img, (horiz_end_x, y_pos), (horiz_end_x, vert_end_y), 0, thickness)
        cv2.line(img, (horiz_end_x, vert_end_y), (center_x, vert_end_y), 0, thickness)


def number_to_cistercian_image(number):
    """
    Convert a number to a Cistercian numeral image and return as base64.
    
    Args:
        number: Number to convert (0-9999)
        
    Returns:
        Base64 encoded image
    """
    if number < 0 or number > 9999:
        raise ValueError("Number must be between 0 and 9999")
    
    img = create_blank_image(300, 400)
    
    img = draw_cistercian_symbol(img, number)
    
    return encode_image_to_base64(img)

def number_to_cistercian_with_segments(number):
    """
    Convert a number to a Cistercian numeral image and return the image with segment positions.
    
    Args:
        number: Number to convert (0-9999)
        
    Returns:
        Dictionary containing:
        - image_data: Base64 encoded image
        - segments: Positions of segments for each digit
    """
    if number < 0 or number > 9999:
        raise ValueError("Number must be between 0 and 9999")
    
    img = create_blank_image(300, 400)
    
    height, width = img.shape
    center_x = width // 2
    
    stem_length = height // 2
    stem_top = height // 4
    stem_bottom = stem_top + stem_length
    
    line_thickness = 3
    
    cv2.line(img, (center_x, stem_top), (center_x, stem_bottom), 0, line_thickness)
    
    units = number % 10
    tens = (number // 10) % 10
    hundreds = (number // 100) % 10
    thousands = (number // 1000) % 10
    
    segments = {}
    
    segments["stem"] = [(center_x, stem_top), (center_x, stem_bottom)]
    segments["units"] = []
    segments["tens"] = []
    segments["hundreds"] = []
    segments["thousands"] = []
    
    if units > 0:
        segments["units"] = draw_digit_with_segments(img, units, center_x, stem_top, 'top-right', line_thickness)
    
    if tens > 0:
        segments["tens"] = draw_digit_with_segments(img, tens, center_x, stem_top, 'top-left', line_thickness)
    
    if hundreds > 0:
        segments["hundreds"] = draw_digit_with_segments(img, hundreds, center_x, stem_bottom, 'bottom-right', line_thickness)
    
    if thousands > 0:
        segments["thousands"] = draw_digit_with_segments(img, thousands, center_x, stem_bottom, 'bottom-left', line_thickness)
    
    return {
        "image_data": encode_image_to_base64(img),
        "segments": segments
    }

def draw_digit_with_segments(img, digit, center_x, y_pos, quadrant, thickness):
    """
    Draw a digit and return the positions of its segments.
    
    Args:
        img: Image to draw on
        digit: Digit to draw (1-9)
        center_x: X-coordinate of stem
        y_pos: Y-coordinate of starting point
        quadrant: Quadrant to draw in ('top-left', 'top-right', 'bottom-left', 'bottom-right')
        thickness: Line thickness
        
    Returns:
        List of segment positions [(x1,y1,x2,y2), ...]
    """
    if digit == 0:
        return []
    
    center_x = int(center_x)
    y_pos = int(y_pos)
    
    x_dir = 1 if 'right' in quadrant else -1
    y_dir = 1 if 'bottom' in quadrant else -1
    
    symbol_size = 50
    
    segments = []
    
    if digit == 1:
        end_x = int(center_x + x_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (end_x, y_pos), 0, thickness)
        segments.append({"type": "horizontal", "start": (center_x, y_pos), "end": (end_x, y_pos)})
    
    elif digit == 2:
        horiz_end_x = int(center_x + x_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (horiz_end_x, y_pos), 0, thickness)
        segments.append({"type": "horizontal", "start": (center_x, y_pos), "end": (horiz_end_x, y_pos)})

        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (horiz_end_x, y_pos), (horiz_end_x, vert_end_y), 0, thickness)
        segments.append({"type": "vertical", "start": (horiz_end_x, y_pos), "end": (horiz_end_x, vert_end_y)})
    
    elif digit == 3:
        end_x = int(center_x + x_dir * symbol_size)
        end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (end_x, end_y), 0, thickness)
        segments.append({"type": "diagonal", "start": (center_x, y_pos), "end": (end_x, end_y)})
    
    elif digit == 4:
        end_x = int(center_x + x_dir * symbol_size)
        end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (end_x, end_y), 0, thickness)
        segments.append({"type": "diagonal", "start": (center_x, y_pos), "end": (end_x, end_y)})
        
        cv2.line(img, (end_x, end_y), (end_x, y_pos), 0, thickness)
        segments.append({"type": "vertical", "start": (end_x, end_y), "end": (end_x, y_pos)})
    
    elif digit == 5:
        end_x = int(center_x + x_dir * symbol_size)
        end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (end_x, end_y), 0, thickness)
        segments.append({"type": "diagonal", "start": (center_x, y_pos), "end": (end_x, end_y)})
        
        cv2.line(img, (end_x, end_y), (center_x, end_y), 0, thickness)
        segments.append({"type": "horizontal", "start": (end_x, end_y), "end": (center_x, end_y)})
    
    elif digit == 6:
        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (center_x, vert_end_y), 0, thickness)
        segments.append({"type": "vertical", "start": (center_x, y_pos), "end": (center_x, vert_end_y)})
    
    elif digit == 7:
        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (center_x, vert_end_y), 0, thickness)
        segments.append({"type": "vertical", "start": (center_x, y_pos), "end": (center_x, vert_end_y)})
        
        horiz_end_x = int(center_x + x_dir * symbol_size)
        cv2.line(img, (center_x, vert_end_y), (horiz_end_x, vert_end_y), 0, thickness)
        segments.append({"type": "horizontal", "start": (center_x, vert_end_y), "end": (horiz_end_x, vert_end_y)})
    
    elif digit == 8:
        horiz_end_x = int(center_x + x_dir * symbol_size)
        cv2.line(img, (center_x, y_pos), (horiz_end_x, y_pos), 0, thickness)
        segments.append({"type": "horizontal", "start": (center_x, y_pos), "end": (horiz_end_x, y_pos)})
        
        vert_end_y = int(y_pos - y_dir * symbol_size)
        cv2.line(img, (horiz_end_x, y_pos), (horiz_end_x, vert_end_y), 0, thickness)
        segments.append({"type": "vertical", "start": (horiz_end_x, y_pos), "end": (horiz_end_x, vert_end_y)})

    elif digit == 9:
        horiz_end_x = int(center_x + x_dir * symbol_size)
        vert_end_y = int(y_pos - y_dir * symbol_size)

        cv2.line(img, (center_x, y_pos), (horiz_end_x, y_pos), 0, thickness)
        segments.append({"type": "horizontal", "start": (center_x, y_pos), "end": (horiz_end_x, y_pos)})
        
        cv2.line(img, (horiz_end_x, y_pos), (horiz_end_x, vert_end_y), 0, thickness)
        segments.append({"type": "vertical", "start": (horiz_end_x, y_pos), "end": (horiz_end_x, vert_end_y)})
        
        cv2.line(img, (horiz_end_x, vert_end_y), (center_x, vert_end_y), 0, thickness)
        segments.append({"type": "horizontal", "start": (horiz_end_x, vert_end_y), "end": (center_x, vert_end_y)})
    
    return segments