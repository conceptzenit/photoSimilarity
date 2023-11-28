from PIL import Image
import os
import numpy as np
import requests
import cv2
from io import BytesIO

#dhash
def dHash(img):
    # Difference Hash(dHash)
    # Scaling down to 8*8
    img = cv2.resize(img, (9, 8))
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    # The previous pixel of each row is greater than the next pixel, which is 1, and the opposite is 0, generating a hash
    for i in range(8):
        for j in range(8):
            if gray[i, j] > gray[i, j+1]:
                hash_str = hash_str+'1'
            else:
                hash_str = hash_str+'0'
    return hash_str

def cmpHash(hash1, hash2):
    # Hash value comparison
    # The sequential combination of 1 and 0 in the algorithm is the fingerprint hash of the picture. The order is not fixed, but must be the same order when comparing.
    # Comparing the fingerprints of the two pictures, calculate the Hamming distance, that is, how much the two 64-bit hash values are different. The smaller the number of different bits, the more similar the pictures
    # Hamming distance: The steps required for one set of binary data to become another set of data can measure the difference between the two images. The smaller the Hamming distance, the higher the similarity. The Hamming distance is 0, that is, the two pictures are exactly the same
    n = 0
    # If the hash length is different, -1 is returned to indicate an error in parameter passing
    if len(hash1) != len(hash2):
        return -1
    # Traverse judgment
    for i in range(len(hash1)):
        # If they are not equal, n counts + 1, and n is finally the similarity
        if hash1[i] != hash2[i]:
            n = n + 1
    return n

def getImageByUrl(url):
    try:
        response = requests.get(url, verify=False)  # Add verify=False to ignore SSL warnings
        response.raise_for_status()

        # Use BytesIO to read the image data
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        print(f"Error fetching image from {url}: {e}")
        return None

def runAllImageSimilaryFun(para1, para2):
    img1 = getImageByUrl(para1)
    img2 = getImageByUrl(para2)

    if img1 is not None and img2 is not None:
        # Convert images to NumPy arrays
        img1 = cv2.cvtColor(np.asarray(img1), cv2.COLOR_RGB2BGR)
        img2 = cv2.cvtColor(np.asarray(img2), cv2.COLOR_RGB2BGR)

        hash1 = dHash(img1)
        hash2 = dHash(img2)

        dist = cmpHash(hash1, hash2)
        return dist
    else:
        print("Error fetching images.")
        return None

#计算汉明距离
def Hamming_distance(hash1,hash2): 
    num = 0
    for index in range(len(hash1)): 
        if hash1[index] != hash2[index]: 
            num += 1
    return num

# production api
# getAllListingWithPicturesUrl = 'https://api.hauslifenetwork.com/hb/api/allListingsWithPictures'
# headers = { 'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTg1MiwiZmlyc3RuYW1lIjoiV2VuIiwibGFzdG5hbWUiOiJMdSIsImVtYWlsIjoid2VuLmx1QGhhdXN2YWxldC5jYSIsInJvbGUiOjIsImJyb2tlcl9pZCI6bnVsbCwiaWF0IjoxNzAxMTQxODU0LCJleHAiOjI3Mzc5NDE4NTR9.5XESx7Z-yb1Bh4fLaqD_h3ul0QfBQADmqaDNajjFNws' }

# local api
getAllListingWithPicturesUrl = 'http://localhost:3001/hb/api/allListingsWithPictures'
headers = { 'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTAyNiwiZmlyc3RuYW1lIjoiRmVsaXgiLCJsYXN0bmFtZSI6IkR1Z2FsLVRyZW1ibGF5IiwiZW1haWwiOiJmZWxpeC5kdEBoYXVzdmFsZXQuY2EiLCJyb2xlIjoyLCJicm9rZXJfaWQiOjEwMjYsImlhdCI6MTY5ODA2OTAyMSwiZXhwIjoyNzM0ODY5MDIxfQ.3eHHelJ5diGkVDbx9dPgg5gCSJldkqJVqyo1o0IGctM' }

getAllListingRes = requests.get(getAllListingWithPicturesUrl, headers=headers)
matched_pictures_ids = []
if getAllListingRes.status_code == 200:
    listings = getAllListingRes.json()['listings']
    for listing in listings:
        listing_pictures = listing['pictures']
        pictures = []
        for listing_picture in listing_pictures:
            if listing_picture['raw_url'] != None and listing_picture['original_url'] != None:
                pictures.append({ 'id': listing_picture['id'], 'raw_url': listing_picture['raw_url'], 'thumbnail_url': listing_picture['original_url']})

        for picture in pictures:
            if picture['raw_url'] != None and picture['thumbnail_url'] != None:
                raw_url = picture['raw_url']
                thumbnail_url = picture['thumbnail_url']
                similarity = runAllImageSimilaryFun(raw_url, thumbnail_url)
                if (similarity != None and similarity < 20):
                    matched_pictures_ids.append(int(picture['id']))
                    print('similarity', raw_url, thumbnail_url, similarity)
# production api
# saveMatchedListingPicturesUrl = 'https://api.hauslifenetwork.com/hb/api/saveMatchedListingPictures'

# local api
saveMatchedListingPicturesUrl = 'http://localhost:3001/hb/api/saveMatchedListingPictures'
saveMatchedListingPicturesRes = requests.post(saveMatchedListingPicturesUrl, headers=headers, json={ 'picture_ids': matched_pictures_ids })
print(saveMatchedListingPicturesRes.status_code)