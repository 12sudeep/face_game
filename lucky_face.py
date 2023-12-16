import cv2
import face_recognition
import datetime
import random
import pygame
from deepface import DeepFace

def generate_win_status(win_probability=0.3, lose_probability=0.7):
    choices = [0, 1]
    weights = [lose_probability, win_probability]
    status = random.choices(choices, weights, k=1)[0]
    if status == 1:
        return 'Congrats! You get a prize.', 'Win', 
    else:
        return "Alas! No prizes for you.", 'Loose'
    

def zooming_text_animation(frame, text, font_scale, font_thickness, text_color, background_color, zoom_duration=30):
    # Set the font and other text parameters
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i in range(zoom_duration):
        # Calculate the current font scale and text position
        current_font_scale = font_scale + (i / zoom_duration) * (2 * font_scale - font_scale)
        current_text_size, _ = cv2.getTextSize(text, font, current_font_scale, font_thickness)
        current_text_x = (frame.shape[1] - current_text_size[0]) // 2
        current_text_y = (frame.shape[0] + current_text_size[1]) // 2

        # Create a copy of the frame with the background color
        frame_with_text = frame.copy()
        frame_with_text[:] = background_color

        # Draw the text on the frame
        cv2.putText(frame_with_text, text, (int(current_text_x), int(current_text_y)), font, current_font_scale, text_color, font_thickness)

        # Display the frame with text
        cv2.imshow('Game On!', frame_with_text)
        cv2.waitKey(10)  # Adjust the delay for the desired animation speed
        if 0xFF == ord('q'):
            break

    return frame_with_text


def make_random_prompt_choice():
    
    word_descriptions = {
        'Odd': './sound_effects/boy_what_the_hell_boy.mp3',
        'Unusual': './sound_effects/disappointed.mp3',
        'Enchanting': './sound_effects/hey_jaganath.mp3',
        'Angelic': './sound_effects/kon_hai_ye_log.mp3',
        'Plain': './sound_effects/laughing.mp3',
        'Flawless': './sound_effects/omg_wow.mp3',
        'Ridiculous': './sound_effects/stop_it_get_some_help.mp3',
        'Repulsive': './sound_effects/ughh_eww.mp3',
        'Sus': './sound_effects/what_the_hell.mp3',
        'Stunning': './sound_effects/wow_beautiful.mp3',
    }

    one_liners = list(word_descriptions.keys())
    choice = random.randint(0, len(one_liners)-1)

    one_liner = one_liners[choice]
    voice = word_descriptions[one_liner]

    return one_liner, voice

def largest_face_location(face_locations: list):
    if len(face_locations) != 0:
        largest_face = max(face_locations, key=lambda face: (face[2] - face[0]) * (face[3] - face[1])) # calculates the area of bounding box and selects max one

        return largest_face
    else:
        return None  # Return None if the list is empty

def place_in_frame(location, frame, face_location, text, font_scale=0.6, font_thickness=2, color=(0, 0, 255)):
    
    (top, right, bottom, left) = face_location
    
    bbox_center_x = (left + right) // 2
    bbox_top = top
    bbox_bottom = bottom

    # Set the font and other text parameters
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = font_scale  # Use a larger font size for better visibility
    font_thickness = font_thickness  # Use a thinner font thickness for normal weight

    # Calculate the size of the text to be drawn
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)

    if location == 'top':
        text_x = bbox_center_x - (text_size[0] // 2)
        text_y = bbox_top - 10  # You can adjust the vertical offset (e.g., 10 pixels)

        # Draw the text on the frame
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, font_thickness)

        return frame
    
    elif location == 'bottom':
        text_x = bbox_center_x - (text_size[0] // 2)
        text_y = bbox_bottom + text_size[1] + 10  # You can adjust the vertical offset (e.g., 10 pixels)

        # Draw the text on the frame
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, font_thickness)

        return frame

