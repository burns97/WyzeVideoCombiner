import getopt
import glob
import sys
import os
import subprocess
import shutil


def main(argv):
    del_source = False
    input_directory = ''
    output_directory = ''

    try:
        opts, args = getopt.getopt(argv, "hdi:o:", ["delSrc", "inputDir=", "outputDir="])
    except getopt.GetoptError:
        print 'WyzeVideoCombiner.py -d -i <inputDir> -o <outputDir>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'WyzeVideoCombiner.py -d -i <inputDir> -o <outputDir>'
            sys.exit()
        elif opt in ("-d", "--delSrc"):
            del_source = True
        elif opt in ("-i", "--inputDir"):
            input_directory = arg
        elif opt in ("-o", "--outputDir"):
            output_directory = arg

    print 'Input directory:', input_directory
    print 'Output directory:', output_directory
    print 'Delete source files: ', del_source

    if not os.path.exists(input_directory):
        print "Input Directory does not exist."
        sys.exit(2)

    paths = glob.glob(input_directory + os.path.sep + "*/")
    for path in paths:
        process_hour_directory(path, del_source)

    if output_directory != "":
        if not os.path.exists(output_directory):
            print "Output Directory does not exist. Creating directory " + output_directory
            os.mkdir(output_directory)

        for video_file in glob.glob(input_directory + os.path.sep + "*.mp4"):
            file_name = os.path.basename(video_file)
            new_home = os.path.join(output_directory, file_name)
            print("Moving file " + video_file + " to new home " + new_home)
            shutil.move(video_file, new_home)


def process_hour_directory(input_directory, del_source):
    print("Processing WyzeCam video found in directory in " + input_directory)

    for root, dirs, files in os.walk(input_directory, topdown=True):
        for name in dirs:
            print("Found Hour Directory " + name)
            generate_file_list(input_directory + os.sep + name)
            run_ffmpeg(input_directory + os.sep + name, "Hour_" + name)

    generate_file_list(input_directory)
    day_video_filename = "Day_" + os.path.split(input_directory.rstrip('\\'))[1]
    run_ffmpeg(input_directory, day_video_filename)
    cleanup_temp_files(input_directory)
    if del_source:
        cleanup_source_files(input_directory)


def generate_file_list(file_directory):
    print("Finding files in hour directory " + file_directory)
    fo_file_list = open(os.path.join(file_directory, "files.txt"), "wb")
    for video_file in glob.glob(file_directory + os.path.sep + "*.mp4"):
        file_name = os.path.basename(video_file)
        if not file_name.startswith("file"):
            fo_file_list.write("file '" + file_name + "'\r\n")

    fo_file_list.close()


def run_ffmpeg(file_directory, output_name):
    print("Running ffmpeg in hour directory " + file_directory)
    print subprocess.Popen("ffmpeg -y -f concat -i files.txt -c copy ..\\" + output_name + ".mp4", shell=True,
                           stdout=subprocess.PIPE, cwd=file_directory).stdout.read()


def cleanup_temp_files(source_directory):
    print("Removing temp files from " + source_directory)
    os.remove(source_directory + os.sep + "files.txt")
    for video_file in glob.glob(source_directory + os.path.sep + "Hour*.mp4"):
        os.remove(video_file)


def cleanup_source_files(source_directory):
    print("Removing original source videos from " + source_directory)
    shutil.rmtree(source_directory)


if __name__ == "__main__":
    main(sys.argv[1:])
