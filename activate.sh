export PYTHONPATH=$PYTHONPATH:./src

python3 src/real_time_object_detection.py --prototxt models/MobileNetSSD_deploy.prototxt.txt --model models/MobileNetSSD_deploy.caffemodel