import os
from PIL import Image
from pprint import pprint

rename_flag = True
resize_flag = False
resize_size = 1200
tmb_flag = True
tmb_size = 300


def resize_tmb_img(img_name, img_src_path, img_dst_path, img_dst_name, out_size):
    im = Image.open(os.path.join(img_src_path, img_name))
    out_size = (out_size, out_size)
    im.thumbnail(out_size)
    img_size = im.size

    new_im = Image.new('RGB', out_size, im.getpixel((1, 1)))

    if img_size[0] > img_size[1]:
        new_im.paste(im, box=(0, round((out_size[1] - img_size[1]) / 2)))
    else:
        new_im.paste(im, box=(round((out_size[0] - img_size[0]) / 2), 0))

    # new_im.show()
    new_im.save(os.path.join(img_dst_path, img_dst_name), "JPEG")


inputpath = 'C:\\Users\\krabs\\Desktop\\Matisse\\original_img'
# inputpath = os.path.join(os.getcwd(), "original_img")
outputpath = os.path.join(os.getcwd(), "output_img")
# print(inputpath)
# pprint(list(os.walk(inputpath)))

for dirpath, dirnames, filenames in os.walk(inputpath):
    out_path = os.path.join(outputpath, os.path.relpath(dirpath, inputpath))
    print(out_path)
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
        print('Processing ' + dirpath)
    else:
        print(dirpath + " Folder does already exits!")
        #True

    # print("list ")
    # path_list = list(os.path.split(dirpath))
    # print(dirpath)
    # print(list(path_list))

    if dirpath == inputpath:
        # nothing to do in root
        True
        # print("root")
    elif str(os.path.relpath(dirpath, inputpath)).find('//'):
        # if subdir
        print("skipping subdir " + os.path.relpath(dirpath, inputpath))
    else:
        # if not subdir
        artikul = os.path.relpath(dirpath, inputpath)

        if tmb_flag:
            resize_tmb_img(filenames[0], dirpath, out_path, artikul + "_tmb" + ".jpg", tmb_size)
        # print("artikul: " + os.path.relpath(dirpath, inputpath))

        counter = 1
        for file in filenames:
            # print('in dir ' + os.path.relpath(dirpath, inputpath) + " there are file " + file)
            if file.endswith('.jpg'):
                if rename_flag:
                    resize_tmb_img(file, dirpath, out_path, file, resize_size)
                    True
                else:
                    resize_tmb_img(file, dirpath, out_path, artikul + ".jpg", resize_size)
                    True



        True


            #print(dirpath)
print('DONE!')
