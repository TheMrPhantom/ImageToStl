import numpy as np
from stl import mesh
import cv2
import sys
import cantor


#Load Image
imageInput=sys.argv[1]
isBending=False
if len(sys.argv)>2:
    isBending=sys.argv[2]=="yes"


def oneFile(imageInput):
    img = cv2.imread(imageInput,0)


    x = img.shape[0]
    y = img.shape[1]
    ratio=y/x

    dim = (int(300*ratio),300)

    img= cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    img=cv2.blur(img,(3,3))

    #Save sample black and white
    #cv2.imwrite("out.jpg",img)

    #Create mesh verticies
    vertices=np.zeros((img.shape[0]*img.shape[1],3))
    cantor.xElements=img.shape[0]

    maxIndex=cantor.getIndex(img.shape[0]-1,img.shape[1]-1)
    counter=0

    print("Calculating verticies...")
    for y in range(img.shape[1]):   
        for x in range(img.shape[0]):
            index=cantor.getIndex(x,y)

            bending=0
            if isBending:
                bending=-(((y/img.shape[1])-0.5)*20)**2
            
            if x == 0 or x==img.shape[0]-1 or y == 0 or y==img.shape[1]-1:
                replacement=-2+bending
                if x == 0:
                    vertices[index]=[x+1,y,replacement]
                if x==img.shape[0]-1:
                    vertices[index]=[x-1,y,replacement]
                if y == 0:
                    vertices[index]=[x,y+1,replacement]
                if y==img.shape[1]-1:
                    vertices[index]=[x,y-1,replacement]
                if x==0 and y==0:
                    vertices[index]=[x+1,y+1,replacement]
                if x==img.shape[0]-1 and y==img.shape[1]-1:
                    vertices[index]=[x-1,y-1,replacement]
            else:

                vertices[index]=[x,y,10-(img[x][y]/255)*10+bending]
            if counter>10000:
                print(int(((index/maxIndex)*100*100))/100,"%")
                counter=0
            counter+=1

    counter=0
    print()
    print("Calculating faces...")
    faces=[]
    for y in range(img.shape[1]-1):
        for x in range(img.shape[0]-1):
            faces.append([cantor.getIndex(x,y),cantor.getIndex(x+1,y),cantor.getIndex(x+1,y+1)])
            faces.append([cantor.getIndex(x,y),cantor.getIndex(x,y+1),cantor.getIndex(x+1,y+1)])

            if counter>10000:
                index=cantor.getIndex(x,y)
                print(int(((index/maxIndex)*100*100))/100,"%")
                counter=0
            counter+=1

    y=img.shape[1]-1
    for x in range(img.shape[0]-1):
        faces.append([cantor.getIndex(x,0),cantor.getIndex(x,y),cantor.getIndex(x+1,y)])
        faces.append([cantor.getIndex(x,0),cantor.getIndex(x+1,y),cantor.getIndex(x+1,0)])

    faces=np.array(faces)


    print()
    print("Creating mesh...")
    # Create the mesh
    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = vertices[f[j],:]

    cube.update_normals()
    # Write the mesh to file "cube.stl"
    cube.save(imageInput.split(".")[0]+".stl")


if "." in imageInput:
    oneFile(imageInput)
else:
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(imageInput) if isfile(join(imageInput, f))]
    for f in onlyfiles:
        oneFile(imageInput+f)