def play_aac_file(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.delay(100)
    except pygame.error:
        print(f"Error: Unable to load or play the file {file_path}")

    pygame.mixer.quit()
    pygame.quit()
    
location, encoding, landmark, timing, countdown, is_prompt_set, validate_win_status, play_sound = None, None, None, None, None, False, None, False

video_capture = cv2.VideoCapture(0)
frame_image=cv2.imread(r"./assets/frame.jpg")

while True:
    ret, live_frame = video_capture.read()
    live_feed_height, live_feed_width, _ = live_frame.shape
    frame_height,frame_width,_ = frame_image.shape

    rgb_frame = live_frame[:,:,::-1]
    result_frame=frame_image.copy()
    x_offset = 66
    y_offset = 169

    face_locations = face_recognition.api.face_locations(rgb_frame) # For face detection

    if len(face_locations) != 0:

        if location == None:
            location = [largest_face_location(face_locations)]
            encoding = face_recognition.api.face_encodings(rgb_frame, location)[0]
            landmark = face_recognition.api.face_landmarks(rgb_frame, location)[0]
            timing = datetime.datetime.now()
            countdown = 3
            is_prompt_set = False

        else:
            face_encodings = face_recognition.api.face_encodings(rgb_frame, face_locations)
            comparison = face_recognition.api.compare_faces(face_encodings, encoding)
            if True not in comparison:
                location = [largest_face_location(face_locations)]
                encoding = face_recognition.api.face_encodings(rgb_frame, location)[0]
                landmark = face_recognition.api.face_landmarks(rgb_frame, location)[0]
                timing = datetime.datetime.now()
                countdown = 3
                is_prompt_set = False
            else:
                index = comparison.index(True)
                location = [face_locations[index]]
                encoding = face_encodings[index]
                landmark = face_recognition.api.face_landmarks(rgb_frame, location)[0]
                current_time = datetime.datetime.now()
                if (current_time - timing).total_seconds() >= 1:
                    timing = current_time

                    if isinstance(countdown, int) and countdown > 1:
                        countdown = countdown - 1
                    else:
                        if is_prompt_set == False:
                            is_prompt_set = True
                            win_status, validate_win_status = generate_win_status()
                            one_liner, voice_prompt = make_random_prompt_choice()
                            countdown = win_status

        top, right, bottom, left = location[0]
        cv2.rectangle(live_frame, (left, top), (right, bottom), (0, 255, 0), 1)  # Green color, thickness 1
        
        if isinstance(countdown, int):
            live_frame = place_in_frame(location='top', frame=live_frame, face_location=location[0], text=str(countdown), font_scale=3, font_thickness=2, color=(0, 255, 0))

        elif isinstance(countdown, str):
            
            (top,right,bottom,left) = location[0]
            cropped_frame = rgb_frame[top:bottom, left:right]
            
            live_frame = place_in_frame(location='top', frame=live_frame, face_location=location[0], text=one_liner, font_scale=1, font_thickness=2, color=(0, 255, 0))

            if validate_win_status == 'Win':
                result_frame = zooming_text_animation(result_frame, win_status, font_scale=1, font_thickness=2, text_color=(255, 255, 255),background_color=(0, 128, 0))
            elif validate_win_status == 'Loose':
                result_frame = zooming_text_animation(result_frame, win_status, font_scale=1, font_thickness=2, text_color=(255, 255, 255),background_color=(0,0,255))


            # faces = DeepFace.analyze(cropped_frame, actions=['gender', 'emotion','age'], enforce_detection=False)
            # face_data =  faces[0]
            # dominant_gender = face_data['dominant_gender']
            # dominant_emotion = face_data['dominant_emotion']
            # age = face_data['age']
            # text = f"Reaction: {dominant_emotion}, Gender: {dominant_gender}, Age_guess: {age}" # Placing text

            faces = DeepFace.analyze(cropped_frame, actions=['emotion'], enforce_detection=False)
            face_data =  faces[0]
            dominant_emotion = face_data['dominant_emotion']
            text = f"Reaction: {dominant_emotion}" # Placing text

            live_frame = place_in_frame(location='bottom', frame=live_frame, face_location=location[0], text=str(text), font_scale=1, font_thickness=2)

            if play_sound == False:
                play_aac_file(voice_prompt)
                play_sound = True

    else:
        location, encoding, landmark, timing, countdown, is_prompt_set, validate_win_status, play_sound = None, None, None, None, None, False, None, False
        
    result_frame[y_offset:y_offset+live_feed_height, x_offset:x_offset+live_feed_width] = live_frame
    cv2.imshow('Game On!', result_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()