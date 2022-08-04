import os

import PIL
from PIL import Image
from shutil import copyfile
import configparser

# pyinstaller --onefile resizer.py --distpath resizer


def prepare_for_url(text):
    text = text.lower()
    for symbol in url_replace:
        text = text.replace(symbol, "-")
    return text


def resize_tmb_img(img_name, img_src_path, img_dst_path, img_dst_name, out_size):

    try:
        im = Image.open(os.path.join(img_src_path, img_name)).convert('RGB')
    except PIL.UnidentifiedImageError:
        print('Format of', img_name, 'at', img_src_path, 'is not jpg!')
        return False

    out_size = (out_size, out_size)
    im.thumbnail(out_size)
    img_size = im.size

    new_im = Image.new('RGB', out_size, im.getpixel((1, 1)))

    if img_size[0] > img_size[1]:
        new_im.paste(im, box=(0, round((out_size[1] - img_size[1]) / 2)))
    else:
        new_im.paste(im, box=(round((out_size[0] - img_size[0]) / 2), 0))

    # new_im.show()
    # new_im.save(os.path.join(img_dst_path, img_dst_name), "JPEG")
    new_im.save(os.path.join(img_dst_path, img_dst_name), "JPEG", subsampling=0)

    return True


def do_the_job():
    errors_arr = []
    for dirpath, dirnames, filenames in os.walk(inputpath):

        if dirpath == inputpath:
            # nothing to do in root
            pass
            # print("root")
        elif "\\" in os.path.relpath(dirpath, inputpath):
            # if subdir
            print("skipping subdir " + str(os.path.relpath(dirpath, inputpath)))
        else:
            # if not subdir
            if url_flag:
                artikul = prepare_for_url(os.path.relpath(dirpath, inputpath))
            else:
                artikul = os.path.relpath(dirpath, inputpath)

            out_path = os.path.join(outputpath, artikul)

            if not os.path.isdir(out_path):
                os.mkdir(out_path)
                print('Processing ' + dirpath)
            else:
                print(dirpath + " Folder does already exits!")
                continue

            # remove everything except jpg
            for file in filenames[::-1]:
                if not file.lower().endswith('.jpg'):
                    filenames.remove(file)

            # generate thumbnails
            if tmb_flag:
                if not resize_tmb_img(filenames[0], dirpath, out_path, artikul + "_tmb" + ".jpg", tmb_size):
                    errors_arr.append((dirpath, filenames[0]))
                    continue
            # print("artikul: " + os.path.relpath(dirpath, inputpath))

            counter = 0
            out_filenames = []
            for file in filenames:
                # print('in dir ' + os.path.relpath(dirpath, inputpath) + " there are file " + file)

                counter += 1

                if rename_flag:
                    out_filename = artikul + "_" + str(counter).zfill(3) + ".jpg"
                else:
                    out_filename = file

                if url_flag:
                    out_filename = prepare_for_url(out_filename)

                out_filenames.append([out_filename, artikul])
                if resize_flag:
                    if not resize_tmb_img(file, dirpath, out_path, out_filename, resize_size):
                        errors_arr.append((dirpath, file))
                        continue
                else:
                    # print("copying" + os.path.join(dirpath, file) + " to " + os.path.join(out_path, out_filename))
                    copyfile(os.path.join(dirpath, file), os.path.join(out_path, out_filename))
            filenames_arr.append(out_filenames)
    if errors_arr:
        print('These files were not processed due to resize error:')
        print(errors_arr)

    if url_flag:
        with open("filenames.txt", 'w') as f:
            for art in filenames_arr:
                out_str = ""
                for file in art:
                    out_str += remote_filepath + file[1] + "/" + file[0] + ";"
                f.write(out_str + "\n")
    else:
        if os.path.exists("filenames.txt"):
            os.remove("filenames.txt")


if __name__ == '__main__':

    filenames_arr = []
    inputpath = os.path.join(os.getcwd(), "original_img")
    outputpath = os.path.join(os.getcwd(), "output_img")

    if not os.path.isdir(inputpath):
        os.mkdir(inputpath)

    if not os.path.isdir(outputpath):
        os.mkdir(outputpath)
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("resizer_config.ini")  # читаем конфиг

    rename_flag = config["global_settings"].getboolean("rename_flag")
    resize_flag = config["global_settings"].getboolean("resize_flag")
    resize_size = config["global_settings"].getint("resize_size")
    tmb_flag = config["global_settings"].getboolean("tmb_flag")
    tmb_size = config["global_settings"].getint("tmb_size")
    url_flag = config["global_settings"].getboolean("url_flag")
    remote_filepath = config["paths"]["loftit_path"]
    url_replace = config["global_settings"]["url_replace"]
    url_replace = url_replace.split(",")

    do_the_job()

    print('DONE!')
    input('Press Enter to exit...')
