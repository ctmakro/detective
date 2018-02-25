import cv2
import csv

# specify path
path = './generated_images/test'

imgpath = path + '.jpg'
csvpath = path + '.csv'

# read JPEG
img = cv2.imread(imgpath)
ih,iw = img.shape[0:2]

# read CSV
# IMPORTANT: y axis coordinate is reversed, from bottom to top.
bboxcount = 0
with open(csvpath,'r') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        name,minx,miny,maxx,maxy = row
        minx,miny,maxx,maxy = \
            int(iw*float(minx)),\
            int(ih*(1-float(miny))),\
            int(iw*float(maxx)),\
            int(ih*(1-float(maxy)))
        # minx,miny,maxx,maxy = \
        #     int(float(minx)),\
        #     int((1-float(miny))),\
        #     int(float(maxx)),\
        #     int((1-float(maxy)))

        if len(name) >10 : name = name[0:10]
        # paint image with bounding boxes
        cv2.rectangle(img,
            (minx+1,miny+1),
            (maxx+1,maxy+1),
            (0,0,0),
            1, # thickness
            lineType = cv2.LINE_AA,
        )
        cv2.rectangle(img,
            (minx,miny),
            (maxx,maxy),
            (255,255,255),
            1, # thickness
            lineType = cv2.LINE_AA,
        )
        cv2.putText(img, name, (minx+1,maxy-5+1),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=.4,
            color = (0,0,0),
            thickness=1,
            lineType = cv2.LINE_AA,
        )
        cv2.putText(img, name, (minx,maxy-5),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=.4,
            color = (255,255,255),
            thickness=1,
            lineType = cv2.LINE_AA,
        )
        bboxcount+=1

print('bbox:',bboxcount)

# display
cv2.imshow(imgpath,img)
cv2.waitKey(0)

# save
cv2.imwrite(path+'_bbox.jpg', img)
