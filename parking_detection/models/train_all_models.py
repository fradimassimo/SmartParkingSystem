import os
import torch

from dataset import acpds
from utils.engine import train_model
from models.rcnn import RCNN


# set device
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

# load dataset
train_ds, valid_ds, test_ds = acpds.create_datasets('dataset/data')

# set dir to store model weights and logs
wd = os.path.expanduser('~/Downloads/pd-camera-weights/')

# train each model multiple times
for i in range(5):
    # RCNN
    train_model(RCNN(roi_res=64,  pooling_type='qdrl'),   train_ds, valid_ds, test_ds, f'{wd}/RCNN_64_qdrl_{i}',    device)
    train_model(RCNN(roi_res=128, pooling_type='qdrl'),   train_ds, valid_ds, test_ds, f'{wd}/RCNN_128_qdrl_{i}',   device)
    train_model(RCNN(roi_res=256, pooling_type='qdrl'),   train_ds, valid_ds, test_ds, f'{wd}/RCNN_256_qdrl_{i}',   device)
    train_model(RCNN(roi_res=64,  pooling_type='square'), train_ds, valid_ds, test_ds, f'{wd}/RCNN_64_square_{i}',  device)
    train_model(RCNN(roi_res=128, pooling_type='square'), train_ds, valid_ds, test_ds, f'{wd}/RCNN_128_square_{i}', device)
    train_model(RCNN(roi_res=256, pooling_type='square'), train_ds, valid_ds, test_ds, f'{wd}/RCNN_256_square_{i}', device)
