import os
from PIL import Image

def resize_tmb_img(img_name,img_src_path,img_dst_path,out_size):
    im = Image.open(os.path.join(img_src_path,img_name))
    out_size = (out_size,out_size)
    im.thumbnail(out_size)
    img_size = im.size

    new_im = Image.new('RGB',out_size,im.getpixel((1,1)))
    
    if img_size[0] > img_size [1]:
        new_im.paste(im,box=(0,round((out_size[1]-img_size[1])/2)))
    else: 
        new_im.paste(im,box=(round((out_size[0]-img_size[0])/2),0))
    
    #new_im.show()
    new_im.save(os.path.join(img_dst_path,img_name), "JPEG")
    
inputpath = os.path.join(os.getcwd(),"original_img")
outputpath = os.path.join(os.getcwd(),"output_img")


for dirpath, dirnames, filenames in os.walk(inputpath):
    structure = os.path.join(outputpath, os.path.relpath(dirpath, inputpath))
    #print(os.path.isdir(structure))
    if not os.path.isdir(structure):
        os.mkdir(structure)
        print('Processing ' + dirpath)
    else:
        print(dirpath + " Folder does already exits!")
    for file in filenames:
        #print('in dir ' + os.path.relpath(dirpath, inputpath) + " there are file " + file)
        if file.endswith('.jpg'):
            resize_tmb_img(file,dirpath,structure,1200)
print('DONE!')
