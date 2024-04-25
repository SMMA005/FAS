import os
import cv2
import face_recognition
import pickle


def generatePath():
    imgModeList = []
    studentIds = []
    folderPath = 'C:/xampp/htdocs/AI FACE/attendanceAppFlask/attendanceAppFlask/app/static/img/Users'
    Pathlist = os.listdir(folderPath)


    for path in Pathlist:
        imgModeList.append(cv2.imread(os.path.join(folderPath, path)))
        studentIds.append(os.path.splitext(path)[0])
        fileName = f'{folderPath}/{path}'
        print(fileName)
        print(studentIds)
    return imgModeList, studentIds


def findEncodings(imgList):
    encodeList = []
    for img in imgList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # It's a good practice to check if any faces are found before accessing the list
        encodes = face_recognition.face_encodings(img)
        if encodes:
            encode = encodes[0]
            encodeList.append(encode)
        else:
            # Handle the case where no faces are detected
            print("No faces found in the image.")
    return encodeList


def main_encoding():
    imgModeList, studentIds = generatePath()
    print("Generating Encoding")
    encodeKnownList = findEncodings(imgModeList)
    if not encodeKnownList:  # Checks if the list is empty
        print("No encodings generated. Exiting.")
        return  # Exit the function if no encodings were generated
    encodeListKnowsWithIds = [encodeKnownList, studentIds]
    print(encodeListKnowsWithIds)
    print("Done Generating Encoding")
    
    # Get the current directory
    current_dir = os.getcwd()
    
    # Construct the path to the file
    encoding_file_path = os.path.join(current_dir, "encodings.pickle")
    
    # Open the file for writing
    with open(encoding_file_path, "wb") as file:
        # Dump the encodings to the file
        pickle.dump(encodeListKnowsWithIds, file)
    
    print(f"Encodings saved to: {encoding_file_path}")
    
main_encoding()
